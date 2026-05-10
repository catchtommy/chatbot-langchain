from __future__ import annotations

import logging

from fastapi import FastAPI

from app.chatbot_service import TuitionChatbotService
from app.schemas import WebhookRequest, WebhookResponse


logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Tuition Management AI Chatbot", version="1.0.0")
service = TuitionChatbotService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/webhook", response_model=WebhookResponse)
def webhook(request: WebhookRequest) -> WebhookResponse:
    reply = service.handle_message(request.message, request.session_id)
    return WebhookResponse(reply=reply)
