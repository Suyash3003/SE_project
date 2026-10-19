from getpass import getpass

from app.auth import hash_password, now_iso
from app.database import SessionLocal
from app.models.auth import User


def main() -> None:
    email = input("Admin email: ").strip().lower()
    password = getpass("Admin password (8+ characters): ")
    if len(password) < 8:
        raise SystemExit("Password must be at least 8 characters")

    db = SessionLocal()
    try:
        if any(user.email == email for user in db.query(User).all()):
            raise SystemExit("An account with that email already exists")
        user = User(
            email=email,
            phone=None,
            password_hash=hash_password(password),
            role="admin",
            status="active",
            dealer_id=None,
            is_email_verified=True,
            verification_token=None,
            reset_token=None,
            reset_token_expires_at=None,
            created_at=now_iso(),
            last_login_at=None,
        )
        db.add(user)
        db.commit()
        print(f"Created admin account {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
