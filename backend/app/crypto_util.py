import base64, hashlib, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings

def _key() -> bytes:
    try:
        k = base64.b64decode(settings.encryption_key)
        if len(k) == 32:
            return k
    except Exception:
        pass
    return hashlib.sha256(settings.encryption_key.encode()).digest()

def encrypt_field(plaintext: str) -> str:
    if not plaintext:
        return ""
    aes = AESGCM(_key())
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("ascii")

def decrypt_field(blob: str) -> str:
    if not blob:
        return ""
    data = base64.b64decode(blob)
    return AESGCM(_key()).decrypt(data[:12], data[12:], None).decode("utf-8")

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()
