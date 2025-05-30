from sqlalchemy.orm import Session

from src.app.database import SessionLocal
from src.app.models.addon import Addon
from src.app.models.barber import Barber
from src.app.models.service import Service


def run_seed_script():
    db: Session = SessionLocal()

    db.query(Barber).delete()
    db.query(Service).delete()
    db.query(Addon).delete()

    db.commit()

    # Barbers create
    barber1 = Barber(name="John", role="barber")
    barber2 = Barber(name="Jack", role="barber")

    # Services
    service1 = Service(name="Haircut", price=100, duration=60)
    service2 = Service(name="Beard Trim", price=50, duration=30)

    # Addons
    addon1 = Addon(name="Beard care", price=50, duration=30, category="comfort")
    addon2 = Addon(name="Hair care", price=30, duration=30, category="comfort")

    barber1.services = [service1, service2]
    barber2.services = [service1, service2]

    barber1.addons = [addon1, addon2]
    barber2.addons = [addon1, addon2]

    db.add_all([barber1, barber2, service1, service2, addon1, addon2])
    db.commit()
    db.close()

    print("✅ Seed completed")


if __name__ == "__main__":
    run_seed_script()