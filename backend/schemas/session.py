import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from schemas.message import MessageResponse


class SessionRequest(BaseModel):
    model: str
    system_prompt: str
    temperature: float
    max_tokens: int = 2048


class SessionRespose(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    model_id: uuid.UUID
    system_prompt: str | None
    temperature: float
    max_tokens: int = 2048
    created_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)
