from datetime import datetime, date, timedelta, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.models.addon import Addon
from src.app.models.appointment import Appointment, AppointmentStatus
from src.app.models.barber_schedule import BarberSchedule
from src.app.models.barber_unavailable_time import BarberUnavailableTime
from src.app.models.service import Service


def get_available_timeslots(
        db: Session,
        barber_id: int,
        target_date: date,
        service_id: int,
        addon_ids: Optional[List[int]] = None,
        slot_interval_minutes: int = 15,
) -> List[datetime]:
    if slot_interval_minutes <= 0 or 60 % slot_interval_minutes != 0:
        raise ValueError("slot_interval_minutes must be a positive integer and a divisor of 60.")

    day_of_week = target_date.weekday()
    schedule_entry = db.scalars(
        select(BarberSchedule)
        .where(BarberSchedule.barber_id == barber_id)
        .where(BarberSchedule.day_of_week == day_of_week)
    ).first()

    if not schedule_entry:
        return []

    working_start_time = schedule_entry.start_time
    working_end_time = schedule_entry.end_time

    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    total_duration_required_minutes = service.duration

    if addon_ids:
        addons = db.query(Addon).filter(Addon.id.in_(addon_ids)).all()
        if len(addons) != len(addon_ids):
            raise HTTPException(
                status_code=400,
                detail="Some addon IDs not found for timeslot calculation"
            )
        total_duration_required_minutes += sum(addon.duration for addon in addons)

    service_duration = timedelta(minutes=total_duration_required_minutes)

    working_start_datetime_utc = datetime.combine(target_date, working_start_time).replace(tzinfo=timezone.utc)
    working_end_datetime_utc = datetime.combine(target_date, working_end_time).replace(tzinfo=timezone.utc)

    start_of_day_for_query = working_start_datetime_utc.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day_for_query = start_of_day_for_query + timedelta(days=1)

    existing_appointments = db.scalars(
        select(Appointment)
        .where(Appointment.barber_id == barber_id)
        .where(Appointment.scheduled_time >= start_of_day_for_query)
        .where(Appointment.scheduled_time <= end_of_day_for_query)
        .where(Appointment.status != AppointmentStatus.cancelled)
    ).all()

    booked_intervals = []

    for appt in existing_appointments:
        start_utc = appt.scheduled_time.astimezone(timezone.utc)\
            if appt.scheduled_time.tzinfo else appt.scheduled_time.replace(tzinfo=timezone.utc)
        end_utc = start_utc + timedelta(minutes=appt.total_duration)
        booked_intervals.append({
            "start": end_utc,
            "end": end_utc
        })

    unavailable_intervals_db = db.scalars(
        select(BarberUnavailableTime)
        .where(BarberUnavailableTime.barber_id == barber_id)
        .where(BarberUnavailableTime.start_time >= start_of_day_for_query)
        .where(BarberUnavailableTime.start_time < end_of_day_for_query)
    ).all()

    for unavail_time in unavailable_intervals_db:
        start_utc = unavail_time.start_time.astimezone(
            timezone.utc) if unavail_time.start_time.tzinfo else unavail_time.start_time.replace(tzinfo=timezone.utc)
        end_utc = unavail_time.end_time.astimezone(
            timezone.utc) if unavail_time.end_time.tzinfo else unavail_time.end_time.replace(tzinfo=timezone.utc)

        booked_intervals.append({
            "start": start_utc,
            "end": end_utc
        })

    booked_intervals.sort(key=lambda x: x["start"])

    merged_booked_intervals = []
    if booked_intervals:
        current_merged = booked_intervals[0]
        for i in range(1, len(booked_intervals)):
            next_interval = booked_intervals[i]
            if next_interval["start"] <= current_merged["end"]:
                current_merged["end"] = max(current_merged["end"], next_interval["end"])
            else:
                merged_booked_intervals.append(current_merged)
                current_merged = next_interval
        merged_booked_intervals.append(current_merged)

    available_slots = []
    current_slot_start = working_start_datetime_utc

    start_minute = current_slot_start.minute
    if start_minute % slot_interval_minutes != 0:
        minutes_to_add = slot_interval_minutes - (start_minute % slot_interval_minutes)
        current_slot_start += timedelta(minutes=minutes_to_add)
        current_slot_start = current_slot_start.replace(second=0, microsecond=0)

    while current_slot_start + service_duration <= working_end_datetime_utc:
        potential_slot_end = current_slot_start + service_duration
        is_available = True

        for booked in merged_booked_intervals:
            if not (potential_slot_end <= booked["start"] or current_slot_start >= booked["end"]):
                is_available = False
                break

        if is_available:
            available_slots.append(current_slot_start)

        current_slot_start += timedelta(minutes=slot_interval_minutes)

    return available_slots
