import sys
from getpass import getpass
import logging
from sqlalchemy.orm import Session

from src.app.auth.security import hash_password
from src.app.database import SessionLocal
from src.app.models.user import User
from src.app.models import barber
from src.app.models import service
from src.app.models import appointment
from src.app.models import addon


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_admin():
    email = input("Admin email: ").strip().lower()
    name = input("Admin name: ").strip()

    phone_number = input("Admin phone number (optional): ").strip()
    if not phone_number:
        phone_number = None

    password = getpass("Admin password: ").strip()
    password_confirm = getpass("Confirm password: ").strip()

    if not email or not name or not password:
        logger.error("❌ Email, name, and password cannot be empty.")
        sys.exit(1)

    if password != password_confirm:
        logger.error("❌ Passwords do not match.")
        sys.exit(1)

    try:
        with SessionLocal() as db:
            if db.query(User).filter_by(email=email).first():
                logger.error(f"❌ User with this email '{email}' already exists.")
                return 1

            admin = User(
                name=name,
                email=email,
                hashed_password=hash_password(password),
                phone_number=phone_number,
                role="admin"
            )

            db.add(admin)
            db.commit()
            db.refresh(admin)

            logger.info(
                "✅ Admin '%s' created successfully with ID: %s",
                admin.email,
                admin.id,
            )
            return 0

    except Exception as e:
        logger.exception("❌ An error occurred: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(create_admin())
