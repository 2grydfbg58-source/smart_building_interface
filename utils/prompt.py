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

    if hasattr(dataset, "to_string"):
        dataset_context = dataset.to_string()
    elif isinstance(dataset, list):
        dataset_context = "\n".join(str(item) for item in dataset)
    else:
        dataset_context = str(dataset)

    prompt = f"""
        You are a helpful building assistant.
        
        Maintain the conversation context across turns.
        If the user asks a follow-up question, answer based on the previous conversation and the dataset.
        
        Conversation history: {conversation_context}
        Context: {dataset_context}
        Current user request: {prompt}

        Follow these rules:
        1. If user request is a question, answer it directly ONLY from the dataset and keep the response short and concise.
           If you cannot answer it, say "don't know" or "That information is not in the dataset" instead of making up an answer.
           Do not include any extra explanation or context.
        
           Example question:
           Q: What is the temperature in the living room?
           A: The temperature in the living room is 21 C.

        2. If user request is a command to change a parameter, return ONLY a valid JSON object, and no extra explanation.
           Ask for confirmation.
           The JSON must contain:
           - "action": a concise action name such as "set_temperature"
           - "parameter": the parameter name being changed
           - "value": the requested numeric or text value
           - "location": the location or "unknown" if not provided
           - "message": a confirmation prompt for the user

           Example command:
           Set the temperature to 22 C in the living room.
           Example JSON response: {{"action":"set_temperature","parameter":"temperature","value":22,"location":"unknown","message":"Confirm changing temperature to 22 C."}}
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