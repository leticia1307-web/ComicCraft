from pathlib import Path

from app.schemas import (
    OutlineResponse,
    StoryResponse,
)


def build_comic_layout(
    outline: OutlineResponse,
    story: StoryResponse,
    image_paths: list[str],
):

    story_by_panel = {
        panel.panel_number: panel
        for panel in story.panels
    }

    layout = []

    for (
        outline_panel,
        image_path,
    ) in zip(
        outline.panels,
        image_paths,
    ):

        story_panel = story_by_panel.get(
            outline_panel.panel_number
        )

        if story_panel is None:

            raise ValueError(
                f"Missing story panel "
                f"{outline_panel.panel_number}"
            )

        image_path = str(
            Path(image_path).resolve()
        )

        if not Path(image_path).exists():

            raise FileNotFoundError(
                image_path
            )

        layout.append(
            {
                "panel_number": (
                    outline_panel.panel_number
                ),
                "title": story_panel.title,
                "scene_description": (
                    outline_panel.scene_description
                ),
                "image_prompt": (
                    outline_panel.image_prompt
                ),
                "image_path": image_path,
                "image_url": (
                    "/static/panels/"
                    + Path(image_path).name
                ),
                "caption": story_panel.caption,
                "narration": story_panel.narration,
                "dialogue": story_panel.dialogue,
            }
        )

    return layout