from fastapi import FastAPI
from pydantic import BaseModel
from agent.agent import answer_question
from datetime import datetime
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional


app = FastAPI(title="Dailymotion Expert Agent")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origins=["*"]
)


LOG_FILE = Path("logs/low_confidence_questions.log")

def log_low_confidence(question: str, mode: str):
    timestamp = datetime.utcnow().isoformat()
    entry = f"[{timestamp}] mode={mode} | question={question}\n"

    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


class AskRequest(BaseModel):
    question: str
    mode: str = "developer"
    pending_question: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    confidence: str
    sources: list[str]
    pending_question: Optional[str] = None
    

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    # If user is replying to a clarification
    if req.pending_question:
        combined_question = (
            f"{req.pending_question}. "
            f"Clarification from user: {req.question}"
        )
        result = answer_question(combined_question, mode=req.mode)
    else:
        result = answer_question(req.question, mode=req.mode)

    return AskResponse(
        answer=result["answer"],
        confidence=result["confidence"],
        sources=result["sources"],
        pending_question=result.get("pending_question"),
    )



