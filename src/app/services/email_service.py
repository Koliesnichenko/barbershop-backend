import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart

from src.app.core.config import settings
from email.mime.text import MIMEText


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
