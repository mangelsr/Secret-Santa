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

# CORS configuration allowing requests from React SPA
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# ASGI Handler for AWS Lambda
handler = Mangum(app)
