"""Streamlit chat UI components."""

import streamlit as st


def display_chat_history():
    """Display the chat history."""
    if "display_messages" in st.session_state:
        for msg in st.session_state.display_messages:
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                with st.chat_message("user"):
                    st.markdown(content)
            elif role == "assistant":
                with st.chat_message("assistant"):
                    if isinstance(content, str):
                        st.markdown(content)
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get("type") == "text":
                                st.markdown(item.get("text", "")) 