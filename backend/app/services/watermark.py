from datetime import datetime, timezone
from app.crypto_util import sha256_hex
def make_watermark(username, meeting_id, classification, client_ip):
    ts = datetime.now(timezone.utc).isoformat()
    token = sha256_hex(f"{username}|{meeting_id}|{ts}|{classification}|{client_ip}")
    return {"token": token, "banner": f"{classification} | {username} | {ts} | {client_ip}", "ts": ts}
