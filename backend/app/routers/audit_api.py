from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit import verify_chain
from app.db import get_db
from app.models import AuditEvent, User
from app.security import current_user
router = APIRouter(prefix="/api/audit", tags=["audit"])
@router.get("")
async def list_audit(user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    if user.role != "security_admin":
        raise HTTPException(403, "SOC / CISO role required")
    rows = (await db.execute(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(200))).scalars().all()
    return {"chain_intact": await verify_chain(db), "events": [{"id": r.id, "actor": r.actor, "action": r.action, "detail": r.detail} for r in rows]}
