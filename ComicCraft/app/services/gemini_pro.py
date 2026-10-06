import json

from google.genai import types

from app.config import settings
from app.schemas import (
    OutlineResponse,
    PromptRequest,
    StoryResponse,
)
from app.services.gemini_client import (
    get_gemini_client,
    retry_request,
)


def _fallback_story(
    request: PromptRequest,
    outline: OutlineResponse,
):
    panels = []

    for panel in outline.panels:
        panels.append({
            "panel_number": panel.panel_number,
            "title": panel.title,
            "caption": (
                f"{request.character_name} faces a new challenge "
                f"in {request.setting}."
            ),
            "narration": (
                f"{panel.scene_description} "
                f"The scene carries a {request.tone} mood, "
                f"as {request.character_name} pushes forward "
                f"through the unfolding adventure."
            ),
            "dialogue": [
                f"{request.character_name}: "
                f"This is the moment that matters most.",
                "Narrator: The adventure reaches a turning point.",
            ],
        })

    return StoryResponse(panels=panels)


def generate_story(
    request: PromptRequest,
    outline: OutlineResponse,
):
    if not settings.GEMINI_API_KEY:
        return _fallback_story(request, outline)

    prompt = f"""
Write a 5-panel comic story based on this outline.

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

Outline:
{outline.model_dump_json(indent=2)}

Requirements:
- Return exactly 5 story panels.
- Each panel must match the provided outline sequence.
- Keep the writing family-friendly and cinematic.
- For each panel provide:
  - panel_number
  - title
  - caption
  - narration
  - dialogue (array of strings)
- The dialogue should feel natural and short.
"""

    def make_request():
        return (
            get_gemini_client()
            .models
            .generate_content(
                model=settings.GEMINI_STORY_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=StoryResponse,
                    max_output_tokens=4000,
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
            return _fallback_story(request, outline)

        raise

    if getattr(response, "parsed", None):
        return response.parsed

    try:
        return StoryResponse.model_validate(
            json.loads(response.text)
        )
    except Exception:
        return _fallback_story(request, outline)
