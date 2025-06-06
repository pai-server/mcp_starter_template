"""Manages Streamlit session state."""

import streamlit as st
import atexit
from datetime import datetime
from typing import Any

from ..utils.async_bridge import AsyncBridge


class SessionManager:
    """Manages persistent state in Streamlit session state."""

    @staticmethod
    def initialize():
        """Initialize session state variables."""
        if "initialized" not in st.session_state:
            st.session_state.initialized = False
            st.session_state.messages = []
            st.session_state.display_messages = []  # Separate display messages
            st.session_state.server_registry = None
            st.session_state.llm_client = None
            st.session_state.chat_session = None
            st.session_state.async_bridge = AsyncBridge()
            st.session_state.available_tools = []
            st.session_state.server_status = {}
            st.session_state.is_processing = False
            st.session_state.tool_execution_log = []
            st.session_state.conversation_summary = ""
            st.session_state.message_count = 0
            st.session_state.config = None
            atexit.register(st.session_state.async_bridge.cleanup)

    @staticmethod
    def add_message(role: str, content: Any, message_type: str = "message"):
        """Add a message to the conversation history."""
        # Add to internal messages (for API)
        st.session_state.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Add to display messages (for UI) - only for actual user/assistant messages
        if message_type == "message" and not (role == "user" and isinstance(content, list) and
                                             any(isinstance(item, dict) and item.get("type") == "tool_result"
                                                 for item in content)):
            st.session_state.display_messages.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "type": message_type
            })

    @staticmethod
    def clear_conversation():
        """Clear the conversation history."""
        st.session_state.messages = []
        st.session_state.display_messages = []
        st.session_state.tool_execution_log = []
        st.session_state.conversation_summary = ""
        st.session_state.message_count = 0 