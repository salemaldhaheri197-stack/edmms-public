from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    app_secret: str = "dev-only-change-me"
    encryption_key: str = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    jwt_ttl_seconds: int = 900
    siem_endpoint: str = ""
    elevenlabs_gateway_url: str = "https://isolated-elevenlabs.internal"
    elevenlabs_zdr: bool = True
    database_url: str = "sqlite+aiosqlite:///./edmms.db"
    cors_origins: str = "http://localhost:5173"

settings = Settings()
CLEARANCE_RANK = {"UNCLASSIFIED": 0, "RESTRICTED": 1, "CONFIDENTIAL": 2, "SECRET": 3, "TOP_SECRET": 4}
CLASSIFICATION_BANNER = {"UNCLASSIFIED": {"en": "UNCLASSIFIED", "ar": "غير مصنف"}, "RESTRICTED": {"en": "RESTRICTED", "ar": "مقيد"}, "CONFIDENTIAL": {"en": "CONFIDENTIAL", "ar": "سري"}, "SECRET": {"en": "SECRET", "ar": "سري للغاية"}, "TOP_SECRET": {"en": "TOP SECRET", "ar": "سري للغاية جداً"}}
