from src.app.celery_worker import celery_app
from src.app.services.email_service import _send_email


@celery_app.task
def send_reminder_email(email_to, subject, body):
    _send_email(email_to, subject, body)