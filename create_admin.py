import sys
from getpass import getpass
import logging
from sqlalchemy.orm import Session

from src.app.auth.security import hash_password
from src.app.database import SessionLocal
from src.app.models.user import User


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def create_admin():
    db: Session = SessionLocal()
    try:
        email = input("Admin email: ").strip()
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

        existing = db.query(User).filter_by(email=email).first()
        if existing:
            logger.error(f"❌ User with this email '{email}' already exists.")
            sys.exit(1)

        admin = User(
            name=name,
            email=email,
            hashed_password=hash_password(password),
            phone_number=phone_number,
            role="admin"
        )

        db.add(admin)
        db.commit()
        db.close()

        logger.info(f"✅ Admin '{admin.email}' created successfully with ID: {admin.id}")

    except Exception as e:
        db.rollback()
        logger.error(f"❌ An error occurred: {e}", exc_info=True)
        sys.exit(1)


    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
