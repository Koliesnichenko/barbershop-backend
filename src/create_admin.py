import sys
from getpass import getpass
import logging
from sqlalchemy.orm import Session

from src.app.auth.security import hash_password
from src.app.database import SessionLocal
from src.app.models.user import User


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def create_admin():
    db: Session = SessionLocal()

    email = input("Admin email: ").strip()
    name = input("Admin name: ").strip()
    password = getpass("Admin password: ").strip()

    existing = db.query(User).filter_by(email=email).first()
    if existing:
        logger.error("❌ User with this email already exists")
        sys.exit(1)

    admin = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        role="admin"
    )

    db.add(admin)
    db.commit()
    db.close()

    logger.error("✅ Admin created successfully")


if __name__ == "__main__":
    create_admin()
