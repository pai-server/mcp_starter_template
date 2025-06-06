#!/bin/bash
# Convenience script to start the CLI application with UV

echo "🚀 Starting MCP CLI Application with UV..."
echo "Make sure UV is installed and the project is synchronized."
echo ""

# Ensure environment is synced
uv sync

echo "🖥️ Launching CLI interface..."
uv run python scripts/cli.py 