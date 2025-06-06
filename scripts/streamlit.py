#!/usr/bin/env python3
"""Streamlit entry point for MCP client."""

import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logging_config import setup_logging

def main():
    """Main entry point for Streamlit application."""
    setup_logging()
    
    # Import streamlit app after path setup
    from interfaces.web.app import main as streamlit_main
    streamlit_main()


if __name__ == "__main__":
    main() 