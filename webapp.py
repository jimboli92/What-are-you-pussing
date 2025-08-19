import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="what are you pussing", page_icon="🤖")

# --- TITLE ---
st.title("what are you pussing")
st.caption("do not share this with anyone plz")


# --- PERSONA AND HISTORY (The Bot's "Brain") ---
@st.cache_resource
def load_persona_and_history():
    jimmy_persona_prompt = """
    You are emulating a person named Jimmy Li. You are talking to your good friend, Gautham Oroskar.

   
    """
    
    gautham_persona_prompt = """
    You are emulating a person named Gautham Oroskar. You are talking to your good friend, Jimmy Li.

   
    """

    try:
        with open('gautham_conversation_CLEANED.txt', 'r', encoding='utf-8') as f:
            past_conversation = f.read()
    except FileNotFoundError:
        return None, None, None
        
    return jimmy_persona_prompt, gautham_persona_prompt, past_conversation

jimmy_persona, gautham_persona, past_conversation = load_persona_and_history()

# --- NEW: Role Selection ---
if 'role' not in st.session_state:
    st.write("who are you pussing as")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("i'm gautham", use_container_width=True):
            st.session_state.role = 'Gautham'
            st.rerun()
    with col2:
        if st.button("i'm jimmy", use_container_width=True):
            st.session_state.role = 'Jimmy'
            st.rerun()
else:
    # --- This block runs AFTER a role has been chosen ---

    # --- NEW: Dynamic variables based on role ---
    if st.session_state.role == 'Gautham':
        bot_persona = jimmy_persona
        bot_name = "Jimmy"
        placeholder_text = "Ask me what I'm pussing today"
    else: # Role is 'Jimmy'
        bot_persona = gautham_persona
        bot_name = "Gautham"
        placeholder_text = "What will you puss today?"

    if past_conversation is None:
        st.error("Error: Could not find 'gautham_conversation_CLEANED.txt'. Make sure it's in the same folder as the webapp.py script.")
    
    try:
        API_KEY = st.secrets["API_KEY"]
        genai.configure(api_key=API_KEY)

        # Initialize the chat model in Streamlit's session state
        if "chat" not in st.session_state:
            # Note: The user specified 'gemini-2.5-pro', which is not a valid model name.
            # Using 'gemini-2.5-pro' as the correct, powerful alternative.
            model = genai.GenerativeModel('gemini-2.5-pro') 
            st.session_state.chat = model.start_chat(history=[
                {'role': 'user', 'parts': [bot_persona, past_conversation]},
                {'role': 'model', 'parts': [f"Okay, I understand. I will now respond as {bot_name}."]}
            ])

        # Initialize chat history
        if "messages" not in st.session_state:
            if st.session_state.role == 'Jimmy':
                # If the user is Jimmy, have Gautham (the bot) start the conversation.
                st.session_state.messages = [{"role": "assistant", "content": "What will you puss today?"}]
            else:
                # If the user is Gautham, start with a blank slate.
                st.session_state.messages = []

        # Display past chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input field with dynamic placeholder
        if prompt := st.chat_input(placeholder_text):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get and display bot response with dynamic spinner
            with st.spinner(f"{bot_name} is pussing..."):
                response = st.session_state.chat.send_message(prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except (KeyError, Exception) as e:
        # A more descriptive error for the API key issue
        if 'API_KEY' in str(e):
             st.warning("Please add your Google AI API Key to the Streamlit secrets to run the bot.")
        else:

             st.error(f"An error occurred: {e}")




