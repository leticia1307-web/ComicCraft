import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings:

    APP_NAME = os.getenv(
        "APP_NAME",
        "ComicCraft",
    )

    DEBUG = (
        os.getenv(
            "DEBUG",
            "true",
        ).lower()
        == "true"
    )

    # ---------------------------------------------------------
    # Gemini
    # ---------------------------------------------------------

    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY",
        "",
    ).strip()

    GEMINI_OUTLINE_MODEL = os.getenv(
        "GEMINI_OUTLINE_MODEL",
        "gemini-3.8-flash",
    )

    GEMINI_STORY_MODEL = os.getenv(
        "GEMINI_STORY_MODEL",
        "gemini-3.8-flash",
    )

    # ---------------------------------------------------------
    # Image generation
    # ---------------------------------------------------------

    IMAGE_PROVIDER = os.getenv(
        "IMAGE_PROVIDER",
        "placeholder",
    ).lower()

    DIFFUSION_MODEL_ID = os.getenv(
        "DIFFUSION_MODEL_ID",
        "stable-diffusion-v1-5/stable-diffusion-v1-5",
    )

    HF_API_KEY = os.getenv(
        "HF_API_KEY",
        "",
    ).strip()

    IMAGE_WIDTH = int(
        os.getenv(
            "IMAGE_WIDTH",
            "512",
        )
    )

    IMAGE_HEIGHT = int(
        os.getenv(
            "IMAGE_HEIGHT",
            "512",
        )
    )

    IMAGE_STEPS = int(
        os.getenv(
            "IMAGE_STEPS",
            "20",
        )
    )

    IMAGE_GUIDANCE = float(
        os.getenv(
            "IMAGE_GUIDANCE",
            "7.5",
        )
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    MAX_PROMPT_LENGTH = int(
        os.getenv(
            "MAX_PROMPT_LENGTH",
            "2000",
        )
    )

    # ---------------------------------------------------------
    # Directories
    # ---------------------------------------------------------

    TEMPLATES_DIR = BASE_DIR / "templates"

    STATIC_DIR = BASE_DIR / "static"

    PANELS_DIR = STATIC_DIR / "panels"

    EXPORTS_DIR = STATIC_DIR / "exports"

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @property
    def gemini_configured(self):
        return bool(self.GEMINI_API_KEY)

    def ensure_directories(self):

        self.STATIC_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.PANELS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.EXPORTS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )


settings = Settings()