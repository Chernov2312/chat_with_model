import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from schemas.message import MessageResponse


class SessionRequest(BaseModel):
    model: str
    system_prompt: str
    temperature: float
    max_tokens: int = 2048


class SessionRespose(BaseModel):
    id: uuid.UUID
    model: str
    system_prompt: str
    temperature: float
    max_tokens: int = 2048
    created_at: datetime
    messages: list[MessageResponse]
    model_config = ConfigDict(from_attributes=True)
