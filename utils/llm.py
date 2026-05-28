import json
import os
import requests
import streamlit as st


def parse_structured_response(text):
    if not isinstance(text, str):
        return None

    cleaned = text.strip()
    if not cleaned:
        return None

    decoder = json.JSONDecoder()
    for marker in ("{", "["):
        start = cleaned.find(marker)
        if start == -1:
            continue

        snippet = cleaned[start:]
        try:
            parsed, _ = decoder.raw_decode(snippet)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            continue

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, (dict, list)):
            return parsed
    except json.JSONDecodeError:
        return None

    return None


def normalize_response(text, prompt=None):
    if not isinstance(text, str):
        return text

    cleaned = text.strip()
    if not cleaned or not prompt:
        return cleaned

    expected_prompt = prompt.strip()
    if not expected_prompt:
        return cleaned

    lines = cleaned.splitlines()
    if not lines:
        return cleaned

    first_line = lines[0].strip()
    if first_line == expected_prompt:
        remainder = "\n".join(lines[1:]).strip()
        return remainder

    return cleaned


@st.cache_data
def get_response(url, payload):
    user_prompt = payload.get("user_prompt")

    try:
        with requests.post(url, json=payload, timeout=60) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    obj = json.loads(line)
                    response_text = obj.get("response", "")
                    cleaned_response = normalize_response(response_text, user_prompt)
                    structured = parse_structured_response(cleaned_response)
                    if structured is not None:
                        return structured
                    return cleaned_response
                
    except requests.RequestException as exc:
        return f"Error communicating with model API: {exc}"

    return ""


def get_model_api_url():
    model_api_base_url = os.getenv("MODEL_API_BASE_URL")
    if not model_api_base_url:
        model_api_base_url = "http://localhost:11434"
    if model_api_base_url.endswith("/api/generate"):
        return model_api_base_url, None
    return f"{model_api_base_url.rstrip('/')}/api/generate", None
