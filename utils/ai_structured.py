"""
Helpers for JSON-only Gemini/Groq responses and graceful fallback parsing.
"""

import base64
import json
import os

import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "llama-3.2-90b-vision-preview")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_GEMINI_VISION_MODEL = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")


def _strip_json_wrappers(raw_text: str) -> str:
    """Strip markdown fences and surrounding whitespace from model output."""
    text = (raw_text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    if "{" in text and "}" in text:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start:end + 1]
    return text


def _parse_json_output(raw_text: str):
    return json.loads(_strip_json_wrappers(raw_text))


def _post_chat_completion(payload: dict):
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Groq API key is not configured")

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=45
    )
    if not response.ok:
        detail = response.text[:500]
        raise RuntimeError(f"Groq request failed ({response.status_code}): {detail}")
    return response.json()


def _post_gemini_generate_content(model: str, payload: dict):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Gemini API key is not configured")

    response = requests.post(
        f"{GEMINI_API_URL}/{model}:generateContent",
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=45
    )
    if not response.ok:
        detail = response.text[:500]
        raise RuntimeError(f"Gemini request failed ({response.status_code}): {detail}")
    return response.json()


def groq_json_vision(system_prompt: str, user_prompt: str, image_bytes: bytes, mime_type: str):
    """Send an image plus text prompt to Groq and parse JSON output."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = f"data:{mime_type};base64,{image_b64}"

    payload = {
        "model": DEFAULT_VISION_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    try:
        raw_text = _post_chat_completion(payload)["choices"][0]["message"]["content"]
        return _parse_json_output(raw_text)
    except Exception:
        payload.pop("response_format", None)
        payload["messages"][1]["content"][0]["text"] = (
            f"{user_prompt}\n\nReturn pure JSON only. No markdown fences."
        )
        raw_text = _post_chat_completion(payload)["choices"][0]["message"]["content"]
        return _parse_json_output(raw_text)


def gemini_json_vision(system_prompt: str, user_prompt: str, image_bytes: bytes, mime_type: str):
    """Send an image plus text prompt to Gemini and parse JSON output."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "systemInstruction": {
            "parts": [
                {"text": system_prompt}
            ]
        },
        "contents": [
            {
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": image_b64
                        }
                    },
                    {
                        "text": user_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json"
        }
    }

    response_json = _post_gemini_generate_content(DEFAULT_GEMINI_VISION_MODEL, payload)
    raw_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_json_output(raw_text)


def gemini_nutrition_vision(image_bytes: bytes, mime_type: str):
    """Use a stricter NutriScan-style Gemini nutrition schema."""
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": image_b64
                        }
                    },
                    {
                        "text": (
                            "Analyze this food image and provide realistic nutrition values. "
                            "Return JSON only."
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "foodName": {"type": "STRING"},
                    "estimatedPortion": {"type": "STRING"},
                    "calories": {"type": "NUMBER"},
                    "protein": {"type": "STRING"},
                    "carbs": {"type": "STRING"},
                    "fats": {"type": "STRING"},
                    "sugar": {"type": "STRING"},
                    "confidenceLevel": {
                        "type": "STRING",
                        "enum": ["High", "Medium", "Low"]
                    },
                    "ingredients": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"}
                    }
                },
                "required": [
                    "foodName",
                    "estimatedPortion",
                    "calories",
                    "protein",
                    "carbs",
                    "fats",
                    "sugar",
                    "confidenceLevel",
                    "ingredients"
                ]
            }
        },
        "systemInstruction": {
            "parts": [
                {
                    "text": (
                        "Act as an advanced food recognition and nutrition estimation AI. "
                        "Analyze the food image and provide the MOST REALISTIC and SCIENTIFICALLY GROUNDED nutrition values. "
                        "Identify the exact food item specifically. "
                        "Estimate portion size in grams based on visual clues like plate size, hand comparison, packaging, or number of pieces. "
                        "Use real-world nutrition knowledge and do not invent exaggerated values. "
                        "Calories must match portion size realistically. "
                        "Protein must not be exaggerated. "
                        "Carbs, fats, and sugar must align with the food type. "
                        "If uncertain, provide a reasonable estimate with lower confidence."
                    )
                }
            ]
        }
    }

    response_json = _post_gemini_generate_content(DEFAULT_GEMINI_VISION_MODEL, payload)
    raw_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_json_output(raw_text)
