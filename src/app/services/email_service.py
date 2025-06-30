import logging

logger = logging.getLogger(__name__)


def send_password_reset_email(email_to: str, token: str, frontend_url: str) -> None:
    """
        Simulates sending a password reset email.
        In a real application, this would contain logic for sending email via synchronous libraries.
        """
    reset_link = f"{frontend_url}/reset-password?token={token}"

    logger.info(f"--- EMAIL SEND SIMULATION ---")
    logger.info(f"To: {email_to}")
    logger.info(f"Subject: Password Reset for BarberShop")
    logger.info(f"Content: You requested a password reset. Please click the link to reset your password: {reset_link}")
    logger.info("--- END OF SIMULATION ---")
