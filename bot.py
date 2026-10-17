from google import genai
from google.genai import types

client = genai.Client()

# System prompts for different personas
PERSONA_PROMPTS = {
    "Default Assistant": "You are a helpful, friendly AI assistant.",
    "Creative Writer": "You are a creative writer. Use expressive, descriptive language and vivid tone.",
    "Code Expert": "You are an expert software developer. Provide clean code snippets, concise explanations, and best practices.",
    "Short & Concise": "You give extremely brief, direct answers without unnecessary filler."
}

def get_streaming_response(messages_history, persona_name="Default Assistant"):
    """
    Accepts full chat history and chosen persona, streaming the reply.
    """
    try:
        # Format Streamlit message history into Gemini Contents objects
        formatted_contents = []
        for msg in messages_history:
            role = "user" if msg["role"] == "user" else "model"
            formatted_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        # Get system prompt for selected persona
        system_prompt = PERSONA_PROMPTS.get(persona_name, PERSONA_PROMPTS["Default Assistant"])

        # Configure request with system instruction
        config = types.GenerateContentConfig(
            system_instruction=system_prompt
        )

        # Stream response from Gemini
        response = client.models.generate_content_stream(
            model="gemini-3-flash-preview",
            contents=formatted_contents,
            config=config
        )

        for chunk in response:
            if chunk.text:
                yield chunk.text

    except Exception as e:
        yield f"Error: {e}"