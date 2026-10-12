from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent, tool
from typing import List
from pydantic import BaseModel, Field
from bedrock_agentcore.tools.code_interpreter_client import CodeInterpreter
import json

code_client = CodeInterpreter("us-west-2")

@tool
def execute_python(code: str) -> str:
    """Execute Python code in the code interpreter."""
    response = code_client.invoke("executeCode", {"language": "python", "code": code})
    output = []
    for event in response["stream"]:
        if "result" in event and "content" in event["result"]:
            content = event["result"]["content"]
            output.append(content)
    return json.dumps(output[-1])


app = BedrockAgentCoreApp()


class ToDoItem(BaseModel):
    description: str = Field(..., description="The text describing the task")
    completed: bool = Field(False, description="Whether the task is complete")


todos = []

system_prompt = """
You are given a problem to solve, by using your todo tools to plan a list of steps, then carrying out each step in turn.
You also have access to an execute_python tool to run Python.
Your plan should include solving the problem without Python, then writing and executing Python code to validate your solution.
To use the execute_python tool to validate your solution, you must have a task on your todo list prefixed with "Write Python code to...".
Now use the todo list tools, create a plan, carry out the steps, and reply with the solution.

The todo tools are the only source of the checklist. Follow this sequence:
- Call create_todos once with every step before doing any work.
- Finish one step, then immediately call mark_complete with that step's position (starting at 1) before starting the next step.
- A step is complete only after mark_complete succeeds for it. Do not check off a step in your own words.
- Do not write your own todo list, checkboxes, or strike markup. Those lines come only from the tool results.
- Before the final answer, call mark_complete for every remaining step, then call list_todos.
- Reply with the solution only. Do not reprint the todo list; the latest tool list is the one that is shown.
"""

def get_todo_report() -> str:
    """Get a report of all todos."""
    result = ""
    for index, todo in enumerate(todos):
        completed = "X" if todo.completed else " "
        start = "[strike][green]" if todo.completed else ""
        end = "[/strike][/green]" if todo.completed else ""
        start += "[red]" if "python" in todo.description.lower() else ""
        end += "[/red]" if "python" in todo.description.lower() else ""
        result += f"Todo #{index + 1}: [{completed}] {start}{todo.description}{end}\n"
    return result


@tool
def create_todos(descriptions: List[str]) -> str:
    """Add new todos from a list of descriptions and return the full list"""
    for desc in descriptions:
        if desc.strip() == "":
            continue
        todos.append(ToDoItem(description=desc))
    return get_todo_report()


@tool
def mark_complete(index: int) -> str:
    """Mark complete the todo at the given position (starting from 1) and return the full list"""
    if 1 <= index <= len(todos):
        todos[index - 1].completed = True
    else:
        return "No todo at this index."
    return get_todo_report()


@tool
def list_todos() -> str:
    """Return the full list of todos with completed ones checked off"""
    return get_todo_report()


tools = [create_todos, mark_complete, list_todos, execute_python]
agent = Agent(model="us.anthropic.claude-sonnet-4-6", system_prompt=system_prompt, tools=tools)


@app.entrypoint
async def invoke(payload):
    """Our Agent function"""
    user_message = payload.get("prompt")
    stream = agent.stream_async(user_message)
    async for event in stream:
        if "data" in event:
            yield event["data"]  # Stream data chunks
        elif "message" in event:
            yield "\n" + get_todo_report()


if __name__ == "__main__":
    app.run()