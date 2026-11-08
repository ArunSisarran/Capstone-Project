from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token, create_password_reset_token, hash_password, user_from_password_reset_token,
    verify_password,
)
from app.models.models import User
from app.schemas.schemas import (
    ForgotPasswordRequest, LoginRequest, ResetPasswordRequest, Token, UserCreate, UserOut,
)
from app.services.email import allow_reset_email, reset_email_body, send_email

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=user_in.email, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)

@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Email a password-reset link. The answer is ALWAYS the same, whether or not the address has an
    account, so this cannot be used to find out who is registered."""
    user = db.query(User).filter(func.lower(User.email) == request.email.lower()).first()
    if user and allow_reset_email(user.email):
        link = f"{settings.frontend_url.rstrip('/')}/reset-password?token={create_password_reset_token(user)}"
        background_tasks.add_task(send_email, user.email, "Reset your password", reset_email_body(link))
    return {"detail": "If that email is registered, a reset link has been sent."}