from datetime import datetime, date, timedelta
from typing import List

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.app.models.appointment import Appointment
from src.app.models.barber_schedule import BarberSchedule
from src.app.models.barber_unavailable_time import BarberUnavailableTime
from src.app.models.service import Service


def get_available_timeslots(
        db: Session,
        barber_id: int,
        target_date: date,
        service_id: int,
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

    service_duration_minutes = service.duration
    service_duration = timedelta(minutes=service_duration_minutes)

    working_start_datetime = datetime.combine(target_date, working_start_time)
    working_end_datetime = datetime.combine(target_date, working_end_time)

    existing_appointments = db.scalars(
        select(Appointment)
        .where(Appointment.barber_id == barber_id)
        .where(Appointment.scheduled_time >= datetime.combine(target_date, datetime.min.time()))
        .where(Appointment.scheduled_time < datetime.combine(target_date, datetime.min.time()) + timedelta(days=1))
    ).all()

    booked_intervals = []

    for appt in existing_appointments:
        booked_intervals.append({
            "start": appt.scheduled_time,
            "end": appt.scheduled_time + timedelta(minutes=appt.total_duration)
        })

    unavailable_intervals_db = db.scalars(
        select(BarberUnavailableTime)
        .where(BarberUnavailableTime.barber_id == barber_id)
        .where(BarberUnavailableTime.start_time >= datetime.combine(
            target_date,
            datetime.min.time()))
        .where(
            BarberUnavailableTime.start_time < datetime.combine(target_date, datetime.min.time()) + timedelta(days=1))
    ).all()

    for unavail_time in unavailable_intervals_db:
        booked_intervals.append({
            "start": unavail_time.start_time,
            "end": unavail_time.end_time
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
    current_slot_start = working_start_datetime
    start_minute = current_slot_start.minute
    if start_minute % slot_interval_minutes != 0:
        current_slot_start += timedelta(minutes=(slot_interval_minutes - (start_minute % slot_interval_minutes)))
        current_slot_start = current_slot_start.replace(second=0, microsecond=0)  # Clear seconds/micros

    while current_slot_start + service_duration <= working_end_datetime:
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
