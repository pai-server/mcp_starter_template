"""Streamlit sidebar component."""

import streamlit as st
from ..core.session_state import SessionManager
from ..core.initialization import cleanup_all_resources


def sidebar_content():
    """Render comprehensive sidebar content."""
    with st.sidebar:
        st.header("🤖 PAI Assistant")

        # Server Status
        st.subheader("📡 Server Status")
        if "server_status" in st.session_state:
            for server_name, status in st.session_state.server_status.items():
                st.text(f"{status} {server_name}")

        # Available Tools
        with st.expander("🛠️ Available Tools", expanded=False):
            if "available_tools" in st.session_state and st.session_state.available_tools:
                for tool in st.session_state.available_tools:
                    st.text(f"• {tool.name}")
                    if st.button(f"ℹ️ Info", key=f"info_{tool.name}", help="Show tool description"):
                        st.info(f"**{tool.name}**\n\n{tool.description}")
            else:
                st.text("No tools available")

        # Conversation Stats
        st.subheader("📊 Conversation Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages", len(st.session_state.get("display_messages", [])))
        with col2:
            st.metric("Tool Calls", len(st.session_state.get("tool_execution_log", [])))

        # Actions
        st.subheader("Actions")
        if st.button("🗑️ Clear Conversation"):
            SessionManager.clear_conversation()
            st.rerun()

        if st.button("🔄 Reinitialize Servers"):
            cleanup_all_resources()
            st.rerun()

        # Tool Execution Log
        if "tool_execution_log" in st.session_state and st.session_state.tool_execution_log:
            with st.expander("📝 Recent Tool Executions", expanded=False):
                for log in st.session_state.tool_execution_log[-5:]:  # Show last 5
                    st.text(f"🔧 {log['tool']}")
                    st.caption(f"{log['timestamp'][:19]}")
                    st.text("Input:")
                    st.json(log['input'])
                    st.text(f"Result: {log['result']}")
                    st.divider() 