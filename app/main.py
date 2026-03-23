import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.exceptions import global_exception_handler
from app.db.session import init_db, SessionLocal
from app.services.bootstrap import ensure_default_data

from app.routers import auth, clinics, patients, appointments, triage, pipeline, quantum, whatsapp

setup_logging(settings.DEBUG)
log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    try:
        db = SessionLocal()
        ensure_default_data(db)
        db.close()
    except Exception as exc:
        log.warning("Bootstrap data creation skipped: %s", exc)
    try:
        from app.ai.trainer import train_all
        from app.ai.model import load_model_bundle
        if not load_model_bundle("heart_disease") or not load_model_bundle("diabetes"):
            log.info("Training AI models because saved models were not found.")
            train_all()
    except Exception as exc:
        log.warning("AI model warmup/training skipped: %s", exc)
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)
app.add_exception_handler(Exception, global_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(clinics.router, prefix="/clinics", tags=["clinics"])
app.include_router(patients.router, prefix="/patients", tags=["patients"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(triage.router, prefix="/triage", tags=["triage"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
app.include_router(quantum.router, prefix="/quantum", tags=["quantum"])
app.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"])

@app.get("/health")
def health():
    from app.quantum.qaoa import QUANTUM_BACKEND
    return {"status": "ok", "version": settings.APP_VERSION, "quantum_backend": QUANTUM_BACKEND}
