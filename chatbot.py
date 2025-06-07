
import streamlit as st
import openai
import os
import json

openai.api_key = "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"  # Replace with your actual API key

st.title("💬 GPT-4o-mini Chat")

# --- Setup ---
CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

# --- Load available chats ---
chat_files = [f for f in os.listdir(CHAT_DIR) if f.endswith(".json")]
chat_titles = [f.replace("chat_", "").replace(".json", "") for f in chat_files]

# --- Sidebar ---
st.sidebar.title("💾 Chat Manager")

# Select existing chat
selected_chat = st.sidebar.selectbox("Select a chat", ["(New Chat)"] + chat_titles)

# New chat name input
if selected_chat == "(New Chat)":
    new_title = st.sidebar.text_input("Enter new chat name")
    if st.sidebar.button("➕ Start New Chat") and new_title:
        filename = f"chat_{new_title}.json"
        st.session_state.chat_file = os.path.join(CHAT_DIR, filename)
        st.session_state.messages = []
        st.rerun()
else:
    filename = f"chat_{selected_chat}.json"
    st.session_state.chat_file = os.path.join(CHAT_DIR, filename)
    # Load chat if not already loaded
    if "messages" not in st.session_state or st.session_state.get("loaded_file") != filename:
        with open(st.session_state.chat_file, "r") as f:
            st.session_state.messages = json.load(f)
        st.session_state.loaded_file = filename

# Download button
if selected_chat != "(New Chat)":
    with open(st.session_state.chat_file, "r") as f:
        content = f.read()
    st.sidebar.download_button("⬇️ Download Chat", content, file_name=filename)

# Delete chat
if selected_chat != "(New Chat)":
    if st.sidebar.button("🗑️ Delete This Chat"):
        os.remove(st.session_state.chat_file)
        st.session_state.clear()
        st.rerun()

# --- Chat display and input ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Say something..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                temperature=0.5,
                max_tokens=1024
            )
            reply = response.choices[0].message.content
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

            # Save chat
            if "chat_file" in st.session_state:
                with open(st.session_state.chat_file, "w") as f:
                    json.dump(st.session_state.messages, f)

        except Exception as e:
            st.error(f"Error: {e}")
