from celery import shared_task
from src.app.services.email_service import send_email
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_email_task(self, email_to: str, subject: str, body: str):
    try:
        send_email(email_to, subject, body)
        logger.info("Email sent successfully to {email_to}")

    except Exception as e:
        logger.error(f"Failed to send email to {email_to}. Retrying. Reason: {e}")
        raise self.retry(e=e)
