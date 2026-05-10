from __future__ import annotations

import logging

from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.assessment import (
    grade_assessment_answer,
    has_pending_assessment,
    start_assessment,
    wants_assessment,
)
from app.config import settings
from app.odoo_client import OdooClient, extract_contact_info
from app.rag import get_vectorstore


logger = logging.getLogger(__name__)


class TuitionChatbotService:
    def __init__(self) -> None:
        self._odoo = OdooClient()
        self._last_lead_by_session: dict[str, int] = {}
        self._chain = self._build_chain()

    def _build_chain(self):
        if not settings.groq_api_key:
            logger.warning("GROQ_API_KEY not set, fallback responses will be used")
            return None

        llm = ChatGroq(api_key=settings.groq_api_key, model=settings.groq_model, temperature=0)
        prompt = ChatPromptTemplate.from_template(
            """
You are a tuition management assistant for parents.
Answer using only the provided context. If unknown, say you are not sure.

Context:
{context}

Question:
{input}
""".strip()
        )
        retriever = get_vectorstore().as_retriever(search_kwargs={"k": 4})
        qa_chain = create_stuff_documents_chain(llm, prompt)
        return create_retrieval_chain(retriever, qa_chain)

    def _answer_with_rag(self, message: str) -> str:
        if self._chain is None:
            return (
                "I can help with courses and fees, but LLM is not configured yet. "
                "Please set GROQ_API_KEY to enable full AI responses."
            )

        try:
            result = self._chain.invoke({"input": message})
            return str(result.get("answer", "I do not have enough information right now."))
        except Exception as exc:  # noqa: BLE001
            logger.warning("RAG chain invocation failed: %s", exc)
            return "I am having trouble answering right now. Please try again in a moment."

    def handle_message(self, message: str, session_id: str) -> str:
        contact = extract_contact_info(message)
        lead_id = None
        if contact:
            lead_id = self._odoo.create_or_update_lead(contact, note=f"Session: {session_id}")
            if lead_id:
                self._last_lead_by_session[session_id] = lead_id

        if wants_assessment(message):
            return start_assessment(session_id, message)

        if has_pending_assessment(session_id):
            result, passed = grade_assessment_answer(session_id, message)
            lead_for_session = self._last_lead_by_session.get(session_id)
            if lead_for_session:
                self._odoo.update_assessment_note(
                    lead_for_session,
                    f"Assessment result for session {session_id}: {'passed' if passed else 'failed'}",
                )
            return result

        reply = self._answer_with_rag(message)
        if contact:
            reply += "\n\nThanks — I have noted your contact details for follow-up."
        return reply
