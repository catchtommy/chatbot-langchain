from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from app.rag import get_vectorstore


@dataclass
class AssessmentState:
    question: str
    expected_answer: str | None


_sessions: Dict[str, AssessmentState] = {}


def _extract_expected_answer(question: str) -> str | None:
    marker = "Answer:"
    if marker not in question:
        return None
    return question.split(marker, 1)[1].strip().lower()


def wants_assessment(message: str) -> bool:
    lowered = message.lower()
    return "assessment" in lowered or "quiz" in lowered or "test me" in lowered


def pick_assessment_question(message: str) -> str:
    subject = "math" if "math" in message.lower() else "english"
    query = f"assessment question {subject}"

    docs = get_vectorstore().similarity_search(query, k=2)
    for doc in docs:
        text = doc.page_content.strip()
        if "assessment question" in text.lower() and subject in text.lower():
            return text

    if subject == "math":
        return "Assessment question math: What is 9 + 6? Answer: 15"
    return "Assessment question english: Write one sentence using the word 'because'."


def start_assessment(session_id: str, message: str) -> str:
    question = pick_assessment_question(message)
    _sessions[session_id] = AssessmentState(
        question=question,
        expected_answer=_extract_expected_answer(question),
    )
    return f"Sure — here is your assessment question:\n{question}"


def has_pending_assessment(session_id: str) -> bool:
    return session_id in _sessions


def grade_assessment_answer(session_id: str, answer: str) -> tuple[str, bool]:
    state = _sessions.pop(session_id)
    normalized = answer.strip().lower()

    if state.expected_answer:
        passed = normalized == state.expected_answer
        if passed:
            return "✅ Correct answer. Great job!", True
        return f"❌ Not quite. Expected answer: {state.expected_answer}", False

    passed = "because" in normalized and len(normalized.split()) >= 4
    if passed:
        return "✅ Good sentence. Assessment passed.", True
    return "❌ Please answer in a full sentence using 'because'.", False
