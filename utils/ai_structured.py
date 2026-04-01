"""
Helpers for JSON-only Groq responses and graceful fallback parsing.
"""

import base64
import json
import os
from typing import Any

import requests


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_TEXT_MODEL = os.getenv('GROQ_TEXT_MODEL', 'llama3-70b-8192')
DEFAULT_VISION_MODEL = os.getenv('GROQ_VISION_MODEL', 'llama-3.2-90b-vision-preview')


def clean_json_text(raw_text: str) -> str:
    """Strip markdown fences and surrounding whitespace from model output."""
    text = (raw_text or '').strip()
    if text.startswith('```'):
        lines = text.splitlines()
        if lines and lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].startswith('```'):
            lines = lines[:-1]
        text = '\n'.join(lines).strip()
    return text


def parse_json_text(raw_text: str) -> Any:
    """Parse JSON-only model output after stripping fences."""
    return json.loads(clean_json_text(raw_text))


def _request_payload(messages: list, model: str, max_tokens: int, temperature: float) -> dict:
    return {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }


def groq_json_completion(system_prompt: str, user_prompt: str, model: str = None,
                         max_tokens: int = 1200, temperature: float = 0.2) -> Any:
    """Request JSON output from Groq and parse it."""
    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not api_key:
        raise RuntimeError('Groq API key is not configured')

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=_request_payload(messages, model or DEFAULT_TEXT_MODEL, max_tokens, temperature),
        timeout=60
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return parse_json_text(content)


def groq_json_vision(system_prompt: str, user_prompt: str, image_bytes: bytes, mime_type: str,
                     model: str = None, max_tokens: int = 1000, temperature: float = 0.2) -> Any:
    """Send an image plus text prompt to Groq and parse JSON output."""
    api_key = os.getenv('GROQ_API_KEY', '').strip()
    if not api_key:
        raise RuntimeError('Groq API key is not configured')

    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    image_url = f"data:{mime_type};base64,{image_b64}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ]
    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json=_request_payload(messages, model or DEFAULT_VISION_MODEL, max_tokens, temperature),
        timeout=90
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return parse_json_text(content)
