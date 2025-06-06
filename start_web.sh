#!/bin/bash
# Convenience script to start the Streamlit web application with UV

echo "🌐 Starting MCP Web Application (Streamlit) with UV..."
echo "Make sure UV is installed and the project is synchronized."
echo ""

# Ensure environment is synced
uv sync

echo "The application will be available at:"
echo "  Local URL: http://localhost:8505"
echo "  Network URL: http://$(hostname -I | awk '{print $1}'):8505"
echo ""

echo "🚀 Launching Streamlit application..."
uv run streamlit run scripts/streamlit.py --server.port 8505 