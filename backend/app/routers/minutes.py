from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit import record
from app.crypto_util import decrypt_field, encrypt_field
from app.db import get_db
from app.models import Meeting, Minutes, User
from app.security import current_user, require_clearance
from app.services.watermark import make_watermark
router = APIRouter(prefix="/api/minutes", tags=["minutes"])
class MinutesIn(BaseModel):
    meeting_id: int
    body: str
@router.post("")
async def upsert_minutes(body: MinutesIn, request: Request, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    m = await db.get(Meeting, body.meeting_id)
    require_clearance(user, m.classification)
    ip = request.client.host if request.client else "0.0.0.0"
    wm = make_watermark(user.username, m.id, m.classification, ip)
    existing = (await db.execute(select(Minutes).where(Minutes.meeting_id == m.id))).scalar_one_or_none()
    if existing:
        existing.body_enc = encrypt_field(body.body)
        existing.watermark_token = wm["token"]
    else:
        db.add(Minutes(meeting_id=m.id, body_enc=encrypt_field(body.body), watermark_token=wm["token"]))
    await record(db, user.username, "MINUTES_WRITE", str(m.id))
    await db.commit()
    return {"ok": True, "watermark": wm}
@router.get("/{meeting_id}")
async def get_minutes(meeting_id: int, request: Request, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    m = await db.get(Meeting, meeting_id)
    require_clearance(user, m.classification)
    row = (await db.execute(select(Minutes).where(Minutes.meeting_id == meeting_id))).scalar_one_or_none()
    await record(db, user.username, "MINUTES_READ", str(meeting_id))
    await db.commit()
    return {"meeting_id": meeting_id, "body": decrypt_field(row.body_enc) if row else "", "classification": m.classification}
