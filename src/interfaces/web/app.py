"""Streamlit Web Application for MCP client."""

import streamlit as st
from lmnr import Laminar

from utils.logging_config import setup_logging, get_logger
from src.interfaces.web.core.session_state import SessionManager
from src.interfaces.web.core.initialization import initialize_mcp_components
from src.interfaces.web.core.processing import process_llm_response
from src.interfaces.web.components.sidebar import sidebar_content
from src.interfaces.web.components.chat import display_chat_history

logger = get_logger(__name__)

# Page config
st.set_page_config(
    page_title="PAI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better message styling
st.markdown("""
<style>
    .assistant-thinking {
        background-color: #f0f2f6;
        border-left: 3px solid #4CAF50;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .tool-execution {
        background-color: #e8f4f8;
        border-left: 3px solid #2196F3;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    # Initialize Laminar for tracing
    Laminar.initialize()
    
    # Initialize session state
    SessionManager.initialize()

    # Main content
    st.title("💬 PAI Assistant")
    st.caption("Chat with AI that can use various tools through MCP servers")

    # Sidebar
    sidebar_content()

    # Initialize if needed
    if not st.session_state.initialized:
        if not initialize_mcp_components():
            st.stop()
        st.rerun()

    # Display chat history
    display_chat_history()

    # Chat input
    if user_input := st.chat_input("Type your message here...", disabled=st.session_state.get("is_processing", False)):
        if not st.session_state.is_processing:
            st.session_state.is_processing = True

            # Add user message
            SessionManager.add_message("user", user_input)

            # Display user message immediately
            with st.chat_message("user"):
                st.markdown(user_input)

            # Generate response
            with st.chat_message("assistant"):
                placeholder = st.empty()

                try:
                    tools_schema = [tool.get_anthropic_schema() for tool in st.session_state.available_tools]

                    # Clean messages before sending to API
                    clean_messages = st.session_state.chat_session.clean_messages_for_api(st.session_state.messages)

                    with st.spinner("🤔 Thinking..."):
                        response = st.session_state.llm_client.get_response(
                            clean_messages,
                            tools=tools_schema,
                            system_prompt="You are a helpful assistant. Use tools when appropriate."
                        )

                    # Process response
                    process_llm_response(response, placeholder)

                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    logger.error(f"Error in chat: {e}")

            st.session_state.is_processing = False
            st.rerun()

    # Footer
    st.markdown("---")
    st.caption("Powered by PAI")


if __name__ == "__main__":
    setup_logging()
    main() 