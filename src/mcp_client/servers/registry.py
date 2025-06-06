"""MCP Server registry for managing multiple servers."""

import logging
from typing import Dict, List, Any

from .connection import MCPServer, StreamlitMCPServer
from mcp_client.config.manager import ConfigurationManager


class MCPServerRegistry:
    """Registry for managing multiple MCP servers."""

    def __init__(self, config_manager: ConfigurationManager):
        self.config_manager = config_manager
        self.servers: Dict[str, MCPServer] = {}
        self.status: Dict[str, bool] = {}

    async def initialize_servers(self, config_path: str = "config/servers.json") -> Dict[str, bool]:
        """Initialize all servers from configuration.

        Args:
            config_path: Path to servers configuration file.

        Returns:
            Dictionary with server names and their initialization status.
        """
        try:
            server_config = self.config_manager.load_servers_config(config_path)
            servers_data = server_config.get("mcpServers", {})

            # Inject Google Maps API key if available
            self._inject_google_maps_key(servers_data)

            for server_name, server_info in servers_data.items():
                try:
                    server = MCPServer(server_name, server_info)
                    await server.initialize()
                    self.servers[server_name] = server
                    self.status[server_name] = True
                    logging.info(f"Successfully initialized server: {server_name}")
                except Exception as e:
                    logging.error(f"Failed to initialize server {server_name}: {e}")
                    self.status[server_name] = False

            return self.status

        except Exception as e:
            logging.error(f"Error loading server configuration: {e}")
            return {}

    def _inject_google_maps_key(self, servers_data: Dict[str, Any]) -> None:
        """Inject Google Maps API key if available and server is configured."""
        google_maps_key = self.config_manager.google_maps_api_key
        
        if google_maps_key and "google-maps" in servers_data:
            if "env" not in servers_data["google-maps"]:
                servers_data["google-maps"]["env"] = {}
            servers_data["google-maps"]["env"]["GOOGLE_MAPS_API_KEY"] = google_maps_key
            logging.info("Google Maps API key injected into server configuration.")
        elif "google-maps" in servers_data and not google_maps_key:
            logging.warning("GOOGLE_MAPS_API_KEY not found in environment, google-maps server might not work.")

    async def get_all_tools(self) -> List[Any]:
        """Get all tools from all initialized servers.

        Returns:
            List of all available tools across servers.
        """
        all_tools = []
        for server_name, server in self.servers.items():
            if self.status.get(server_name, False):
                try:
                    tools = await server.list_tools()
                    all_tools.extend(tools)
                except Exception as e:
                    logging.error(f"Error getting tools from {server_name}: {e}")

        return all_tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by finding the appropriate server.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.

        Returns:
            Tool execution result.

        Raises:
            ValueError: If tool is not found in any server.
        """
        for server_name, server in self.servers.items():
            if self.status.get(server_name, False):
                try:
                    tools = await server.list_tools()
                    tool_names = [tool.name for tool in tools]
                    if tool_name in tool_names:
                        return await server.execute_tool(tool_name, arguments)
                except Exception as e:
                    logging.error(f"Error checking tools in {server_name}: {e}")

        raise ValueError(f"Tool '{tool_name}' not found in any server")

    async def cleanup_all(self) -> None:
        """Clean up all server connections."""
        for server_name, server in self.servers.items():
            try:
                await server.cleanup()
                logging.info(f"Cleaned up server: {server_name}")
            except Exception as e:
                logging.error(f"Error cleaning up server {server_name}: {e}")

        self.servers.clear()
        self.status.clear()


class StreamlitMCPServerRegistry(MCPServerRegistry):
    """Streamlit-specific server registry with async bridge support."""

    def __init__(self, config_manager: ConfigurationManager, async_bridge):
        super().__init__(config_manager)
        self.async_bridge = async_bridge
        self.servers: Dict[str, StreamlitMCPServer] = {}

    def initialize_servers_sync(self, config_path: str = "config/servers.json") -> Dict[str, bool]:
        """Initialize servers synchronously using async bridge."""
        try:
            server_config = self.config_manager.load_servers_config(config_path)
            servers_data = server_config.get("mcpServers", {})

            # Inject Google Maps API key if available
            self._inject_google_maps_key(servers_data)

            for server_name, server_info in servers_data.items():
                try:
                    server = StreamlitMCPServer(server_name, server_info, self.async_bridge)
                    success = server.initialize_sync()
                    if success:
                        self.servers[server_name] = server
                        self.status[server_name] = True
                        logging.info(f"Successfully initialized server: {server_name}")
                    else:
                        self.status[server_name] = False
                except Exception as e:
                    logging.error(f"Failed to initialize server {server_name}: {e}")
                    self.status[server_name] = False

            return self.status

        except Exception as e:
            logging.error(f"Error loading server configuration: {e}")
            return {}

    def get_all_tools_sync(self) -> List[Any]:
        """Get all tools synchronously using async bridge."""
        return self.async_bridge.run_async(self.get_all_tools())

    def execute_tool_sync(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute tool synchronously using async bridge."""
        return self.async_bridge.run_async(self.execute_tool(tool_name, arguments)) 