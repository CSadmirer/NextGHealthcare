import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FIXED: Removed .core, .db, and .services because your files are flat in the app/ folder
from app.config import settings
from app.logging_config import setup_logging
from app.exceptions import global_exception_handler
from app.session import init_db, SessionLocal
from app.bootstrap import ensure_default_data

# FIXED: Removed .routers as these files (auth.py, clinics.py, etc.) are directly in the app/ folder
from app import auth, clinics, patients, appointments, triage, pipeline, quantum, whatsapp

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
        # FIXED: Removed .ai because trainer.py and model.py are in the app/ folder
        from app.trainer import train_all
        from app.model import load_model_bundle
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

# FIXED: Routers are now imported directly from the app folder
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
    # FIXED: Removed .quantum because qaoa.py is in the app/ folder
    from app.qaoa import QUANTUM_BACKEND
    return {"status": "ok", "version": settings.APP_VERSION, "quantum_backend": QUANTUM_BACKEND}
