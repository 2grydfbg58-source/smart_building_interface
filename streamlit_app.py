import pandas as pd
import streamlit as st
from utils.llm import get_response, get_model_api_url
from utils.helper import get_dataset_path
from utils.prompt import create_payload

# Title and description
st.title("Prototype")
st.write("This is my first Streamlit app!")

# Layout for dataset ingestion
col1 = st.columns(1)

with col1[0]:
    if st.button("Ingest Dataset"):
        try:
            csv_path = get_dataset_path()
            st.session_state["df"] = pd.read_csv(csv_path)
            st.session_state["response"] = ""
            st.success("Dataset ingested successfully!")
        except FileNotFoundError:
            st.error("Dataset file not found. Please check the path and try again.")

# Display dataset preview if available
if "df" in st.session_state:
    st.subheader("Dataset Preview")
    st.dataframe(st.session_state["df"])

# Show instructions when dataset is missing
if "df" not in st.session_state:
    st.info("Please ingest the dataset first to enable question entry.")

# Callback to submit prompt when Enter is pressed
def ask_question():
    dataset = st.session_state.get("df")
    prompt = st.session_state.get("user_prompt", "").strip()

    if dataset is None:
        st.session_state["response"] = "Please ingest the dataset first."
        return

    if not prompt:
        st.session_state["response"] = "Please enter a prompt and press Enter."
        return

    url, error_message = get_model_api_url()

    if error_message:
        st.session_state["response"] = error_message
        return
    
    payload = create_payload(prompt, dataset)

    with loading_placeholder.container():
        with st.spinner("Generating response..."):
            st.session_state["response"] = get_response(url, payload)

# Add slider for model temperature
st.session_state["temperature"] = st.slider(
    "Model Temperature",
    min_value=0.0,
    max_value=1.0,
    value=st.session_state.get("temperature", 0.2),
    step=0.01,
    help="Controls randomness: 0 = deterministic, 1 = very creative"
)

# Add slider for max tokens
st.session_state["max_tokens"] = st.slider(
    "Max Tokens",
    min_value=1,
    max_value=1000,
    value=st.session_state.get("max_tokens", 10),
    step=1
)

# Placeholder for loading feedback under the controls
loading_placeholder = st.empty()

# Add text input for user prompt with enter submission
st.text_input(
    "Enter your prompt:",
    key="user_prompt",
    disabled=("df" not in st.session_state),
    on_change=ask_question,
    placeholder="Type your question and press Enter to submit"
)

# Display response after question submission
if st.session_state.get("response"):
    st.subheader("Response")
    st.write(st.session_state["response"])
