import logging
import random
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart

from src.app.schemas.appointment import AppointmentShortUserView, AppointmentShortUserView

from sqlalchemy.orm import Session

from src.app.core.config import settings
from email.mime.text import MIMEText

from src.app.models.appointment import AppointmentStatus
from src.app.models.user import User

logger = logging.getLogger(__name__)


def _send_email(email_to: str, subject: str, body: str):
    """
    inner function for sending email
    """

    try:
        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAIL_SENDER_NAME} <{settings.EMAIL_SENDER_ADDRESS}>"
        msg["To"] = email_to

        context = ssl.create_default_context()

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
            logger.info(f"Email {subject} sent to {email_to}")
    except smtplib.SMTPAuthenticationError:
        logger.error(f"Failed to send email to {email_to}: SMTP authentication error")

    except smtplib.SMTPConnectError as e:
        logger.error(f"Failed connect to SMTP server: {settings.SMTP_HOST}:{settings.SMTP_PORT}: {e}."
                     f" Check host and port.")

    except Exception as e:
        logger.error(f"An unexpected error occurred while sending email to {email_to}: {e}")


def send_password_reset_email(email_to: str, token: str, frontend_url: str) -> None:
    """
    inner function for sending email to reset password
    """

    reset_link = f"{frontend_url}/reset-password?token={token}"
    subject = "Password Reset for BarberShop"
    body = f"""
    <html>
      <body>
        <p>Hello,</p>
        <p>You requested to reset your password for your BarberShop account.
         Please click the following link to reset your password:</p>
        <p><a href="{reset_link}">Reset your password here</a></p>
        <p>This link will expire in {settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
        <p>Best regards,<br>The BarberShop Team</p>
      </body>
    </html>
    """
    
    _send_email(email_to, subject, body)


def send_registration_email(email_to: str, user_name: str, frontend_url: str):
    """
    sending email after successful registration
    """
    subject = "Welcome to BarberShop"
    body = f"""
    <html>
      <body>
        <p>Hello, {user_name}</p>
        <p>Welcome to BarberShop</p>
        <p>You can now log in and start using our services.</p>
        <p>Return to our website: <a href="{frontend_url}">{frontend_url}</a></p>
        <p>Best regards,<br>The BarberShop Team</p>
      </body>
    </html>
    """

    _send_email(email_to, subject, body)


def generate_and_send_verification_code(db: Session, user: User):
    code = str(random.randint(10 ** (settings.EMAIL_VERIFICATION_CODE_LENGTH - 1),
                              10 ** settings.EMAIL_VERIFICATION_CODE_LENGTH - 1))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES)

    user.verification_code = code
    user.verification_code_expires_at = expires_at
    db.commit()
    db.refresh(user)

    subject = "Email Verification Code"
    body = f"""
    <html>
    <body>
        <p>Hi, {user.name}!</p>
        <p>Your verification code is: <strong>{code}</strong></p>
        <p>This code will expire in {settings.EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES} minutes.</p>
        <p>Best regards,<br>The BarberShop Team</p>
    </body>
    </html>
    """

    _send_email(user.email, subject, body)


def send_booking_confirmation_email(
        email_to: str,
        user_name: str,
        scheduled_day: str,
        scheduled_date: str,
        scheduled_time: str,
        barber_name: str,
        service_title: str,
        total_price: int,
        total_duration: int,
        status: str,
        frontend_url: str
) -> None:
    subject = "Booking Confirmation"
    body = f"""
    <html>
    <body>
        <p>Hello, {user_name}</p>
        <p>Your appointment has been confirmed:</p>
        <ul>
            <li><strong>Date:</strong> {scheduled_day}, {scheduled_date}</li>
            <li><strong>Time:</strong> {scheduled_time}</li>
            <li><strong>Barber:</strong> {barber_name}</li>
            <li><strong>Service:</strong> {service_title}</li>
            <li><strong>Price:</strong> {total_price}</li>
            <li><strong>Duration: </strong> {total_duration}</li>
            <li><strong>Status</strong> {status}</li>
            <li><strong>Our website:</strong> {frontend_url}</li>
        </ul>
        <p>See you soon!</p>
        <p><a href="{frontend_url}">Visit our website</a></p>
    </body>
    </html>
    """

    _send_email(email_to, subject, body)


def send_booking_cancellation_email(
        email_to: str,
        user_name: str,
        scheduled_day: str,
        scheduled_date: str,
        scheduled_time: str,
        barber_name: str,
        service_title: str,
        total_price: int,
        total_duration: int,
        status: str,
        frontend_url: str
) -> None:
    subject = "Booking Cancellation"
    body = f"""
    <html>
    <body>
        <p>Hello, {user_name}</p>
        <p>Your booking has been cancelled:</p>
        <ul>
            <li><strong>Date:</strong> {scheduled_day}, {scheduled_date}</li>
            <li><strong>Time:</strong> {scheduled_time}</li>
            <li><strong>Barber:</strong> {barber_name}</li>
            <li><strong>Service:</strong> {service_title}</li>
            <li><strong>Price:</strong> {total_price}</li>
            <li><strong>Duration: </strong> {total_duration}</li>
            <li><strong>Status</strong> {status}</li>
            <li><strong>Our website:</strong> {frontend_url}</li>
        </ul>
        <p>If this was a mistake, you can rebook anytime.</p>
        <p><a href="{frontend_url}">Visit our website</a></p>
    </body>
    </html>
    """

    _send_email(email_to, subject, body)
