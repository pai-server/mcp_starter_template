"""Conversation management for MCP client."""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import TextContent

from .client import LLMClient
from mcp_client.servers.registry import MCPServerRegistry


class ChatSession:
    """Orchestrates the interaction between user, LLM, and MCP tools."""

    def __init__(self, server_registry: MCPServerRegistry, llm_client: LLMClient) -> None:
        self.server_registry = server_registry
        self.llm_client = llm_client
        self.max_messages_to_keep = 10  # Reduced to keep fewer messages in context
        self.conversation_summary = ""  # Store conversation summary
        self.message_count = 0  # Track total messages for periodic summarization

    def clean_messages_for_api(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean messages by removing extra fields that aren't expected by Anthropic API."""
        cleaned_messages = []
        for msg in messages:
            # Only keep 'role' and 'content' fields
            cleaned_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            cleaned_messages.append(cleaned_msg)
        return cleaned_messages

    async def cleanup_servers(self) -> None:
        """Clean up all servers properly."""
        await self.server_registry.cleanup_all()

    async def store_in_memory(self, key: str, value: str) -> None:
        """Store data in memory server if available."""
        try:
            await self.server_registry.execute_tool("store", {"key": key, "value": value})
            logging.info(f"Stored in memory: {key}")
        except Exception as e:
            logging.warning(f"Failed to store in memory: {e}")

    async def retrieve_from_memory(self, key: str) -> Optional[str]:
        """Retrieve data from memory server if available."""
        try:
            result = await self.server_registry.execute_tool("retrieve", {"key": key})
            if isinstance(result.content, list):
                for content_item in result.content:
                    if isinstance(content_item, TextContent):
                        return content_item.text
        except Exception as e:
            logging.warning(f"Failed to retrieve from memory: {e}")
        return None

    async def summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Create a summary of the conversation to reduce tokens."""
        # Extract key points from the conversation
        conversation_text = []
        for msg in messages[-10:]:  # Last 10 messages
            role = msg["role"]
            content = msg.get("content", "")
            if isinstance(content, str):
                conversation_text.append(f"{role}: {content}")
            elif isinstance(content, list):
                text_parts = []
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                if text_parts:
                    conversation_text.append(f"{role}: {' '.join(text_parts)}")
        
        if not conversation_text:
            return ""
        
        # Create a summary prompt
        summary_prompt = f"""Summarize the following conversation in 2-3 sentences, focusing on key information and context:

{chr(10).join(conversation_text)}

Summary:"""
        
        try:
            # Clean messages before sending to API
            clean_messages = self.clean_messages_for_api([{"role": "user", "content": summary_prompt}])
            response = self.llm_client.get_response(
                clean_messages,
                system_prompt="You are a helpful assistant that creates concise summaries."
            )
            if response.content and response.content[0].type == "text":
                return response.content[0].text
        except Exception as e:
            logging.warning(f"Failed to create summary: {e}")
        
        return ""

    def prune_messages_with_summary(self, messages: List[Dict[str, Any]], summary: str = "") -> List[Dict[str, Any]]:
        """Prune messages while maintaining context through summary and keeping tool pairs intact."""
        if len(messages) <= self.max_messages_to_keep:
            return messages
        
        # First, identify tool_use/tool_result pairs that must be kept together
        tool_pairs = []
        for i in range(len(messages) - 1):
            if messages[i]["role"] == "assistant":
                # Check if this assistant message has tool_use blocks
                content = messages[i].get("content", [])
                if isinstance(content, list):
                    has_tool_use = any(
                        isinstance(item, dict) and item.get("type") == "tool_use"
                        for item in content
                    )
                    if has_tool_use and i + 1 < len(messages):
                        # Check if next message is user with tool_result
                        next_content = messages[i + 1].get("content", [])
                        if isinstance(next_content, list) and messages[i + 1]["role"] == "user":
                            has_tool_result = any(
                                isinstance(item, dict) and item.get("type") == "tool_result"
                                for item in content
                            )
                            if has_tool_result:
                                tool_pairs.append((i, i + 1))
        
        # Keep only recent messages, but ensure we don't break tool pairs
        keep_from = max(0, len(messages) - self.max_messages_to_keep)
        
        # Adjust keep_from to not break any tool pairs
        for assistant_idx, user_idx in tool_pairs:
            if assistant_idx < keep_from <= user_idx:
                # We would break this pair, so include both messages
                keep_from = assistant_idx
        
        pruned = messages[keep_from:]
        
        # Ensure we start with a user message (unless it would break a tool pair)
        while pruned and pruned[0]["role"] == "assistant":
            # Check if removing this assistant message would break a tool pair
            first_msg_has_tool_use = False
            content = pruned[0].get("content", [])
            if isinstance(content, list):
                first_msg_has_tool_use = any(
                    isinstance(item, dict) and item.get("type") == "tool_use"
                    for item in content
                )
            
            if first_msg_has_tool_use and len(pruned) > 1 and pruned[1]["role"] == "user":
                # This assistant message has tool_use and next is user (likely with tool_result)
                # Keep both to maintain the pair
                break
            else:
                # Safe to remove this assistant message
                pruned.pop(0)
        
        # If we have a summary and the first message is a user message, prepend context
        if summary and pruned and pruned[0]["role"] == "user":
            # Only modify if it's not a tool_result message
            content = pruned[0].get("content", [])
            is_tool_result = isinstance(content, list) and any(
                isinstance(item, dict) and item.get("type") == "tool_result"
                for item in content
            )
            
            if not is_tool_result:
                if isinstance(content, str):
                    new_content = f"[Previous conversation context: {summary}]\n\n{content}"
                else:
                    new_content = f"[Previous conversation context: {summary}]\n\n{str(content)}"
                
                context_message = {
                    "role": "user",
                    "content": new_content
                }
                pruned[0] = context_message
        
        # Validate that all messages have content
        pruned = [msg for msg in pruned if msg.get("content")]
        
        return pruned

    async def get_system_prompt(self) -> str:
        """Get system prompt for the conversation."""
        return (
            "You are a helpful assistant. Use the available tools when appropriate. "
            "When you use a tool, the system will provide its output. "
            "Based on the tool output, provide a natural language response to the user."
        )

    async def initialize_conversation(self) -> List[Dict[str, Any]]:
        """Initialize a new conversation with context from memory if available."""
        messages: List[Dict[str, Any]] = []
        
        # Try to retrieve previous conversation context from memory
        previous_summary = await self.retrieve_from_memory("conversation_summary")
        if previous_summary:
            logging.info(f"Retrieved previous context: {previous_summary[:100]}...")
            self.conversation_summary = previous_summary
        
        return messages 