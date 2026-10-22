import streamlit as st
from gemini_utils import generate_gemini_response

# Page setup
st.set_page_config(
    page_title="Manaf AI Assistant",
    page_icon="💬",
    layout="wide"
)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# =============================================================================
# SIDEBAR / CONTROL PANEL
# =============================================================================
with st.sidebar:
    st.title("⚙️ Control Panel")

    st.subheader("Upload Image or PDF")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["png", "jpg", "jpeg", "pdf"],
        help="200MB per file • PNG, JPG, PDF"
    )
    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")

    st.markdown("---")

    st.subheader("🎙️ Voice Recording")
    if st.button("Start Recording", use_container_width=True):
        st.info("Voice recording triggered...")

    st.markdown("---")

    # Clear Chat History Button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# =============================================================================
# MAIN CHAT INTERFACE
# =============================================================================
st.title("💬 Manaf AI Assistant")

# Render existing chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User prompt input
if prompt := st.chat_input("Type your message here..."):
    # Build the previous conversation (last 10 messages) so the AI remembers
    history_text = ""
    for m in st.session_state.messages[-10:]:
        who = "User" if m["role"] == "user" else "Assistant"
        history_text += f"{who}: {m['content']}\n"

    if history_text:
        full_prompt = (
            f"Previous conversation:\n{history_text}\n"
            f"Now answer the user's latest message.\nUser: {prompt}"
        )
    else:
        full_prompt = prompt

    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get the uploaded file (if any) so it is sent to Gemini
    file_bytes = uploaded_file.getvalue() if uploaded_file else None
    mime_type = uploaded_file.type if uploaded_file else None

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_gemini_response(
                full_prompt,
                file_bytes=file_bytes,
                mime_type=mime_type,
            )
            st.markdown(response)

    # Append assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": response})