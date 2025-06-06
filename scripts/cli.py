#!/usr/bin/env python3
"""CLI entry point for MCP client."""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logging_config import setup_logging
from interfaces.cli.app import CLIApp


async def main():
    """Main entry point for CLI application."""
    setup_logging()
    
    app = CLIApp()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 