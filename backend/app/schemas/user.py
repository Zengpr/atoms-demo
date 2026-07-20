from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.config import CAMEL_CONFIG


class UserRegister(BaseModel):
    email: str
    username: str = Field(min_length=2, max_length=30)
    password: str = Field(min_length=6, max_length=100)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    avatar_url: Optional[str] = Field(None, serialization_alias="avatarUrl")
    credits: int
    created_at: datetime

    model_config = CAMEL_CONFIG


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

    model_config = CAMEL_CONFIG
