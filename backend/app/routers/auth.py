from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit import record
from app.db import get_db
from app.models import User
from app.security import issue_token, verify_password
router = APIRouter(prefix="/api/auth", tags=["auth"])
class LoginIn(BaseModel):
    username: str
    password: str
    mfa_assertion: str = "dev-hardware-stub"
@router.post("/login")
async def login(body: LoginIn, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.username == body.username))).scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        await record(db, body.username, "LOGIN_FAIL", "invalid credentials")
        await db.commit()
        raise HTTPException(401, "invalid credentials")
    token = issue_token(user)
    await record(db, user.username, "LOGIN_OK", f"role={user.role}")
    await db.commit()
    return {"access_token": token, "token_type": "bearer", "user": {"username": user.username, "display_en": user.display_en, "display_ar": user.display_ar, "role": user.role, "clearance": user.clearance, "language": user.language}}
