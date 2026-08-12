import os

class Settings:
    PROJECT_NAME: str = "Family Secret Santa API"
    STAGE: str = os.getenv("STAGE", "dev")
    GROUPS_TABLE: str = os.getenv("GROUPS_TABLE", "santa-secreto-groups-dev")
    SES_SENDER_EMAIL: str = os.getenv("SES_SENDER_EMAIL", "notifications@yourdomain.com")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")

settings = Settings()
