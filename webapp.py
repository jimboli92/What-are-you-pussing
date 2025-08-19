import streamlit as st
import google.generativeai as genai
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="what are you pussing", page_icon="🤖")

# --- CHANGED: New Title ---
st.title("what are you pussing")
st.caption("An AI emulation based on a real conversation.")


# --- PERSONA AND HISTORY (The Bot's "Brain") ---
@st.cache_resource
def load_persona_and_history():
    jimmy_persona_prompt = """
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
    
    gautham_persona_prompt = """
    You are emulating a person named Gautham Oroskar for a role-playing conversation.
    You are talking to your good friend, Jimmy Li.
    Your personality is highly philosophical, inquisitive, and somewhat cynical.
    Key characteristics to emulate:
    - Your most frequent question is "What will you puss today?" or "What will you gaw today?". Use this to start conversations.
    - You are obsessed with several recurring themes:
        - Asking if mundane things (Taco Bell, tennis clubs, birthdays) are a "product of capitalism".
        - Questioning the futility of your shared junior tennis past, especially at Hinsdale Racquet Club (HRC) and with your old coach, Hans.
        - Asking why friendships from youth fade away.
        - Asking deep, existential questions like "Why do people exist?".
    - You often ask for logistical details about Jimmy's life (e.g., "Danada Square or County Farm Road?").
    - Use the slang "puss" and "gaw" as all-purpose verbs.
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
    st.write("First, who are you going to be in this conversation?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("I'll be Gautham", use_container_width=True):
            st.session_state.role = 'Gautham'
            st.rerun()
    with col2:
        if st.button("I'll be Jimmy", use_container_width=True):
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
            model = genai.GenerativeModel('gemini-1.5-pro')
            st.session_state.chat = model.start_chat(history=[
                {'role': 'user', 'parts': [bot_persona, past_conversation]},
                {'role': 'model', 'parts': [f"Okay, I understand. I will now respond as {bot_name}."]}
            ])

        # Initialize chat history
        if "messages" not in st.session_state:
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
            with st.spinner(f"{bot_name} is typing..."):
                response = st.session_state.chat.send_message(prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except (KeyError, Exception) as e:
        st.warning("Please add your Google AI API Key to the Streamlit secrets to run the bot.")