from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Serverless backend for managing family Secret Santa draws",
    version="1.0.0"
)

# CORS configuration allowing requests only from configured origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X-Admin-Passcode", "X-Edit-Passcode"],
)

app.include_router(router)

# ASGI Handler for AWS Lambda
handler = Mangum(app)
