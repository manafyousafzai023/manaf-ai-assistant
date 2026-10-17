import streamlit as st
import google.generativeai as genai
from PIL import Image
import pypdf
from streamlit_mic_recorder import speech_to_text

# Page Setup
st.set_page_config(page_title="Manaf AI Assistant", page_icon="💬", layout="wide")

# Configure Gemini API Key
API_KEY = "YOUR GEMINI KEY"  # Keep your working API key here
genai.configure(api_key=API_KEY)

# Initialize Gemini Model
model = genai.GenerativeModel("gemini-3.5-flash")

# Initialize Chat Memory
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Sidebar: Control Panel
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # File Upload Widget
    uploaded_file = st.file_uploader(
        "Upload Image or PDF", 
        type=["png", "jpg", "jpeg", "pdf"]
    )
    
    # Reliable Voice Input Widget
    st.write("🎙️ **Voice Recording**")
    spoken_text = speech_to_text(
        start_prompt="🎤 Start Recording", 
        stop_prompt="⏹️ Stop Recording", 
        language="en", 
        key="voice_recorder"
    )
    
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()

# Main Header
st.title("💬 Manaf AI Assistant")

# Display Past Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture User Text Input
text_input = st.chat_input("Type your message here...")

# Combine Text or Voice Input
user_prompt = text_input or spoken_text

if user_prompt:
    # Display User Prompt
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # If a file is uploaded, attach it to prompt
            if uploaded_file is not None:
                prompt_parts = []
                file_type = uploaded_file.type

                if "image" in file_type:
                    image = Image.open(uploaded_file)
                    st.image(image, caption="Uploaded Image", use_column_width=True)
                    prompt_parts.append(image)

                elif file_type == "application/pdf":
                    pdf_reader = pypdf.PdfReader(uploaded_file)
                    extracted_text = ""
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() or ""
                    prompt_parts.append(f"PDF Context:\n{extracted_text}")

                prompt_parts.append(user_prompt)
                response = model.generate_content(prompt_parts, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            # Standard Chat Memory Mode
            else:
                response = st.session_state.chat.send_message(user_prompt, stream=True)
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            message_placeholder.markdown(f"**Error:** {str(e)}")