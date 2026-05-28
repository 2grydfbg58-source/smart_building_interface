import streamlit as st


def create_full_prompt(prompt, dataset):
    prompt = f"""
        You are a helpful building assistant.

        User request: {prompt}
        Dataset: {dataset.to_string()}
        
        Follow these rules:
        1. If user request is a question, answer it directly from the dataset and keep the response short and concise.
            For example question:
            What is the temperature in the living room?
            Example answer: The temperature in the living room is 21 C.   

        2. If user request is a command to change a parameter, return ONLY a valid JSON object and no extra explanation.
           The JSON must contain:
           - "intent": "control"
           - "action": a concise action name such as "set_temperature"
           - "parameter": the parameter name being changed
           - "value": the requested numeric or text value
           - "unit": the unit if provided, otherwise null
           - "location": the location or "unknown" if not provided
           - "confirmation_required": true
           - "message": a confirmation prompt for the user

            Example command:
            Set the temperature to 22 C in the living room.
            Example JSON response: {{"intent":"control","action":"set_temperature","parameter":"temperature","value":22,"unit":"C","location":"unknown","confirmation_required":true,"message":"Confirm changing temperature to 22 C."}}
        """
    return prompt


def create_payload(prompt, dataset):
    payload = {
        "model": "llama3.1",
        "prompt": create_full_prompt(prompt, dataset),
        "temperature": st.session_state.get("temperature", 0.2),
        "max_tokens": st.session_state.get("max_tokens", 100),
        "stream": False
    }
    return payload