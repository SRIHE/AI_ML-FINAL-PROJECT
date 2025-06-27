import streamlit as st
import requests
import pandas as pd
import altair as alt
import json
import time

st.set_page_config(page_title="Soul Lifter", layout="wide")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "emotions" not in st.session_state:
    st.session_state.emotions = []

st.title("💜 Soul Lifter – Mental Health Chatbot")
tabs = st.tabs(["💬 Chat", "📊 Dashboard", "📁 Logs"])

# --- TAB 1: Chat ---
with tabs[0]:
    st.subheader("🧠 Talk to Me – I'm Listening")

    # Display previous messages FIRST (so user sees full history)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input box (below the chat)
    user_input = st.chat_input("Type your message...")

    if user_input:
        # Save user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        try:
            # Simulate typing
            with st.chat_message("assistant"):
                typing_placeholder = st.empty()
                for dots in ["", ".", "..", "..."]:
                    typing_placeholder.markdown(f"🤖 Typing{dots}")
                    time.sleep(0.3)

            # Send message to backend
            res = requests.post("http://127.0.0.1:5000/chat", json={"message": user_input})
            data = res.json()
            reply = data.get("response", "Sorry, I didn’t understand.")
            emotion = data.get("emotion", "neutral")

            # Format final reply
            full_reply = f"{reply}  \n\n🧠 *Emotion: `{emotion}`*"
            typing_placeholder.markdown(full_reply)

            # Save bot reply
            st.session_state.messages.append({"role": "assistant", "content": full_reply})
            st.session_state.emotions.append(emotion)

        except Exception as e:
            error_msg = f"⚠️ Backend not responding: {e}"
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            with st.chat_message("assistant"):
                st.markdown(error_msg)

    # Reset Chat button at the bottom
    st.markdown("---")
    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = []
        st.session_state.emotions = []
        try:
            requests.post("http://127.0.0.1:5000/reset")
            st.success("Conversation reset.")
        except Exception as e:
            st.error(f"Backend reset failed: {e}")

# --- TAB 2: Dashboard ---
with tabs[1]:
    st.subheader("📊 Emotion Dashboard")

    if st.session_state.emotions:
        df = pd.DataFrame(st.session_state.emotions, columns=["Emotion"])
        emotion_count = df["Emotion"].value_counts().reset_index()
        emotion_count.columns = ["Emotion", "Count"]

        chart = alt.Chart(emotion_count).mark_bar().encode(
            x=alt.X("Emotion:N", title="Emotion"),
            y=alt.Y("Count:Q", title="Count"),
            color="Emotion:N"
        ).properties(width=500, height=400)

        st.altair_chart(chart, use_container_width=True)
        st.metric("Total Messages", len(st.session_state.messages) // 2)
        st.metric("Unique Emotions", len(set(st.session_state.emotions)))
    else:
        st.info("No data yet. Start chatting!")

# --- TAB 3: Logs ---
with tabs[2]:
    st.subheader("💾 Logs")

    if st.button("💾 Save Chat Log"):
        with open("chat_logs.json", "w") as f:
            json.dump(st.session_state.messages, f, indent=4)
        st.success("Chat log saved to chat_logs.json ✅")
