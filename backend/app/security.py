from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from argon2 import PasswordHasher
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings, CLEARANCE_RANK
from app.db import get_db
from app.models import User
ph = PasswordHasher()
bearer = HTTPBearer(auto_error=False)
def hash_password(pw: str) -> str:
    return ph.hash(pw)
def verify_password(pw: str, hashed: str) -> bool:
    try:
        return ph.verify(hashed, pw)
    except Exception:
        return False
def issue_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user.username, "role": user.role, "clr": user.clearance, "uid": user.id, "iat": int(now.timestamp()), "exp": int((now + timedelta(seconds=settings.jwt_ttl_seconds)).timestamp())}
    return jwt.encode(payload, settings.app_secret, algorithm="HS256")
async def current_user(creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)], db: Annotated[AsyncSession, Depends(get_db)], x_mfa_assertion: Annotated[str | None, Header()] = None) -> User:
    if creds is None:
        raise HTTPException(401, "hardware MFA + bearer token required")
    try:
        data = jwt.decode(creds.credentials, settings.app_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(401, "invalid or expired token")
    user = (await db.execute(select(User).where(User.username == data["sub"]))).scalar_one_or_none()
    if not user:
        raise HTTPException(401, "unknown principal")
    if settings.app_env != "development" and not x_mfa_assertion:
        raise HTTPException(401, "step-up hardware MFA assertion missing")
    return user
def require_clearance(user: User, classification: str) -> None:
    if CLEARANCE_RANK.get(user.clearance, -1) < CLEARANCE_RANK.get(classification, 99):
        raise HTTPException(403, "clearance insufficient for meeting classification")
