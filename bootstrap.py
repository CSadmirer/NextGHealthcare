from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.clinic import Clinic
from app.models.user import User
from app.core.security import hash_password
from app.core.config import settings

def ensure_default_data(db: Session) -> dict:
    clinic = db.scalars(select(Clinic).where(Clinic.name == settings.CLINIC_PUBLIC_NAME)).first()
    if not clinic:
        clinic = Clinic(name=settings.CLINIC_PUBLIC_NAME, plan="enterprise")
        db.add(clinic)
        db.commit()
        db.refresh(clinic)

    admin = db.scalars(select(User).where(User.email == settings.DEFAULT_ADMIN_EMAIL)).first()
    if not admin:
        admin = User(
            clinic_id=clinic.id,
            full_name="Clinic Admin",
            email=settings.DEFAULT_ADMIN_EMAIL,
            hashed_password=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
            role="admin",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    return {"clinic_id": clinic.id, "admin_email": admin.email}
