from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crypto_util import encrypt_field
from app.models import ActionItem, Meeting, User
from app.security import hash_password
SEED_USERS = [("ceo", "Chief Executive", "CEO", "executive", "TOP_SECRET"), ("vp.ops", "VP Operations", "VP", "executive", "SECRET"), ("ea.ceo", "Executive Assistant", "EA", "ea", "SECRET"), ("manager.it", "IT Manager", "IT", "manager", "CONFIDENTIAL"), ("analyst", "Analyst", "Analyst", "employee", "RESTRICTED"), ("soc.admin", "SOC Administrator", "SOC", "security_admin", "SECRET")]
async def seed_if_empty(db: AsyncSession) -> None:
    if (await db.execute(select(User))).scalars().first():
        return
    users = {}
    for uname, en, ar, role, clr in SEED_USERS:
        u = User(username=uname, display_en=en, display_ar=ar, password_hash=hash_password("ChangeMe!2026"), role=role, clearance=clr, language="en")
        db.add(u)
        users[uname] = u
    await db.flush()
    start = datetime.utcnow() + timedelta(days=1)
    m = Meeting(title_enc=encrypt_field("Q3 Strategic Oversight"), classification="SECRET", owner_id=users["ceo"].id, starts_at=start, ends_at=start + timedelta(hours=1), status="scheduled", language="en")
    db.add(m)
    await db.flush()
    db.add(ActionItem(meeting_id=m.id, assignee_id=users["manager.it"].id, title_enc=encrypt_field("Harden isolated voice gateway mTLS"), classification="SECRET", due_at=datetime.utcnow() + timedelta(days=3), status="open"))
    await db.commit()
