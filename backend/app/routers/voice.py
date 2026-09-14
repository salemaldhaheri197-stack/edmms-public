from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.audit import record
from app.crypto_util import encrypt_field
from app.db import get_db
from app.models import Meeting, User
from app.security import current_user, require_clearance
from app.services.voice_gateway import gateway
router = APIRouter(prefix="/api/voice", tags=["voice"])
class VoiceTurn(BaseModel):
    language: str = "en"
    transcript: str
    audio_b64: str | None = None
@router.post("/book")
async def voice_book(body: VoiceTurn, user: User = Depends(current_user), db: AsyncSession = Depends(get_db)):
    intent = gateway.parse_transcript(body.transcript, body.language)
    gateway.purge_audio(None)
    await record(db, user.username, "VOICE_SESSION", intent.intent)
    if intent.intent == "book":
        require_clearance(user, intent.classification)
        start = datetime.utcnow() + timedelta(hours=2)
        m = Meeting(title_enc=encrypt_field(intent.title), classification=intent.classification, owner_id=user.id, starts_at=start, ends_at=start + timedelta(minutes=45), language=intent.language)
        db.add(m)
        await db.commit()
        return {"spoken_en": "Meeting drafted. Audio discarded.", "intent": intent.intent, "meeting_id": m.id, "zdr": True}
    await db.commit()
    return {"spoken_en": "Query processed. No audio retained.", "intent": intent.intent, "zdr": True}
