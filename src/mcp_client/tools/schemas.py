"""MCP Tool schemas and definitions."""

from typing import Any, Dict


class MCPTool:
    """Represents an MCP tool with its properties and formatting."""

    def __init__(
        self, name: str, description: str, input_schema: Dict[str, Any]
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.input_schema: Dict[str, Any] = input_schema

    def __str__(self) -> str:
        return f"Tool: {self.name}\nDescription: {self.description}"

    def format_for_llm(self) -> str:
        """Format tool information for LLM consumption.

        Returns:
            A formatted string describing the tool.
        """
        return (
            f"**{self.name}**\n"
            f"Description: {self.description}\n"
            f"Input Schema: {self.input_schema}\n"
        )

    def get_anthropic_schema(self) -> Dict[str, Any]:
        """Get tool schema in Anthropic format.

        Returns:
            Dictionary with tool schema for Anthropic API.
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
        } 