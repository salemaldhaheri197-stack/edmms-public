from dataclasses import dataclass
from app.config import settings, CLEARANCE_RANK
@dataclass
class VoiceIntent:
    language: str
    intent: str
    title: str
    classification: str
    when_iso: str | None
class ZeroRetentionVoiceGateway:
    def parse_transcript(self, transcript: str, language: str) -> VoiceIntent:
        text = transcript.strip()
        lower = text.lower()
        intent = "book" if any(k in lower for k in ("book", "schedule", "احجز")) else "query"
        classification = "SECRET" if "secret" in lower or "سري" in text else "RESTRICTED"
        if classification not in CLEARANCE_RANK:
            classification = "RESTRICTED"
        return VoiceIntent(language=language, intent=intent, title=text[:180], classification=classification, when_iso=None)
    def purge_audio(self, buffer):
        return None
gateway = ZeroRetentionVoiceGateway()
