"""Configuration management for MCP client."""

import json
import os
from typing import Any, Dict

from dotenv import load_dotenv


class ConfigurationManager:
    """Manages configuration and environment variables for the MCP client."""

    def __init__(self) -> None:
        """Initialize configuration with environment variables."""
        self.load_env()
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.google_maps_key_from_env = os.getenv("GOOGLE_MAPS_API_KEY")
        self.tavily_key_from_env = os.getenv("TAVILY_API_KEY")

    @staticmethod
    def load_env() -> None:
        """Load environment variables from .env file."""
        load_dotenv()

    @staticmethod
    def load_servers_config(file_path: str = "config/servers.json") -> Dict[str, Any]:
        """Load server configuration from JSON file.

        Args:
            file_path: Path to the JSON configuration file.

        Returns:
            Dict containing server configuration.

        Raises:
            FileNotFoundError: If configuration file doesn't exist.
            JSONDecodeError: If configuration file is invalid JSON.
        """
        with open(file_path, "r") as f:
            return json.load(f)

    @property
    def anthropic_api_key(self) -> str:
        """Get the Anthropic API key.

        Returns:
            The API key as a string.

        Raises:
            ValueError: If the API key is not found in environment variables.
        """
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        return self.api_key

    @property
    def google_maps_api_key(self) -> str | None:
        """Get the Google Maps API key from environment variables."""
        return self.google_maps_key_from_env

    @property
    def tavily_api_key(self) -> str | None:
        """Get the Tavily API key from environment variables."""
        return self.tavily_key_from_env 