"""Unit tests for MCP tool schemas."""

import unittest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_client.tools.schemas import MCPTool


class TestMCPTool(unittest.TestCase):
    """Test cases for MCPTool."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool = MCPTool(
            name="test_tool",
            description="A test tool for unit testing",
            input_schema={
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                },
                "required": ["param1"]
            }
        )

    def test_tool_initialization(self):
        """Test tool initialization."""
        self.assertEqual(self.tool.name, "test_tool")
        self.assertEqual(self.tool.description, "A test tool for unit testing")
        self.assertIsInstance(self.tool.input_schema, dict)

    def test_string_representation(self):
        """Test string representation of tool."""
        expected = "Tool: test_tool\nDescription: A test tool for unit testing"
        self.assertEqual(str(self.tool), expected)

    def test_format_for_llm(self):
        """Test formatting tool for LLM consumption."""
        formatted = self.tool.format_for_llm()
        self.assertIn("**test_tool**", formatted)
        self.assertIn("Description: A test tool for unit testing", formatted)
        self.assertIn("Input Schema:", formatted)

    def test_get_anthropic_schema(self):
        """Test getting Anthropic-compatible schema."""
        schema = self.tool.get_anthropic_schema()
        
        expected_schema = {
            "name": "test_tool",
            "description": "A test tool for unit testing",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "integer"}
                },
                "required": ["param1"]
            }
        }
        
        self.assertEqual(schema, expected_schema)

    def test_empty_input_schema(self):
        """Test tool with empty input schema."""
        tool = MCPTool("empty_tool", "Tool with no params", {})
        schema = tool.get_anthropic_schema()
        self.assertEqual(schema["input_schema"], {})


if __name__ == "__main__":
    unittest.main() 