import streamlit as st

def create_full_prompt(prompt, dataset):
    prompt = f"""
        User prompt: {prompt}
        Dataset:{dataset.to_string()}
        Give a clear, short, concise answer without exlanation.
        """
    return prompt

def create_payload(prompt, dataset):
    payload = {
        "model": "llama3.1",
        "prompt": create_full_prompt(prompt, dataset),
        "temperature": st.session_state.get("temperature", 0.2),
        "max_tokens": st.session_state.get("max_tokens", 10),
        "stream": False
    }
    return payload