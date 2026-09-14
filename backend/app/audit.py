from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crypto_util import sha256_hex
from app.models import AuditEvent
from app.config import settings
import httpx
GENESIS = "0" * 64
async def record(db: AsyncSession, actor: str, action: str, detail: str) -> AuditEvent:
    last = (await db.execute(select(AuditEvent).order_by(AuditEvent.id.desc()))).scalars().first()
    prev = last.event_hash if last else GENESIS
    ts = datetime.now(timezone.utc).isoformat()
    event_hash = sha256_hex(f"{prev}|{ts}|{actor}|{action}|{detail}")
    ev = AuditEvent(actor=actor, action=action, detail=detail, prev_hash=prev, event_hash=event_hash)
    db.add(ev)
    await db.flush()
    if settings.siem_endpoint:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(settings.siem_endpoint, json={"cef": f"CEF:0|EDMMS|Audit|1|{action}|{detail}|5|actor={actor}"})
        except Exception:
            pass
    return ev
async def verify_chain(db: AsyncSession) -> bool:
    rows = (await db.execute(select(AuditEvent).order_by(AuditEvent.id.asc()))).scalars().all()
    prev = GENESIS
    for r in rows:
        if r.prev_hash != prev:
            return False
        alt = sha256_hex(f"{r.prev_hash}|{r.ts.isoformat()}|{r.actor}|{r.action}|{r.detail}")
        if r.event_hash != alt:
            return False
        prev = r.event_hash
    return True
