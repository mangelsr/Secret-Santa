import os
from typing import List

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def _resolve_smtp_password() -> str:
    direct_password = os.getenv("SMTP_PASSWORD", "")
    if direct_password:
        return direct_password

    param_name = os.getenv("SMTP_PASSWORD_PARAM", "")
    if not param_name:
        return ""

    try:
        ssm = boto3.client("ssm", region_name=os.getenv("AWS_REGION", "us-east-1"))
        response = ssm.get_parameter(Name=param_name, WithDecryption=True)
        return response.get("Parameter", {}).get("Value", "")
    except (BotoCoreError, ClientError):
        return ""


def _parse_allowed_origins(raw: str) -> List[str]:
    origins = [origin.strip().rstrip("/") for origin in raw.split(",") if origin.strip()]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


class Settings:
    PROJECT_NAME: str = "Family Secret Santa API"
    STAGE: str = os.getenv("STAGE", "dev")
    GROUPS_TABLE: str = os.getenv("GROUPS_TABLE", "santa-secreto-groups-dev")
    SES_SENDER_EMAIL: str = os.getenv("SES_SENDER_EMAIL", "notifications@yourdomain.com")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

    # CORS Configuration
    ALLOWED_ORIGINS: List[str] = _parse_allowed_origins(
        os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    )

    # SMTP Configuration (Gmail / SSM Parameter Store)
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = _resolve_smtp_password()
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Santa Secreto 🎅")

    # Passcode Brute-Force Protection
    MAX_PASSCODE_ATTEMPTS: int = int(os.getenv("MAX_PASSCODE_ATTEMPTS", "5"))
    PASSCODE_LOCKOUT_SECONDS: int = int(os.getenv("PASSCODE_LOCKOUT_SECONDS", "900"))


settings = Settings()
