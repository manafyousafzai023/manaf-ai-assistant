import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Always read the .env that sits next to this file
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))


def _load_keys():
    """Reads GEMINI_KEY_1, GEMINI_KEY_2, ... (also GEMINI_API_KEYS / GEMINI_API_KEY / GOOGLE_API_KEY)."""
    keys = []
    for name in sorted(os.environ):
        if name.startswith("GEMINI_KEY") or name in ("GEMINI_API_KEYS", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
            keys.extend(v.strip() for v in os.environ[name].split(",") if v.strip())
    return list(dict.fromkeys(keys))


API_KEYS = _load_keys()


def generate_gemini_response(
    prompt: str,
    preferred_model: str = "gemini-3.8-flash",
    file_bytes=None,
    mime_type=None,
) -> str:
    """Tries each model and key in order until one works."""
    valid_keys = [k for k in API_KEYS if k and "YOUR_" not in k]

    if not valid_keys:
        return "❌ Error: No API keys found. Add GEMINI_KEY_1=your_key to your .env file."

    # If a file (image/PDF) is uploaded, send it together with the text
    contents = prompt
    if file_bytes:
        contents = [
            types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
            prompt,
        ]

    models_to_try = list(dict.fromkeys(
        [preferred_model, "gemini-3.8-flash", "gemini-3.5-flash-lite"]
    ))
    last_error = None

    for model_name in models_to_try:
        for index, key in enumerate(valid_keys):
            try:
                client = genai.Client(api_key=key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                )
                return response.text
            except Exception as e:
                last_error = e
                print(f"⚠️ {model_name} / key #{index + 1} failed: {e}")
                time.sleep(1)
                continue

    return f"❌ All models failed. Last error: {last_error}"