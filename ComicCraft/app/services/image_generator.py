import base64

from PIL import Image

from app.config import settings
from app.services.gemini_client import get_gemini_client


IMAGE_MODEL = "gemini-3.1-flash-image"


def _save_image(image_bytes: bytes, panel_number: int) -> str:
    settings.ensure_directories()

    output_path = (
        settings.PANELS_DIR
        / f"panel_{panel_number}.jpg"
    )

    output_path.write_bytes(image_bytes)

    with Image.open(output_path) as image:
        image.verify()

    return str(output_path)


def _fallback_image(panel_number: int) -> str:
    settings.ensure_directories()

    output_path = (
        settings.PANELS_DIR
        / f"panel_{panel_number}.png"
    )

    image = Image.new(
        "RGB",
        (
            settings.IMAGE_WIDTH,
            settings.IMAGE_HEIGHT,
        ),
        (235, 240, 255),
    )

    image.save(output_path)

    return str(output_path)


def _build_comic_prompt(prompt: str) -> str:
    return f"""
Create a finished comic-book illustration for one panel.

Scene:
{prompt}

Visual requirements:
- colorful professional comic-book artwork
- vibrant harmonious colors
- cinematic lighting
- expressive character
- dynamic composition
- detailed environment
- polished graphic-novel quality
- strong foreground, middle ground, and background
- clear focal point
- rich blue, cyan, purple, orange, and yellow accents
- family-friendly
- consistent character appearance
- no written words
- no captions
- no speech bubbles
- no watermark
- no placeholder-looking graphics
"""


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    if (
        settings.IMAGE_PROVIDER != "gemini"
        or not settings.GEMINI_API_KEY
    ):
        return _fallback_image(panel_number)

    comic_prompt = _build_comic_prompt(prompt)

    try:
        client = get_gemini_client()

        interaction = client.interactions.create(
            model=IMAGE_MODEL,
            input=comic_prompt,
            response_format={
                "type": "image",
                "mime_type": "image/jpeg",
                "aspect_ratio": "4:3",
                "image_size": "1K",
            },
        )

        output_image = getattr(
            interaction,
            "output_image",
            None,
        )

        if output_image is None:
            print(
                f"No image returned for panel {panel_number}."
            )
            return _fallback_image(panel_number)

        image_data = getattr(
            output_image,
            "data",
            None,
        )

        if not image_data:
            print(
                f"Empty image data for panel {panel_number}."
            )
            return _fallback_image(panel_number)

        if isinstance(image_data, str):
            image_bytes = base64.b64decode(image_data)
        else:
            image_bytes = image_data

        return _save_image(
            image_bytes,
            panel_number,
        )

    except Exception as exc:
        error_text = str(exc)

        if (
            "429" in error_text
            or "Too Many Requests" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "quota" in error_text.lower()
        ):
            print(
                f"Gemini image rate limit reached for "
                f"panel {panel_number}. "
                "Using fallback image."
            )
            return _fallback_image(panel_number)

        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text
            or "high demand" in error_text.lower()
        ):
            print(
                f"Gemini image service temporarily "
                f"unavailable for panel {panel_number}. "
                "Using fallback image."
            )
            return _fallback_image(panel_number)

        print(
            f"Image generation failed for panel "
            f"{panel_number}: {exc}"
        )

        return _fallback_image(panel_number)