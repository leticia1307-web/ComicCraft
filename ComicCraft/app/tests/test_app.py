import os


# Force the development image provider during tests.
os.environ["IMAGE_PROVIDER"] = "placeholder"

# Prevent tests from requiring a real Gemini request.
os.environ["GEMINI_API_KEY"] = ""


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_homepage():

    response = client.get("/")

    assert response.status_code == 200

    assert "ComicCraft" in response.text


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"


def test_json_generation():

    payload = {

        "story_prompt":
            "A brave fox explores "
            "an enchanted forest.",

        "character_name":
            "Ember",

        "setting":
            "enchanted forest",

        "tone":
            "dramatic",

        "art_style":
            "comic book",
    }

    response = client.post(
        "/generate-comic/json",
        json=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert len(
        data["layout"]
    ) == 5

    assert data[
        "pdf_path"
    ].endswith(".pdf")


def test_image_endpoint():

    response = client.get(
        "/test-image",
        params={
            "prompt":
                "a friendly fox"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data[
        "image_url"
    ].endswith(".png")