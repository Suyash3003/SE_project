from app.database import Document, Field


class User(Document):
    __collection__ = "users"
    email = Field("email")
    phone = Field("phone")
    password_hash = Field("password_hash")
    role = Field("role")
    status = Field("status")
    dealer_id = Field("dealer_id")
    is_email_verified = Field("is_email_verified")
    verification_token = Field("verification_token")
    reset_token = Field("reset_token")
    reset_token_expires_at = Field("reset_token_expires_at")
    created_at = Field("created_at")
    last_login_at = Field("last_login_at")
