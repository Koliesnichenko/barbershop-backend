from typing import List
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path)

print("DEBUG: config.py DATABASE_URL =", os.getenv("DATABASE_URL"))


class Settings(BaseSettings):
    """
    Class to hold all app configuration settings.
    Settings are loaded from environment variables, including from the .env file.
    """

    DATABASE_URL: str = Field(..., alias="DATABASE_URL", description="URL for PostgreSQL database connection")
    SECRET_KEY: str = Field(..., alias="SECRET_KEY", description="Secret key for signing JWT tokens")

    SMTP_HOST: str = Field(..., description="SMTP server host")
    SMTP_PORT: int = Field(587, description="SMTP server port")
    SMTP_USERNAME: str = Field(..., description="SMTP username (your sender email address)")
    SMTP_PASSWORD: str = Field(..., description="SMTP password or app-specific password")
    EMAIL_SENDER_ADDRESS: str = Field(..., description="SMTP sender address")
    EMAIL_SENDER_NAME: str = Field("BarberShop App", description="SMTP name displayed as sender")

    EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES: int = 10
    EMAIL_VERIFICATION_CODE_LENGTH: int = 6

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    REDIS_URL: str = Field("redis://localhost:6379/0", alias="REDIS_URL", description="URL for Redis connection")

    # CORS settings
    # Pydantic-settings
    CORS_ORIGINS_RAW: str = Field(
        "http://localhost,http://localhost:3000,http://192.168.10.188:3000/,http://172.31.48.1:3000/",
        alias="CORS_ORIGINS",
        description="Comma-separated allowed domains for CORS in .env"
    )

    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 15
    FRONTEND_URL: str = "http://localhost:3000"  # for reset send frontend

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """
        Computed property that splits the comma-separated CORS_ORIGINS_RAW into a list of strings.
        Each item is stripped of leading/trailing whitespace.
        """
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    # Configuration for pydantic-settings
    model_config = SettingsConfigDict(
        env_file=".env",
        extra='ignore',  # Ignore extra fields in .env not defined in the class
        case_sensitive=True  # Environment variable names are case-sensitive
    )


settings = Settings()


def get_settings():
    return settings
