import os

class Settings:
    PROJECT_NAME: str = "Family Secret Santa API"
    STAGE: str = os.getenv("STAGE", "dev")
    GROUPS_TABLE: str = os.getenv("GROUPS_TABLE", "santa-secreto-groups-dev")
    SES_SENDER_EMAIL: str = os.getenv("SES_SENDER_EMAIL", "notifications@yourdomain.com")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    
    # SMTP Configuration (Gmail)
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_FROM_NAME: str = os.getenv("SMTP_FROM_NAME", "Santa Secreto 🎅")

settings = Settings()
