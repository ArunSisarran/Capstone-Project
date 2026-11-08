import hashlib
import hmac
import uuid
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

def hash_password(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload.get("sub")
    except jwt.JWTError:
        return None

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id)
    except (ValueError, TypeError, AttributeError):
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise credentials_exception

    return user

PASSWORD_RESET_PURPOSE = "password-reset"

def _password_fingerprint(hashed_password: str) -> str:
    """Short, one way scramble of the user's CURRENT password hash. When the password changes,
    the fingerpoint changes, so any reset link made before the change stops working."""
    return hashlib.sha256(hashed_password.encode()).hexdigest()[:16]

def create_password_reset_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_expire_minutes)
    note = {
        "uid": str(user.id),
        "purpose": PASSWORD_RESET_PURPOSE,
        "fp": _password_fingerprint(user.hashed_password),
        "exp": expire,
    }
    return jwt.encode(note, settings.secret_key, algorithm=settings.algorithm)  

def user_from_password_reset_token(token: str, db: Session) -> User | None:
    """The user this reset token belongs to, or None if the token is not valid."""
    try:
        note = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.JWTError:                                           # forged, damaged or expired
        return None
    if note.get("purpose") != PASSWORD_RESET_PURPOSE:              # e.g. a login token
        return None
    try:
        user_id = uuid.UUID(note.get("uid"))
    except (ValueError, TypeError, AttributeError):
        return None
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        return None
    if not hmac.compare_digest(str(note.get("fp")), _password_fingerprint(user.hashed_password)):
        return None                                                # the password changed: link already used
    return user