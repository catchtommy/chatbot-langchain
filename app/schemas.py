from pydantic import BaseModel, Field


class WebhookRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(min_length=1, max_length=128)


class WebhookResponse(BaseModel):
    reply: str
