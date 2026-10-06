import json

from google.genai import types

from app.config import settings
from app.schemas import (
    OutlineResponse,
    PromptRequest,
)
from app.services.gemini_client import (
    get_gemini_client,
    retry_request,
)


def _fallback_outline(request: PromptRequest):
    beats = [
        (
            "The Beginning",
            "Introduce the hero and the central problem.",
        ),
        (
            "The Discovery",
            "The hero discovers an important clue.",
        ),
        (
            "The Challenge",
            "A major obstacle tests the hero.",
        ),
        (
            "The Turning Point",
            "The hero makes a courageous decision.",
        ),
        (
            "The Finale",
            "The conflict reaches a satisfying conclusion.",
        ),
    ]

    panels = []

    for number, (title, description) in enumerate(
        beats,
        start=1,
    ):
        panels.append({
            "panel_number": number,
            "title": title,
            "scene_description": (
                f"{description} "
                f"Setting: {request.setting}. "
                f"Main character: "
                f"{request.character_name}. "
                f"Tone: {request.tone}."
            ),
            "image_prompt": (
                f"{request.art_style} comic panel, "
                f"{request.character_name} in "
                f"{request.setting}, "
                f"{description.lower()} "
                "cinematic composition, "
                "expressive character, "
                "detailed background, "
                "clear foreground, "
                "high quality, "
                "no text."
            ),
        })

    return OutlineResponse(panels=panels)


def generate_outline(request: PromptRequest):

    if not settings.GEMINI_API_KEY:
        return _fallback_outline(request)

    prompt = f"""
Create a 5-panel comic outline.

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:
- Exactly 5 panels.
- Each panel must move the story forward.
- Keep the story family-friendly.
- Make the scenes visually interesting.
- Provide a useful image prompt for each panel.
- Do not include text inside the generated image prompts.
"""

    def make_request():
        return (
            get_gemini_client()
            .models
            .generate_content(
                model=settings.GEMINI_OUTLINE_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=OutlineResponse,
                    max_output_tokens=3000,
                ),
            )
        )

    try:
        response = retry_request(
            make_request,
            retries=3,
            delay=5,
        )

    except Exception as exc:
        error_text = str(exc)

        if (
            "503" in error_text
            or "UNAVAILABLE" in error_text
            or "429" in error_text
            or "RESOURCE_EXHAUSTED" in error_text
            or "high demand" in error_text
            or "quota" in error_text.lower()
        ):
            return _fallback_outline(request)

        raise

    if getattr(response, "parsed", None):
        return response.parsed

    try:
        return OutlineResponse.model_validate(
            json.loads(response.text)
        )
    except Exception:
        return _fallback_outline(request)