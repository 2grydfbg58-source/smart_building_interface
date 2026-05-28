import json
import streamlit as st


def build_conversation_context(conversation_history=None):
    conversation_history = conversation_history or []
    if not conversation_history:
        return "No prior conversation."

    lines = ["Previous conversation:"]
    for turn in conversation_history:
        role = turn.get("role", "unknown").capitalize()
        content = turn.get("content")
        if isinstance(content, (dict, list)):
            content = json.dumps(content)
        lines.append(f"{role}: {content}")

    return "\n".join(lines)


def create_full_prompt(prompt, dataset, conversation_history=None):
    conversation_context = build_conversation_context(conversation_history)
    prompt = f"""
        You are a helpful building assistant for a smart building interface.
        Maintain the conversation context across turns.
        If the user asks a follow-up question, answer based on the previous conversation and the dataset.
        If the user issues a control command, return ONLY a valid JSON object asking for confirmation.

        {conversation_context}

        Dataset:
        {dataset.to_string()}

        Current user request: {prompt}

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


def create_payload(prompt, dataset, conversation_history=None):
    payload = {
        "model": "llama3.1",
        "prompt": create_full_prompt(prompt, dataset, conversation_history=conversation_history),
        "user_prompt": prompt,
        "temperature": st.session_state.get("temperature", 0.2),
        "max_tokens": st.session_state.get("max_tokens", 100),
        "stream": False
    }
    return payload