from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.db import SessionLocal, init_db
from app.routers import actions, audit_api, auth, meetings, minutes, voice
from app.seed import seed_if_empty

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with SessionLocal() as db:
        await seed_if_empty(db)
    yield

app = FastAPI(title="EDMMS", description="High-Security Executive Meeting Management System reference API", version="0.4.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(meetings.router)
app.include_router(voice.router)
app.include_router(minutes.router)
app.include_router(actions.router)
app.include_router(audit_api.router)

@app.get("/api/health")
async def health():
    return {"status": "ok", "zdr": settings.elevenlabs_zdr}
