from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit import record
from app.crypto_util import decrypt_field, encrypt_field
from app.db import get_db
from app.models import ActionItem, User
from app.security import current_user, require_clearance
router = APIRouter(prefix="/api/actions", tags=["actions"])
class ActionIn(BaseModel):
    meeting_id: int
    assignee_id: int
    title: str
    classification: str
    due_at: datetime
@router.get("")
async def list_actions(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(ActionItem))).scalars().all()
    out = []
    for a in rows:
        try:
            require_clearance(user, a.classification)
        except Exception:
            continue
        out.append({"id": a.id, "title": decrypt_field(a.title_enc), "classification": a.classification, "status": a.status, "escalated": a.escalated})
    return out
@router.post("")
async def create_action(body: ActionIn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    require_clearance(user, body.classification)
    a = ActionItem(meeting_id=body.meeting_id, assignee_id=body.assignee_id, title_enc=encrypt_field(body.title), classification=body.classification, due_at=body.due_at)
    db.add(a)
    await record(db, user.username, "ACTION_CREATE", body.title[:80])
    await db.commit()
    return {"id": a.id}
@router.post("/escalate-overdue")
async def escalate(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if user.role not in ("executive", "security_admin", "ea"):
        raise HTTPException(403, "escalation reserved")
    return {"escalated": 0}
