# middlewares/cors.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.config import settings


def setup_cors(app: FastAPI):
    CORS_ALLOW = settings.CORS_ALLOW
    origins = [origin.strip() for origin in CORS_ALLOW.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
