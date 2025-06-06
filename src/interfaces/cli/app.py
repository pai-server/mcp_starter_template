"""CLI Application for MCP client."""

import logging
from typing import Any, Dict, List

from anthropic import APIError
from lmnr import Laminar
from mcp.types import TextContent, ImageContent, EmbeddedResource

from mcp_client.config.manager import ConfigurationManager
from mcp_client.servers.registry import MCPServerRegistry
from mcp_client.llm.client import LLMClient
from mcp_client.llm.conversation import ChatSession
from utils.logging_config import get_logger

logger = get_logger(__name__)


class CLIApp:
    """CLI Application for MCP client."""

    def __init__(self):
        self.config = ConfigurationManager()
        self.server_registry = None
        self.llm_client = None
        self.chat_session = None

    async def initialize(self) -> bool:
        """Initialize the CLI application."""
        try:
            # Initialize Laminar for tracing
            Laminar.initialize()
            
            # Initialize server registry
            self.server_registry = MCPServerRegistry(self.config)
            
            # Initialize servers
            server_status = await self.server_registry.initialize_servers()
            
            # Check if any servers initialized successfully
            if not any(server_status.values()):
                logger.error("Failed to initialize any MCP servers")
                return False

            # Initialize LLM client
            self.llm_client = LLMClient(self.config.anthropic_api_key)
            
            # Initialize chat session
            self.chat_session = ChatSession(self.server_registry, self.llm_client)
            
            logger.info("CLI application initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize CLI application: {e}")
            return False

    async def run(self):
        """Run the CLI application."""
        if not await self.initialize():
            logger.error("Failed to initialize application. Exiting.")
            return

        logger.info("MCP Chat Client started. Type 'quit' or 'exit' to exit.")
        
        try:
            # Get all available tools
            all_tools = await self.server_registry.get_all_tools()
            all_tools_anthropic_schema = [tool.get_anthropic_schema() for tool in all_tools]
            
            # Get system prompt
            system_prompt = await self.chat_session.get_system_prompt()
            
            # Initialize conversation
            messages = await self.chat_session.initialize_conversation()

            while True:
                try:
                    user_input = input("You: ").strip()
                    if user_input.lower() in ["quit", "exit"]:
                        logger.info("\nExiting...")
                        break

                    messages.append({"role": "user", "content": user_input})

                    # Clean messages before sending to API
                    clean_messages = self.chat_session.clean_messages_for_api(messages)
                    
                    response = self.llm_client.get_response(
                        clean_messages, tools=all_tools_anthropic_schema, system_prompt=system_prompt
                    )

                    await self._process_response(response, messages, all_tools_anthropic_schema, system_prompt)

                except APIError as e:
                    logger.error(f"LLM API Error: {e}. Please check your API key and network.")
                    # If it's a token limit error, try to recover by aggressive pruning
                    if "prompt is too long" in str(e):
                        await self._handle_token_limit_error(messages)
                except KeyboardInterrupt:
                    logger.info("\nExiting...")
                    break

        finally:
            if self.chat_session:
                await self.chat_session.cleanup_servers()

    async def _process_response(
        self, 
        response, 
        messages: List[Dict[str, Any]], 
        tools_schema: List[Dict[str, Any]], 
        system_prompt: str
    ):
        """Process LLM response and handle tool calls."""
        process_response = True
        
        while process_response:
            assistant_content = []
            
            for content in response.content:
                if content.type == "text":
                    logger.info(f"\nAssistant: {content.text}")
                    assistant_content.append({"type": "text", "text": content.text})
                    if len(response.content) == 1:
                        process_response = False
                elif content.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": content.id,
                        "name": content.name,
                        "input": content.input
                    })
                    
            # Only append the assistant message if it has content
            if assistant_content:
                messages.append({"role": "assistant", "content": assistant_content})
            
            # Process any tool calls
            tool_results = await self._execute_tool_calls(response)
            
            # If we have tool results, send them and get another response
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
                
                # Check if we need to summarize before pruning
                self.chat_session.message_count += 1
                if self.chat_session.message_count % 20 == 0:  # Summarize every 20 messages
                    new_summary = await self.chat_session.summarize_conversation(messages)
                    if new_summary:
                        self.chat_session.conversation_summary = new_summary
                        # Store summary in memory
                        await self.chat_session.store_in_memory("conversation_summary", self.chat_session.conversation_summary)
                
                # Prune messages with summary context
                messages = self.chat_session.prune_messages_with_summary(messages, self.chat_session.conversation_summary)
                
                # Clean messages before sending to API
                clean_messages = self.chat_session.clean_messages_for_api(messages)
                
                response = self.llm_client.get_response(
                    clean_messages, tools=tools_schema, system_prompt=system_prompt
                )
                
                # Check if this response is just text (final response)
                if len(response.content) == 1 and response.content[0].type == "text":
                    logger.info(f"\nFinal response: {response.content[0].text}")
                    messages.append({"role": "assistant", "content": [{"type": "text", "text": response.content[0].text}]})
                    process_response = False
            else:
                # No tool calls, we're done processing
                process_response = False

    async def _execute_tool_calls(self, response) -> List[Dict[str, Any]]:
        """Execute tool calls from LLM response."""
        tool_results = []
        
        for content in response.content:
            if content.type == "tool_use":
                tool_name = content.name
                tool_input = content.input
                tool_use_id = content.id
                
                logger.info(f"Executing tool: {tool_name}")
                logger.info(f"With arguments: {tool_input}")
                
                try:
                    result_obj = await self.server_registry.execute_tool(tool_name, tool_input)
                    
                    # Extract text content from result
                    text_parts = []
                    if isinstance(result_obj.content, list):
                        for content_item in result_obj.content:
                            if isinstance(content_item, TextContent):
                                text_parts.append(content_item.text)
                            elif isinstance(content_item, ImageContent):
                                # Handle image content - just indicate an image was returned
                                text_parts.append("[Image content returned]")
                            elif isinstance(content_item, EmbeddedResource):
                                # Handle embedded resources
                                text_parts.append(f"[Resource: {content_item.resource.uri}]")
                            else:
                                text_parts.append(str(content_item))
                    else:
                        text_parts.append(str(result_obj.content))
                    
                    result_text = " ".join(text_parts) if text_parts else ""
                    
                    # Truncate very long results (like base64 images)
                    if len(result_text) > 10000:
                        result_text = result_text[:1000] + f"... [Content truncated, original length: {len(result_text)}]"
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result_text
                    })
                    
                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    logger.error(error_msg)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": error_msg
                    })
        
        return tool_results

    async def _handle_token_limit_error(self, messages: List[Dict[str, Any]]):
        """Handle token limit error by emergency pruning."""
        logger.info("Attempting to recover from token limit error...")
        # Create emergency summary
        emergency_summary = await self.chat_session.summarize_conversation(messages)
        if emergency_summary:
            await self.chat_session.store_in_memory("emergency_summary", emergency_summary)
        
        # Keep only last 5 messages
        messages = messages[-5:]
        
        # Ensure valid message sequence
        while messages and messages[0]["role"] != "user":
            messages.pop(0) 