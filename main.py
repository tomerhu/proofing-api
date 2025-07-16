import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session
from fastapi.staticfiles import StaticFiles
from models import Suggestion
from pydantic import BaseModel
from typing import List

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./db/app.db"
)
engine = create_engine(DATABASE_URL, echo=True)


app = FastAPI(
    title="Proofreading API MVP",
    description="A simple service to ping and eventually proofread text.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # during development you can use ["*"]. 
    allow_credentials=True,
    allow_methods=["*"],            # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],            # allow Content-Type, Authorization, etc.
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

class ProofreadRequest(BaseModel):
    text: str

class Highlight(BaseModel):
    start: int
    end: int
    suggestion: str

class ProofreadResponse(BaseModel):
    text: str
    highlights: List[Highlight]

@app.get("/")
def root():
    return {"message": "Service is up! Try /ping or /proofread"}

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.post("/proofread")
def proofread(req: ProofreadRequest):
    text = req.text

    # Dummy suggestion
    span = {"start": 0, "end": 5}
    suggestion_text = "Dummy suggestion"

    # 4.2 – Persist into SQLite
    with Session(engine) as session:
        suggestion = Suggestion(
            input_text=text,
            span_start=span["start"],
            span_end=span["end"],
            suggestion=suggestion_text
        )
        session.add(suggestion)
        session.commit()  # writes row to suggestions.db

    # 4.3 – Return response as before
    return {
        "text": text,
        "suggestions": [
            {
                "span": span,
                "suggestion": suggestion_text
            }
        ]
    }

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")