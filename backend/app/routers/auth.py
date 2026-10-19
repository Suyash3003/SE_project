from __future__ import annotations

from datetime import datetime, timezone
import os
import secrets
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, Depends, HTTPException

from app.auth import (
    create_access_token, get_current_user, hash_password, normalize_identifier,
    now_iso, require_roles, verify_password,
)
from app.database import get_db
from app.models import Dealer
from app.models.auth import User

router = APIRouter()


class Credentials(BaseModel):
    identifier: str = Field(min_length=3)
    password: str = Field(min_length=8)
    role: str


class Registration(BaseModel):
    email: str
    phone: str | None = None
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = normalize_identifier(value)
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("A valid email is required")
        return value


class DealerRegistration(Registration):
    name: str = Field(min_length=2)
    city: str = Field(min_length=2)
    state: str = Field(min_length=2)


class ResetRequest(BaseModel):
    identifier: str = Field(min_length=3)


class ResetPassword(BaseModel):
    token: str
    password: str = Field(min_length=8)


def _find_user(db, identifier: str) -> User | None:
    identifier = normalize_identifier(identifier)
    for user in db.query(User).all():
        if user.email == identifier or user.phone == identifier:
            return user
    return None


@router.post("/register/customer")
def register_customer(payload: Registration, db=Depends(get_db)):
    if _find_user(db, payload.email) or (payload.phone and _find_user(db, payload.phone)):
        raise HTTPException(status_code=409, detail="An account with these details already exists")
    user = User(
        email=payload.email,
        phone=normalize_identifier(payload.phone) if payload.phone else None,
        password_hash=hash_password(payload.password),
        role="customer",
        status="active",
        dealer_id=None,
        is_email_verified=False,
        verification_token=secrets.token_urlsafe(32),
        reset_token=None,
        reset_token_expires_at=None,
        created_at=now_iso(),
        last_login_at=None,
    )
    db.add(user)
    db.commit()
    result = {"message": "Customer account created. Verify your email before using email-only features.", "user_id": user.id}
    if os.getenv("AUTH_DEV_MODE") == "1":
        result["verification_token"] = user.verification_token
    return result


@router.post("/register/dealer")
def register_dealer(payload: DealerRegistration, db=Depends(get_db)):
    if _find_user(db, payload.email) or (payload.phone and _find_user(db, payload.phone)):
        raise HTTPException(status_code=409, detail="An account with these details already exists")
    dealer = Dealer(
        name=payload.name, code=f"PENDING-{payload.email.split('@')[0][:12]}",
        city=payload.city, state=payload.state, region_id=None,
        warehouse_id=None, latitude=None, longitude=None, tier="pending",
        credit_limit=0, performance_score=0,
    )
    db.add(dealer)
    db.flush()
    user = User(
        email=payload.email,
        phone=normalize_identifier(payload.phone) if payload.phone else None,
        password_hash=hash_password(payload.password),
        role="dealer",
        status="pending",
        dealer_id=dealer.id,
        is_email_verified=False,
        verification_token=secrets.token_urlsafe(32), reset_token=None, reset_token_expires_at=None,
        created_at=now_iso(), last_login_at=None,
    )
    db.add(user)
    db.commit()
    result = {"message": "Dealer registration submitted for admin approval.", "user_id": user.id}
    if os.getenv("AUTH_DEV_MODE") == "1":
        result["verification_token"] = user.verification_token
    return result


@router.post("/login")
def login(payload: Credentials, db=Depends(get_db)):
    if payload.role not in {"admin", "dealer", "customer"}:
        raise HTTPException(status_code=400, detail="Invalid role")
    user = _find_user(db, payload.identifier)
    if not user or user.role != payload.role or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.status != "active":
        raise HTTPException(status_code=403, detail="Your account is pending approval or suspended")
    user.last_login_at = now_iso()
    db.commit()
    return {"access_token": create_access_token(user), "token_type": "bearer", "role": user.role, "dealer_id": getattr(user, "dealer_id", None)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "phone": user.phone, "role": user.role, "status": user.status, "dealer_id": getattr(user, "dealer_id", None)}


@router.post("/forgot-password")
def forgot_password(payload: ResetRequest, db=Depends(get_db)):
    user = _find_user(db, payload.identifier)
    if user:
        from datetime import timedelta
        import secrets
        user.reset_token = secrets.token_urlsafe(32)
        user.reset_token_expires_at = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
        db.commit()
        result = {"message": "If an account exists, a reset link has been generated."}
        if os.getenv("AUTH_DEV_MODE") == "1":
            result["reset_token"] = user.reset_token
        return result
    return {"message": "If an account exists, a reset link has been generated."}


@router.post("/verify-email")
def verify_email(token: str, db=Depends(get_db)):
    user = next((candidate for candidate in db.query(User).all() if candidate.verification_token == token), None)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")
    user.is_email_verified = True
    user.verification_token = None
    db.commit()
    return {"message": "Email verified successfully"}


@router.post("/reset-password")
def reset_password(payload: ResetPassword, db=Depends(get_db)):
    user = next((candidate for candidate in db.query(User).all() if candidate.reset_token == payload.token), None)
    if not user or not user.reset_token_expires_at or datetime.fromisoformat(user.reset_token_expires_at) <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user.password_hash = hash_password(payload.password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()
    return {"message": "Password reset successfully"}


@router.get("/dealer-registrations")
def dealer_registrations(db=Depends(get_db), _: User = Depends(require_roles("admin"))):
    return [
        {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "dealer_id": user.dealer_id,
            "created_at": user.created_at,
        }
        for user in db.query(User).filter(User.role == "dealer", User.status == "pending").all()
    ]


@router.post("/dealer-registrations/{user_id}/approve")
def approve_dealer(user_id: int, db=Depends(get_db), _: User = Depends(require_roles("admin"))):
    user = db.query(User).filter(User.id == user_id, User.role == "dealer").first()
    if not user:
        raise HTTPException(status_code=404, detail="Dealer registration not found")
    user.status = "active"
    db.commit()
    return {"message": "Dealer approved"}


@router.post("/dealer-registrations/{user_id}/reject")
def reject_dealer(user_id: int, db=Depends(get_db), _: User = Depends(require_roles("admin"))):
    user = db.query(User).filter(User.id == user_id, User.role == "dealer").first()
    if not user:
        raise HTTPException(status_code=404, detail="Dealer registration not found")
    user.status = "suspended"
    db.commit()
    return {"message": "Dealer rejected"}
