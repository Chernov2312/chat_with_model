import uuid
from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, ConfigDict


class MessageRequest(BaseModel):
    content: str
    stream_options: dict[str, bool]


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: Literal["user", "system", "assistant"]
    content: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MessageHistoryResponse(BaseModel):
    messages: List[MessageResponse]
