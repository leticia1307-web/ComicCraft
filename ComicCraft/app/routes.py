from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Query,
    Request,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)
from fastapi.templating import (
    Jinja2Templates,
)

from app.config import settings
from app.schemas import PromptRequest
from app.services.exporters import save_pdf
from app.services.gemini_flash import (
    generate_outline,
)
from app.services.gemini_pro import (
    generate_story,
)
from app.services.image_generator import (
    generate_image,
)
from app.services.layout_builder import (
    build_comic_layout,
)


router = APIRouter()


templates = Jinja2Templates(
    directory=str(
        settings.TEMPLATES_DIR
    )
)


def _validate_form(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
):

    return PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )


def _generate_comic(
    request_data: PromptRequest,
):

    # Step 1
    outline = generate_outline(
        request_data
    )

    # Step 2
    story = generate_story(
        request_data,
        outline,
    )

    # Step 3
    image_paths = []

    for panel in outline.panels:

        image_path = generate_image(
            panel.image_prompt,
            panel.panel_number,
        )

        image_paths.append(
            image_path
        )

    # Step 4
    layout = build_comic_layout(
        outline,
        story,
        image_paths,
    )

    # Step 5
    pdf_path = save_pdf(
        layout
    )

    return layout, pdf_path


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
def generate(
    request: Request,

    story_prompt: Annotated[
        str,
        Form(),
    ],

    character_name: Annotated[
        str,
        Form(),
    ],

    setting: Annotated[
        str,
        Form(),
    ],

    tone: Annotated[
        str,
        Form(),
    ],

    art_style: Annotated[
        str,
        Form(),
    ],
):

    try:

        data = _validate_form(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
        )

        layout, pdf_path = (
            _generate_comic(data)
        )

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "layout": layout,
                "pdf_url": (
                    "/exports/"
                    + Path(pdf_path).name
                ),
            },
        )

    except Exception as exc:

        if settings.DEBUG:
            detail = str(exc)
        else:
            detail = (
                "Comic generation failed. "
                "Check server logs."
            )

        raise HTTPException(
            status_code=500,
            detail=detail,
        ) from exc


@router.post(
    "/generate-comic/json"
)
def generate_comic_json(
    payload: PromptRequest,
):

    try:

        layout, pdf_path = (
            _generate_comic(payload)
        )

        return {
            "success": True,
            "layout": layout,
            "pdf_path": (
                "/exports/"
                + Path(pdf_path).name
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/test-image"
)
def test_image(
    prompt: str = Query(
        default=(
            "a friendly fox "
            "in an enchanted forest"
        )
    ),
):

    try:

        image_path = generate_image(
            prompt,
            panel_number=0,
        )

        return {
            "success": True,
            "image_url": (
                "/static/panels/"
                + Path(image_path).name
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/exports/{filename}"
)
def download_export(
    filename: str,
):

    if (
        Path(filename).name
        != filename
    ):

        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    path = (
        settings.EXPORTS_DIR
        / filename
    )

    if (
        not path.exists()
        or path.suffix.lower()
        != ".pdf"
    ):

        raise HTTPException(
            status_code=404,
            detail="Export not found.",
        )

    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=path.name,
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
def export_success(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={},
    )