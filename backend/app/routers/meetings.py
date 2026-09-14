from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit import record
from app.config import CLASSIFICATION_BANNER
from app.crypto_util import decrypt_field, encrypt_field
from app.db import get_db
from app.models import Attendee, Meeting, User
from app.security import current_user, require_clearance
from app.services.watermark import make_watermark
router = APIRouter(prefix="/api/meetings", tags=["meetings"])
class MeetingIn(BaseModel):
    title: str
    classification: str
    starts_at: datetime
    ends_at: datetime
    language: str = "en"
    attendee_usernames: list[str] = []
def _view(m, user, ip):
    return {"id": m.id, "title": decrypt_field(m.title_enc), "classification": m.classification, "banner": CLASSIFICATION_BANNER[m.classification], "starts_at": m.starts_at.isoformat(), "ends_at": m.ends_at.isoformat(), "status": m.status, "language": m.language, "watermark": make_watermark(user.username, m.id, m.classification, ip)}
@router.get("")
async def list_meetings(request: Request, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Meeting))).scalars().all()
    ip = request.client.host if request.client else "0.0.0.0"
    visible = []
    for m in rows:
        try:
            require_clearance(user, m.classification)
            visible.append(_view(m, user, ip))
        except HTTPException:
            continue
    await record(db, user.username, "MEETING_LIST", f"count={len(visible)}")
    await db.commit()
    return visible
@router.post("")
async def create_meeting(body: MeetingIn, request: Request, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if user.role not in ("executive", "ea", "manager"):
        raise HTTPException(403, "cannot create meetings")
    require_clearance(user, body.classification)
    m = Meeting(title_enc=encrypt_field(body.title), classification=body.classification, owner_id=user.id, starts_at=body.starts_at, ends_at=body.ends_at, language=body.language)
    db.add(m)
    await db.flush()
    await record(db, user.username, "MEETING_CREATE", f"id={m.id}")
    await db.commit()
    return _view(m, user, request.client.host if request.client else "0.0.0.0")
