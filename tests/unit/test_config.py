"""Unit tests for configuration management."""

import json
import os
import tempfile
import unittest
from unittest.mock import patch

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from mcp_client.config.manager import ConfigurationManager


class TestConfigurationManager(unittest.TestCase):
    """Test cases for ConfigurationManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = ConfigurationManager()

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_api_key"})
    def test_anthropic_api_key_from_env(self):
        """Test getting Anthropic API key from environment."""
        config = ConfigurationManager()
        self.assertEqual(config.anthropic_api_key, "test_api_key")

    @patch.dict(os.environ, {}, clear=True)
    def test_anthropic_api_key_missing(self):
        """Test error when Anthropic API key is missing."""
        config = ConfigurationManager()
        with self.assertRaises(ValueError):
            _ = config.anthropic_api_key

    @patch.dict(os.environ, {"GOOGLE_MAPS_API_KEY": "test_maps_key"})
    def test_google_maps_api_key(self):
        """Test getting Google Maps API key from environment."""
        config = ConfigurationManager()
        self.assertEqual(config.google_maps_api_key, "test_maps_key")

    @patch.dict(os.environ, {}, clear=True)
    def test_google_maps_api_key_missing(self):
        """Test Google Maps API key returns None when missing."""
        config = ConfigurationManager()
        self.assertIsNone(config.google_maps_api_key)

    def test_load_servers_config(self):
        """Test loading servers configuration from JSON file."""
        # Create a temporary config file
        test_config = {
            "mcpServers": {
                "test_server": {
                    "command": "test_command",
                    "args": ["arg1", "arg2"]
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_config, f)
            temp_file = f.name
        
        try:
            loaded_config = ConfigurationManager.load_servers_config(temp_file)
            self.assertEqual(loaded_config, test_config)
        finally:
            os.unlink(temp_file)

    def test_load_servers_config_file_not_found(self):
        """Test error when config file doesn't exist."""
        with self.assertRaises(FileNotFoundError):
            ConfigurationManager.load_servers_config("nonexistent_file.json")


if __name__ == "__main__":
    unittest.main() 