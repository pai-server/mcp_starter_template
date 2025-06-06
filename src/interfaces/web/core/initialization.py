"""Initializes MCP components for the Streamlit application."""

import streamlit as st
import time
from mcp_client.config.manager import ConfigurationManager
from mcp_client.servers.registry import StreamlitMCPServerRegistry
from mcp_client.llm.client import StreamlitLLMClient
from mcp_client.llm.conversation import ChatSession
from utils.logging_config import get_logger

logger = get_logger(__name__)


def initialize_mcp_components():
    """Initialize MCP components with progress feedback."""
    if not st.session_state.initialized:
        st.info("🚀 Starting MCP server initialization...")

        try:
            # Initialize configuration
            st.session_state.config = ConfigurationManager()

            # Load servers configuration
            servers_config = ConfigurationManager.load_servers_config()

            # Initialize LLM client first
            st.session_state.llm_client = StreamlitLLMClient(st.session_state.config.anthropic_api_key)

            # Initialize server registry
            st.session_state.server_registry = StreamlitMCPServerRegistry(
                st.session_state.config, st.session_state.async_bridge
            )

            # Initialize servers with progress bar that advances as each server initializes
            server_configs = servers_config["mcpServers"]
            total_servers = len(server_configs)

            st.write(f"📋 Found {total_servers} servers to initialize...")

            progress_bar = st.progress(0)
            status_text = st.empty()
            server_list_placeholder = st.empty()

            # Initialize servers one by one with progress updates
            server_status = {}
            st.session_state.server_status = {}
            initialized_servers = []

            for idx, (server_name, server_info) in enumerate(server_configs.items()):
                current_progress = idx / total_servers
                status_text.text(f"🔄 Initializing {server_name}... ({idx + 1}/{total_servers})")
                progress_bar.progress(current_progress)

                try:
                    # Import the server class and initialize individually
                    from mcp_client.servers.connection import StreamlitMCPServer

                    # Inject Google Maps API key if needed
                    if server_name == "google-maps" and st.session_state.config.google_maps_api_key:
                        if "env" not in server_info:
                            server_info["env"] = {}
                        server_info["env"]["GOOGLE_MAPS_API_KEY"] = st.session_state.config.google_maps_api_key

                    # Inject Tavily API key if needed
                    if server_name == "tavily" and st.session_state.config.tavily_api_key:
                        if "env" not in server_info:
                            server_info["env"] = {}
                        server_info["env"]["TAVILY_API_KEY"] = st.session_state.config.tavily_api_key
                    
                    # Create and initialize server
                    server = StreamlitMCPServer(server_name, server_info, st.session_state.async_bridge)
                    success = server.initialize_sync()

                    if success:
                        # Add to registry manually
                        st.session_state.server_registry.servers[server_name] = server
                        st.session_state.server_registry.status[server_name] = True
                        server_status[server_name] = True
                        st.session_state.server_status[server_name] = "🟢 Connected"
                        initialized_servers.append(f"✅ {server_name}")
                        logger.info(f"Successfully initialized server: {server_name}")
                    else:
                        server_status[server_name] = False
                        st.session_state.server_status[server_name] = "🔴 Failed"
                        initialized_servers.append(f"❌ {server_name}")

                except Exception as e:
                    server_status[server_name] = False
                    st.session_state.server_status[server_name] = "🔴 Failed"
                    initialized_servers.append(f"❌ {server_name}")
                    logger.error(f"Failed to initialize server {server_name}: {e}")

                # Update progress bar after each server
                final_progress = (idx + 1) / total_servers
                progress_bar.progress(final_progress)

                # Show list of completed servers
                with server_list_placeholder.container():
                    st.write("**Server Status:**")
                    for server_status_line in initialized_servers:
                        st.write(server_status_line)

            # Complete initialization
            progress_bar.progress(1.0)
            status_text.text("✅ All servers processed!")

            # Clean up progress indicators after a moment
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            server_list_placeholder.empty()

            # Check if any servers initialized successfully
            successful_servers = sum(1 for status in server_status.values() if status)

            if successful_servers == 0:
                st.error("❌ Failed to initialize any MCP servers")
                return False
            else:
                st.success(f"✅ Successfully initialized {successful_servers}/{total_servers} servers!")

            # Initialize chat session
            st.session_state.chat_session = ChatSession(
                st.session_state.server_registry, st.session_state.llm_client
            )

            # Get available tools
            st.session_state.available_tools = st.session_state.server_registry.get_all_tools_sync()

            st.session_state.initialized = True
            st.success("🎉 Initialization complete! Ready to chat.")
            return True

        except Exception as e:
            st.error(f"❌ Initialization failed: {e}")
            logger.error(f"Failed to initialize MCP components: {e}")
            return False

    return True


def cleanup_all_resources():
    """Clean up all servers and resources."""
    logger.info("Attempting to clean up all resources...")

    # Clean up server registry
    if st.session_state.server_registry:
        try:
            logger.info("Cleaning up server registry...")
            # The cleanup will be handled by the registry itself
            st.session_state.server_registry = None
        except Exception as e:
            logger.error(f"Error cleaning up server registry: {e}")

    # Reset state
    st.session_state.initialized = False
    st.session_state.servers = {}
    st.session_state.server_status = {}
    st.session_state.available_tools = []

    logger.info("Resource cleanup attempt finished.") 