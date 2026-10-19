from __future__ import annotations
from pydantic import BaseModel, Field, field_validator
from app.auth import normalize_identifier


class CredentialsSchema(BaseModel):
    identifier: str = Field(..., min_length=3, description="Email or dealer code")
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(admin|dealer|customer)$")


class RegistrationSchema(BaseModel):
    email: str
    phone: str | None = None
    password: str = Field(..., min_length=8)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        val = normalize_identifier(value)
        if "@" not in val or "." not in val.split("@")[-1]:
            raise ValueError("A valid email address is required")
        return val


class DealerRegistrationSchema(RegistrationSchema):
    name: str = Field(..., min_length=2)
    city: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2)


class PasswordResetRequestSchema(BaseModel):
    identifier: str = Field(..., min_length=3)


class PasswordResetConfirmSchema(BaseModel):
    token: str = Field(..., min_length=16)
    new_password: str = Field(..., min_length=8)
