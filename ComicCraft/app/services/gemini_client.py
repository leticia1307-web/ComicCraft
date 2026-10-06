import os
import time

from dotenv import load_dotenv
from google import genai


load_dotenv()


_client = None


def get_gemini_client():
    global _client

    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is missing in .env"
            )

        _client = genai.Client(api_key=api_key)

    return _client


def retry_request(request_function, retries=3, delay=5):
    last_error = None

    for attempt in range(retries):
        try:
            return request_function()

        except Exception as exc:
            last_error = exc

            error_text = str(exc)

            if (
                "503" not in error_text
                and "UNAVAILABLE" not in error_text
                and "high demand" not in error_text
            ):
                raise

            if attempt < retries - 1:
                time.sleep(delay)

    raise last_error