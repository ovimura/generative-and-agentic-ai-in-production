# Alex - the Agentic Learning Equities Explainer

## Multi-agent Enterprise-Grade SaaS Financial Planner

![Course Image](assets/alex.png)

_If you're looking at this in Cursor, please right click on the filename in the Explorer on the left, and select "Open preview", to view it in formatted glory._

### Welcome to The Capstone Project for Week 3 and Week 4!

#### The directories:

1. **guides** - this is where you will live - step by step guides to deploy to production
2. **backend** - the agent code, organized into subdirectories, each a uv project (as is the backend parent directory)
3. **frontend** - a NextJS React frontend integrated with Clerk
4. **terraform** - separate terraform subdirectories with state for each part
5. **scripts** - the final deployment script, including `run_local.py`

#### Run locally

`scripts/run_local.py` starts the FastAPI API on port 8000 and the Next.js frontend on port 3000. It needs `src/alex/.env` and `frontend/.env.local`.

On Windows PowerShell, set UTF-8 before starting. The script prints emoji, and the default cp1252 console raises `UnicodeEncodeError` and exits before either server starts.

```powershell
cd src/alex/scripts
$env:PYTHONUTF8 = "1"
uv run .\run_local.py
```

On macOS or Linux:

```bash
cd src/alex/scripts
uv run run_local.py
```

Run one copy. The script waits until the process it started is listening on ports 3000 and 8000. If either port is already taken, it exits and asks you to stop the other process. Stopping the script on Windows also stops the Next.js and API child processes, so those ports are released.

#### Order of play:

##### Week 3

- On Week 3 Day 3, we will do 1_permissions and 2_sagemaker
- On Week 3 Day 4, we will do 3_ingest
- On Week 3 Day 5, we will do 4_researcher

##### Week 4

- On Week 4 Day 1, we will do 5_database
- On Week 4 Day 2, we will do 6_agents
- On Week 4 Day 3, we will do 7_frontend
- On Week 4 Day 4, we will do 8_enterprise

#### Keep in mind

- Please submit your community_contributions, including links to your repos, in the production repo community_contributions folder
- Regularly do a git pull to get the latest code
- Reach out in Udemy or email (ed@edwarddonner.com) if I can help! This is a gigantic project and I am here to help you deliver it!