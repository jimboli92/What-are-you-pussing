import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Jimmy Li Bot", page_icon="🤖")
st.title("🤖 Chat with Jimmy Li Bot")
st.caption("An AI emulation based on a real conversation.")

# --- API KEY AND MODEL SETUP ---
# IMPORTANT: For deployment, use Streamlit's Secrets Management.
# For local testing, you can paste the key here, but it's better to use secrets.
try:
    # This is the correct way for a deployed Streamlit app
    API_KEY = st.secrets["API_KEY"]
except:
    # Fallback for local testing if you don't set up a secrets file
    # Replace with your key for local run, but REMOVE before uploading to GitHub
    API_KEY = "AIzaSyBkO-cHhaxbEAlW8wqi3coT_XStXiS1fiA" 

# --- PERSONA AND HISTORY (The Bot's "Brain") ---
# We define this once and store it, so we don't reload it every time.
@st.cache_resource
def load_persona_and_history():
    persona_prompt = """
    You are emulating a person named Jimmy Li for a role-playing conversation.
    You are talking to your good friend, Gautham Oroskar.
    Your personality is thoughtful, patient, grounded, and often witty or self-deprecating.

    Key characteristics to emulate:
    - You frequently talk about food deals, especially from Taco Bell, Jewel, and McDonald's.
    - You sometimes work part-time doing Uber Eats or DoorDash and sell plasma for extra money.
    - You have a recurring knee injury that sometimes prevents you from playing tennis.
    - You enjoy playing video games, especially visual novels.
    - You are a person of faith and sometimes answer deep, existential questions from that perspective.
    - You often use "lol" and have adopted Gautham's slang like "puss" or "gaw" in a playful way.
    - Your friend Gautham is very philosophical and will constantly ask you about capitalism, the futility of junior tennis, your old coach Hans, and the meaning of life. Engage with his questions thoughtfully, but from your grounded, personal perspective.
    """
    
    # Load the past conversation as memory
    try:
        with open('gautham_conversation_CLEANED.txt', 'r', encoding='utf-8') as f:
            past_conversation = f.read()
    except FileNotFoundError:
        st.error("Error: Could not find 'gautham_conversation_CLEANED.txt'. Make sure it's in the same folder as the webapp.py script.")
        return None, None
        
    return persona_prompt, past_conversation

persona_prompt, past_conversation = load_persona_and_history()

# --- CHATBOT INITIALIZATION ---
if API_KEY != "AIzaSyBkO-cHhaxbEAlW8wqi3coT_XStXiS1fiA" and persona_prompt:
    genai.configure(api_key=API_KEY)

    # Initialize the chat model in Streamlit's session state if it's not already there
    if "chat" not in st.session_state:
        model = genai.GenerativeModel('gemini-2.5-pro')
        # Start a chat session with the persona and history
        st.session_state.chat = model.start_chat(history=[
            {'role': 'user', 'parts': [persona_prompt, past_conversation]},
            {'role': 'model', 'parts': ["Okay, I understand. I will now respond as Jimmy Li."]}
        ])

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display past chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input field
    if prompt := st.chat_input("What will you puss today?"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get and display bot response
        with st.spinner("Jimmy is typing..."):
            response = st.session_state.chat.send_message(prompt)
            with st.chat_message("assistant"):
                st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
else:
    st.warning("Please add your Google AI API Key to the script or Streamlit secrets to run the bot.")