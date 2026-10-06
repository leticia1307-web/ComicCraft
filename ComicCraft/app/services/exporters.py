from datetime import datetime
from pathlib import Path

from fpdf import FPDF

from app.config import settings


def _safe_text(text: str):

    return (
        text
        .encode(
            "latin-1",
            errors="replace",
        )
        .decode("latin-1")
    )


def save_pdf(
    layout: list[dict],
):

    settings.ensure_directories()

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S-%f"
    )

    output = (
        settings.EXPORTS_DIR
        / f"comiccraft-{timestamp}.pdf"
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=12,
    )

    for panel in layout:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        pdf.multi_cell(
            0,
            10,
            _safe_text(
                f"Panel "
                f"{panel['panel_number']}: "
                f"{panel['title']}"
            ),
        )

        image_path = Path(
            panel["image_path"]
        )

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=20,
                y=35,
                w=170,
            )

        pdf.set_y(210)

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        pdf.multi_cell(
            0,
            6,
            _safe_text(
                panel[
                    "scene_description"
                ]
            ),
        )

        pdf.ln(3)

        pdf.set_font(
            "Helvetica",
            "B",
            11,
        )

        pdf.multi_cell(
            0,
            6,
            _safe_text(
                panel["caption"]
            ),
        )

        pdf.ln(2)

        pdf.set_font(
            "Helvetica",
            size=10,
        )

        pdf.multi_cell(
            0,
            6,
            _safe_text(
                panel["narration"]
            ),
        )

        for dialogue in panel.get(
            "dialogue",
            [],
        ):

            pdf.ln(1)

            pdf.set_font(
                "Helvetica",
                "I",
                10,
            )

            pdf.multi_cell(
                0,
                6,
                _safe_text(dialogue),
            )

    pdf.output(
        str(output)
    )

    return str(output)