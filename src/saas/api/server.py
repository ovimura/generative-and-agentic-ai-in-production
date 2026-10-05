import os
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials
from openai import OpenAI
import jwt as pyjwt

app = FastAPI()

# Add CORS middleware (allows frontend to call backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clerk authentication setup. Leeway covers clock drift between Windows and Docker.
clerk_config = ClerkConfig(
    jwks_url=os.getenv("CLERK_JWKS_URL"),
    verify_iat=False,
    leeway=30.0,
)
class LoggingClerkHTTPBearer(ClerkHTTPBearer):
    def _decode_token(self, token: str):
        decoded = super()._decode_token(token)
        if decoded is None:
            try:
                header = pyjwt.get_unverified_header(token)
            except Exception as error:
                header = f"{type(error).__name__}: {error}"
            try:
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                pyjwt.decode(
                    token,
                    key=signing_key.key,
                    audience=self.audience,
                    issuer=self.issuer,
                    algorithms=["RS256"],
                    options={
                        "verify_exp": self.config.verify_exp,
                        "verify_aud": self.config.verify_aud,
                        "verify_iss": self.config.verify_iss,
                        "verify_iat": self.config.verify_iat,
                    },
                    leeway=self.config.leeway,
                )
            except Exception as error:
                print(f"CLERK_DECODE_ERROR header={header} error={type(error).__name__}: {error}", flush=True)
        return decoded


clerk_guard = LoggingClerkHTTPBearer(clerk_config)

class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str

system_prompt = """
You are provided with notes written by a doctor from a patient's visit.
Your job is to summarize the visit for the doctor and provide an email.
Reply with exactly three sections with the headings:
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
"""

def user_prompt_for(visit: Visit) -> str:
    return f"""Create the summary, next steps and draft email for:
Patient Name: {visit.patient_name}
Date of Visit: {visit.date_of_visit}
Notes:
{visit.notes}"""

@app.post("/api/consultation")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    user_id = creds.decoded["sub"]
    client = OpenAI()

    user_prompt = user_prompt_for(visit)
    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=prompt,
        stream=True,
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get("/health")
def health_check():
    """Health check endpoint (used for local Docker; Lambda does not invoke it)"""
    return {"status": "healthy"}

# Serve static files (our Next.js export) - MUST BE LAST!
static_path = Path("static")
if static_path.exists():
    @app.get("/")
    async def serve_root():
        return FileResponse(static_path / "index.html")

    app.mount("/", StaticFiles(directory="static", html=True), name="static")