"""LLM client integration for MCP."""

import logging
from typing import Any, Dict, List, Optional
import json

from anthropic import Anthropic, APIError


class LLMClient:
    """Client for interacting with Anthropic's Claude API."""

    def __init__(self, api_key: str) -> None:
        self.client = Anthropic(api_key=api_key)

    def _estimate_token_count(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, int]:
        """Estimate token count for a request to the Claude API using tiktoken."""
        try:
            import tiktoken
        except ImportError:
            logging.warning("tiktoken not installed. Cannot estimate token count. Run 'pip install tiktoken'")
            return {}

        encoding = tiktoken.get_encoding("cl100k_base")
        
        token_counts = {
            "system_prompt": 0,
            "tools": 0,
            "messages": 0,
        }

        if system_prompt:
            token_counts["system_prompt"] = len(encoding.encode(system_prompt))

        if tools:
            token_counts["tools"] = len(encoding.encode(json.dumps(tools)))

        messages_tokens = 0
        for message in messages:
            if message.get("role"):
                messages_tokens += len(encoding.encode(message["role"]))
            
            content = message.get("content")
            if isinstance(content, str):
                messages_tokens += len(encoding.encode(content))
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "text" and item.get("text"):
                        messages_tokens += len(encoding.encode(item["text"]))
                    elif item.get("type") == "tool_use":
                        messages_tokens += len(encoding.encode(item.get("name", "")))
                        messages_tokens += len(encoding.encode(json.dumps(item.get("input", {}))))
                    elif item.get("type") == "tool_result" and item.get("content"):
                        messages_tokens += len(encoding.encode(json.dumps(item.get("content"))))
        
        token_counts["messages"] = messages_tokens
        token_counts["total"] = sum(token_counts.values())

        return token_counts

    def get_response(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> Any:
        """Get response from Claude API.

        Args:
            messages: List of conversation messages.
            tools: Optional list of available tools.
            system_prompt: Optional system prompt.

        Returns:
            Claude API response.

        Raises:
            APIError: If API call fails.
        """
        try:
            # Estimate and log token count before sending
            token_estimates = self._estimate_token_count(messages, tools, system_prompt)
            if token_estimates:
                logging.info("="*20 + " Request Token Estimates " + "="*20)
                logging.info(f"Total estimated INPUT tokens: {token_estimates['total']}")
                logging.info(f"  - System Prompt:      {token_estimates['system_prompt']} tokens")
                logging.info(f"  - Tools Definition:   {token_estimates['tools']} tokens")
                logging.info(f"  - Messages History:   {token_estimates['messages']} tokens")
                logging.info("="*57)

            kwargs = {
                "model": "claude-3-5-haiku-latest",
                "max_tokens": 4096,
                "messages": messages,
            }

            if tools:
                kwargs["tools"] = tools

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            if response.usage:
                logging.info("="*20 + " Actual Token Usage " + "="*24)
                logging.info(f"Actual INPUT tokens:  {response.usage.input_tokens}")
                logging.info(f"Actual OUTPUT tokens: {response.usage.output_tokens}")
                logging.info("="*57)

            return response

        except APIError as e:
            logging.error(f"Error calling Anthropic API: {e}")
            raise


class StreamlitLLMClient(LLMClient):
    """Streamlit-specific LLM client with additional UI integration."""

    def get_response_with_streaming(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None,
    ) -> Any:
        """Get response with potential streaming support.
        
        Note: This is a placeholder for future streaming implementation.
        """
        return self.get_response(messages, tools, system_prompt) 