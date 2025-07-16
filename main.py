import os
from fastapi import FastAPI, Request
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.ext.fastapi.fastapi_middleware import FastAPIMiddleware
from applicationinsights import TelemetryClient
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session
from fastapi.staticfiles import StaticFiles
from models import Suggestion
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./db/app.db"
)
engine = create_engine(DATABASE_URL, echo=True)

# ——— Read your App Insights connection string from .env ———
conn_str = os.getenv("APPINSIGHTS_CONNECTION_STRING")
instr_key = os.getenv("APPINSIGHTS_INSTRUMENTATION_KEY")
if instr_key:
    tc = TelemetryClient(instr_key)
else:
    tc = None

app = FastAPI(
    title="Proofreading API MVP",
    description="A powerful tool to proofread text.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # during development you can use ["*"]. 
    allow_credentials=True,
    allow_methods=["*"],            # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],            # allow Content-Type, Authorization, etc.
)

app.add_middleware(
    FastAPIMiddleware,
    exporter=AzureExporter(connection_string=conn_str),
    sampler=ProbabilitySampler(rate=1.0),
)

@app.middleware("http")
async def catch_exceptions(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception:
        # Automatically records the exception (stack trace + context)
        if tc:
            tc.track_exception()
            tc.flush()
        # Re-raise so FastAPI still returns a 500
        raise


logger = logging.getLogger("proofread-api")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
logger.addHandler(AzureLogHandler(connection_string=conn_str))


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
    suggestions: List[Highlight]

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
    
    if tc:
        tc.track_metric("proofread_calls", 1)
        tc.flush()

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

    logger.info("proofread called", extra={"text_length": len(req.text)})
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

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="static")