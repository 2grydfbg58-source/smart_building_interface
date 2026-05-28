import pandas as pd
import streamlit as st
from utils.llm import get_response, get_model_api_url
from utils.helper import get_dataset_path
from utils.prompt import create_payload


st.set_page_config(page_title="Smart Building Assistant", layout="wide")

st.title("Smart Building Assistant")
st.write(
    "Ingest the dataset, then chat with the assistant."
)


if "conversation" not in st.session_state:
    st.session_state["conversation"] = []
if "pending_action" not in st.session_state:
    st.session_state["pending_action"] = None
if "confirmation_status" not in st.session_state:
    st.session_state["confirmation_status"] = ""
if "temperature" not in st.session_state:
    st.session_state["temperature"] = 0.2
if "max_tokens" not in st.session_state:
    st.session_state["max_tokens"] = 100


with st.sidebar:
    st.subheader("Controls")
    if st.button("Ingest Dataset"):
        try:
            csv_path = get_dataset_path()
            st.session_state["df"] = pd.read_csv(csv_path)
            st.session_state["conversation"] = []
            st.session_state["pending_action"] = None
            st.session_state["confirmation_status"] = ""
            st.success("Dataset ingested successfully!")
        except FileNotFoundError:
            st.error("Dataset file not found. Please check the path and try again.")

    if st.button("Clear conversation"):
        st.session_state["conversation"] = []
        st.session_state["pending_action"] = None
        st.session_state["confirmation_status"] = "Conversation cleared."

    st.slider(
        "Model Temperature",
        min_value=0.0,
        max_value=1.0,
        value=st.session_state["temperature"],
        step=0.01,
        help="Controls randomness: 0 = deterministic, 1 = very creative",
        key="temperature"
    )
    st.slider(
        "Max Tokens",
        min_value=1,
        max_value=1000,
        value=st.session_state["max_tokens"],
        step=1,
        key="max_tokens"
    )


if "df" in st.session_state:
    st.subheader("Dataset Preview")
    st.dataframe(st.session_state["df"])
else:
    st.info("Please ingest the dataset first to enable chat.")


def append_message(role, content):
    st.session_state["conversation"].append({"role": role, "content": content})


def handle_turn(prompt):
    dataset = st.session_state.get("df")
    if dataset is None:
        st.session_state["confirmation_status"] = "Please ingest the dataset first."
        return

    prompt = prompt.strip()
    if not prompt:
        st.session_state["confirmation_status"] = "Please enter a prompt before sending."
        return

    confirmation_keywords = {"yes", "confirm", "approve", "proceed"}
    cancel_keywords = {"no", "cancel", "reject", "abort"}

    if st.session_state["pending_action"] and prompt.lower() in confirmation_keywords:
        action = st.session_state["pending_action"]
        action_summary = (
            f"Confirmed action: {action.get('action', 'control_action')} "
            f"with value {action.get('value')} {action.get('unit') or ''} "
            f"for {action.get('location', 'unknown')}."
        )
        append_message("assistant", action_summary)
        st.session_state["pending_action"] = None
        st.session_state["confirmation_status"] = action_summary
        return

    if st.session_state["pending_action"] and prompt.lower() in cancel_keywords:
        cancel_summary = "Action cancelled. You can issue a new command or ask another question."
        append_message("assistant", cancel_summary)
        st.session_state["pending_action"] = None
        st.session_state["confirmation_status"] = cancel_summary
        return

    append_message("user", prompt)
    st.session_state["confirmation_status"] = ""

    url, error_message = get_model_api_url()
    if error_message:
        append_message("assistant", error_message)
        st.session_state["pending_action"] = None
        return

    history = [
        message for message in st.session_state["conversation"][:-1]
    ]

    payload = create_payload(prompt, dataset, conversation_history=history)

    with st.spinner("Generating response..."):
        response = get_response(url, payload)

    append_message("assistant", response)
    if isinstance(response, dict):
        st.session_state["pending_action"] = response
    else:
        st.session_state["pending_action"] = None


user_input = st.chat_input("Ask a question or issue a command", disabled=("df" not in st.session_state))
if user_input:
    handle_turn(user_input)


for message in st.session_state["conversation"]:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role):
        if isinstance(content, dict):
            st.json(content)
            if content.get("confirmation_required"):
                st.caption(content.get("message", "Review the proposed action and confirm or cancel."))
        else:
            st.write(content)


if st.session_state["pending_action"]:
    pending_action = st.session_state["pending_action"]
    st.info(pending_action.get("message", "Review the proposed action and respond with confirmation."))


if st.session_state["confirmation_status"]:
    st.success(st.session_state["confirmation_status"])
