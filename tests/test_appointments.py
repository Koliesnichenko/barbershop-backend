import pytest
from datetime import datetime, timedelta, timezone

from src.app.models.barber import Barber
from src.app.models.service import Service
from src.app.models.addon import Addon


@pytest.fixture
def barber(db_session):
    barber = Barber(name="Test Barber")
    db_session.add(barber)
    db_session.commit()
    db_session.refresh(barber)
    return barber


@pytest.fixture
def service(db_session):
    service = Service(
        name="Haircut",
        duration=30,
        price=300,
    )
    db_session.add(service)
    db_session.commit()
    db_session.refresh(service)
    return service


@pytest.fixture
def addon(db_session):
    addon = Addon(
        name="Beard",
        duration=15,
        price=100,
    )
    db_session.add(addon)
    db_session.commit()
    db_session.refresh(addon)
    return addon


def test_create_appointment(client, barber, service, addon):
    schedule_time = (
        datetime.now(timezone.utc) + timedelta(hours=1)
    ).isoformat()

    payload = {
        "name": "Test Name",
        "phone_number": "+47933384945",
        "barber_id": barber.id,
        "service_id": service.id,
        "addon_ids": [addon.id],
        "scheduled_time": schedule_time,
    }

    response = client.post("/api/appointments/", json=payload)

    assert response.status_code == 201

    data = response.json()
    assert data["barber_id"] == barber.id
    assert data["service_id"] == service.id
    assert data["status"] == "upcoming"
    assert data["total_price"] == service.price + addon.price

