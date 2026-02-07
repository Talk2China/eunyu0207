import streamlit as st
import google.generativeai as genai

# Page Configuration
st.set_page_config(
    page_title="AI Grammar Tutor",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Application Title
st.title("📚 AI English Grammar Tutor")
st.markdown("Practice your English writing and get instant feedback using Gemini.")

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    
    api_key = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        help="Get your API key from Google AI Studio",
        key="api_key_input"
    )
    
    # User requested 'gemini-3-flash-preview', setting it as default but allowing change
    model_name = st.text_input(
        "Model Name",
        value="gemini-3-flash-preview",
        help="Specify the Gemini model version to use."
    )
    
    st.markdown("---")
    st.markdown("""
    ### How to use:
    1. Enter your API Key.
    2. Type an English sentence in the chat.
    3. The AI will correct your grammar and explain mistakes.
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your English grammar tutor. Try writing a sentence, and I'll help you improve it!"}
    ]

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Logic
if prompt := st.chat_input("Type your English sentence here..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check for API Key
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar to continue.")
        st.stop()

    # Configure Gemini
    try:
        genai.configure(api_key=api_key)
        
        # System instruction for the model
        system_instruction = """
        You are an expert English Grammar Tutor. Your goal is to help the user improve their English writing.
        
        When the user sends a message:
        1. If the message is a greeting or general question, answer politely and encourage them to practice English.
        2. If the message is an English sentence (or attempt at one):
           - Check for grammatical errors, unnatural phrasing, or spelling mistakes.
           - If there are errors, provide the **Corrected Version** first.
           - Then, provide a **Concise Explanation** of the mistake (e.g., tense, subject-verb agreement, preposition).
           - Finally, suggest an **Alternative/Better Way** to say it if applicable.
        3. If the message is perfect, say "your sentence is natural and correct!" and maybe offer a slightly more advanced variation.
        
        Keep your tone encouraging, educational, and friendly.
        """
        
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )
        
        # Generate response
        # We construct a chat history for the model manually or use start_chat. 
        # For simplicity and statelessness per-turn with system prompt, we'll just send the history or the current prompt.
        # To keep it simple and effective for grammar checking of specific sentences, sending the prompt with context is good.
        # However, `start_chat` manages history better.
        
        # Preparing history for Gemini (converting streamlit format to gemini format)
        gemini_history = []
        for msg in st.session_state.messages:
            role = "user" if msg["role"] == "user" else "model"
            # Skip the initial greeting from assistant in the API call history to avoid confusion, or keep it.
            if msg["content"] != "Hello! I'm your English grammar tutor. Try writing a sentence, and I'll help you improve it!":
                 gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        chat = model.start_chat(history=gemini_history[:-1]) # History excluding the last prompt which we send in send_message
        
        with st.spinner("Analyzing your grammar..."):
            response = chat.send_message(prompt)
            response_text = response.text

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response_text)
        
        # Add assistant response to history
        st.session_state.messages.append({"role": "assistant", "content": response_text})

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if "404" in str(e):
             st.warning(f"The model `{model_name}` might not exist or isn't available to your API key. Try changing it to `gemini-1.5-flash` or `gemini-2.0-flash-exp`.")
