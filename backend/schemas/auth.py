import re
import uuid

from pydantic import BaseModel, EmailStr, Field

password_valid = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$",
)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    password: str = Field(..., min_length=8, max_length=250)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=250)


class UserResponse(BaseModel):
    id: uuid.UUID = Field(...)
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=100)
    access_token: str = Field(..., max_length=250)
    token_type: str = "bearer"
