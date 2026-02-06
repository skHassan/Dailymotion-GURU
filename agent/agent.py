from typing import TypedDict, List

from agent.retriever import Retriever
from agent.llm import generate
from agent.prompt import (
    BASE_SYSTEM_PROMPT,
    DEVELOPER_STYLE,
    NON_DEVELOPER_STYLE,
    CLARITY_CHECK_PROMPT,
    CLARIFICATION_PROMPT
)

# --------------------
# Configuration
# --------------------

CONFIDENCE_THRESHOLD = 0.60
DOMAIN_PREFIX = "Dailymotion"


# --------------------
# Types
# --------------------

class AgentResponse(TypedDict, total=False):
    answer: str
    confidence: str  # "high" | "low" | "clarification"
    sources: List[str]
    pending_question: str


# --------------------
# Helpers
# --------------------

def normalize_question(question: str) -> str:
    """
    Ensure the retriever always operates in the Dailymotion domain.
    """
    q = question.lower()
    if "dailymotion" not in q:
        return f"{DOMAIN_PREFIX} {question}"
    return question


def assess_question_clarity(question: str) -> str:
    """
    Ask the LLM whether the question is:
    - CLEAR
    - NEEDS_CLARIFICATION
    - UNSUPPORTED
    """
    decision = generate(
        CLARITY_CHECK_PROMPT,
        question
    ).strip().upper()

    # Safety fallback
    if decision not in {"CLEAR", "NEEDS_CLARIFICATION", "UNSUPPORTED"}:
        return "CLEAR"

    return decision


def is_relevant(question: str, chunks: list[dict]) -> bool:
    """
    Lightweight relevance check to avoid clearly off-topic matches.
    """
    q_terms = set(question.lower().split())

    for c in chunks:
        text = c["text"].lower()
        overlap = sum(1 for term in q_terms if term in text)
        if overlap >= 2:
            return True

    return False


def build_context(chunks: list[dict]):
    """
    Build context text and collect source names.
    """
    context_blocks = []
    sources = []

    for c in chunks:
        context_blocks.append(
            f"[Source: {c['source']}]\n{c['text']}"
        )
        sources.append(c["source"])

    return "\n\n".join(context_blocks), sorted(set(sources))

def generate_clarification_question(question: str) -> str:
    return generate(
        CLARIFICATION_PROMPT.format(question=question),
        ""
    ).strip()


# --------------------
# Main entry point
# --------------------
retriever = Retriever()
def answer_question(question: str, mode: str = "developer") -> AgentResponse:
    # 1. Clarity assessment (LLM-driven, no heuristics)
    clarity = assess_question_clarity(question)

    print(clarity)

    if clarity == "NEEDS_CLARIFICATION":
        return {
            "answer": (
                "I can help with that, but I need a bit more information first.\n\n"
                "Could you clarify what you already have? For example:\n"
                "- a video ID\n"
                "- a video URL\n"
                "- or an embedded player\n\n"
                "Once that’s clear, I can give you the exact steps."
            ),
            "confidence": "clarification",
            "sources": [],
            "pending_question": question, 
        }

    if clarity == "UNSUPPORTED":
        return {
            "answer": (
                "This question is not clearly answered in the official "
                "Dailymotion documentation."
            ),
            "confidence": "low",
            "sources": ["Dailymotion Developer Documentation"],
        }

    # 2. Domain-normalized retrieval
    normalized_question = normalize_question(question)

    results = retriever.search(normalized_question, top_k=4)

    # 3. Confidence + relevance gating
    if not results or results[0]["score"] < CONFIDENCE_THRESHOLD or not is_relevant(question, results):
        # If the question was CLEAR but evidence is weak → clarification
        clarification = generate_clarification_question(question)
        return {
            "answer": clarification,
            "confidence": "clarification",
            "sources": [],
            "pending_question": question,
        }


    # 4. Build grounded prompt
    context, sources = build_context(results)

    style_prompt = (
        DEVELOPER_STYLE if mode == "developer"
        else NON_DEVELOPER_STYLE
    )

    system_prompt = (
        BASE_SYSTEM_PROMPT
        + "\n"
        + style_prompt
        + "\n\nDocumentation context:\n"
        + context
    )

    # 5. Generate final answer
    answer = generate(system_prompt, question)

    return {
        "answer": answer,
        "confidence": "high",
        "sources": [
            src.replace(".txt", "").replace("_", " ")
            for src in sources
        ],
    }


# if __name__ == "__main__":
#     q = "how can I get dailymotion video title?" 
#     print(answer_question(q, mode="non_developer"))