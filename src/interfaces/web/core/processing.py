"""Handles LLM response processing and tool calls for the Streamlit app."""

import streamlit as st
from datetime import datetime
from typing import Any, Dict

from utils.logging_config import get_logger
from .session_state import SessionManager

logger = get_logger(__name__)


def execute_tool_call(tool_name: str, tool_input: Dict[str, Any]):
    """Execute a tool call."""
    try:
        result = st.session_state.server_registry.execute_tool_sync(tool_name, tool_input)

        # Log tool execution
        st.session_state.tool_execution_log.append({
            "tool": tool_name,
            "input": tool_input,
            "result": str(result)[:200] + "..." if len(str(result)) > 200 else str(result),
            "timestamp": datetime.now().isoformat()
        })

        return result
    except Exception as e:
        logger.error(f"Error executing tool {tool_name}: {e}")
        return f"Error: {e}"


def process_llm_response(response, placeholder_for_live_update):
    """Process LLM response and handle tool calls."""
    assistant_content = []
    tool_results = []

    # Process response content
    for content in response.content:
        if content.type == "text":
            assistant_content.append({"type": "text", "text": content.text})
            with placeholder_for_live_update.container():
                st.markdown(content.text)

        elif content.type == "tool_use":
            assistant_content.append({
                "type": "tool_use",
                "id": content.id,
                "name": content.name,
                "input": content.input
            })

            # Execute tool
            with placeholder_for_live_update.container():
                with st.status(f"🛠️ Executing {content.name}...", expanded=True) as status:
                    st.json(content.input)

                    result = execute_tool_call(content.name, content.input)
                    status.update(label=f"✅ {content.name} completed", state="complete")

            # Format tool result
            if hasattr(result, 'content') and isinstance(result.content, list):
                text_parts = []
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        text_parts.append(content_item.text)
                    else:
                        text_parts.append(str(content_item))
                result_text = " ".join(text_parts) if text_parts else str(result)
            else:
                result_text = str(result)

            # Truncate very long results
            if len(result_text) > 10000:
                result_text = result_text[:1000] + f"... [Content truncated, original length: {len(result_text)}]"

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": content.id,
                "content": result_text
            })

    # Add assistant message
    if assistant_content:
        SessionManager.add_message("assistant", assistant_content)

    # If we have tool results, continue the conversation
    if tool_results:
        SessionManager.add_message("user", tool_results, "tool_result")

        # Get follow-up response
        tools_schema = [tool.get_anthropic_schema() for tool in st.session_state.available_tools]

        # Clean messages before sending to API
        clean_messages = st.session_state.chat_session.clean_messages_for_api(st.session_state.messages)

        with st.spinner("🤔 Processing results..."):
            follow_up_response = st.session_state.llm_client.get_response(
                clean_messages,
                tools=tools_schema,
                system_prompt="You are a helpful assistant. Use tools when appropriate."
            )

        # Process follow-up response (recursively)
        process_llm_response(follow_up_response, placeholder_for_live_update) 