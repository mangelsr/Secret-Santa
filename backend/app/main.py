from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend Serverless para gestión del sorteo de Santa Secreto Familiar",
    version="1.0.0"
)

# Configuración CORS para permitir peticiones desde la SPA React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción se puede restringir al dominio de Cloudflare
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Handler ASGI para AWS Lambda
handler = Mangum(app)
