from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import router


BASE_DIR = Path(__file__).resolve().parent.parent

settings.ensure_directories()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI Comic Story Creator using Gemini and Stable Diffusion",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=str(settings.STATIC_DIR)),
    name="static",
)


app.include_router(router)


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "image_provider": settings.IMAGE_PROVIDER,
        "gemini_configured": settings.gemini_configured,
    }