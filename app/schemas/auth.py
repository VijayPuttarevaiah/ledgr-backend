import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_RULE_MESSAGE = (
    "password must be at least 12 characters and include a number and mixed case"
)


def _validate_password_strength(value: str) -> str:
    if (
        len(value) < 12
        or not re.search(r"[0-9]", value)
        or not re.search(r"[a-z]", value)
        or not re.search(r"[A-Z]", value)
    ):
        raise ValueError(PASSWORD_RULE_MESSAGE)
    return value


class RegisterRequest(BaseModel):
    model_config = {"extra": "forbid"}

    first_name: str = Field(..., max_length=60)
    last_name: str = Field(..., max_length=60)
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, value: str) -> str:
        return _validate_password_strength(value)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    role: str
    created_at: str


class LoginRequest(BaseModel):
    model_config = {"extra": "forbid"}

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
