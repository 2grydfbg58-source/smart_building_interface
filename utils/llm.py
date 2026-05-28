import json
import os
import requests
import streamlit as st

@st.cache_data
def get_response(url, payload):
    try:
        with requests.post(url, json=payload, timeout=60) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    obj = json.loads(line)
                    return obj.get("response", "")
    except requests.RequestException as exc:
        return f"Error communicating with model API: {exc}"

def get_model_api_url():
    model_api_base_url = os.getenv("MODEL_API_BASE_URL")
    if not model_api_base_url:
        model_api_base_url = "http://localhost:11434"
    if model_api_base_url.endswith("/api/generate"):
        return model_api_base_url, None
    return f"{model_api_base_url.rstrip('/')}/api/generate", None
