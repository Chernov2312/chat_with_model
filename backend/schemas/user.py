import uuid

from pydantic import BaseModel, ConfigDict, EmailStr


class UserReadResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    email: EmailStr
