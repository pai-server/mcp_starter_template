#!/usr/bin/env python3
"""
Development utility script with inline dependencies.

This script demonstrates UV's script capabilities with inline dependency metadata.
"""
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich>=13.0.0",
#     "typer>=0.9.0",
# ]
# ///

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import subprocess
import sys
from pathlib import Path

app = typer.Typer(help="🛠️ Development utilities for MCP Agents Starter")
console = Console()

@app.command()
def setup():
    """🚀 Setup development environment with UV."""
    console.print(Panel("🚀 Setting up development environment", style="bold blue"))
    
    commands = [
        "uv sync --dev",
        "uv run pre-commit install",
    ]
    
    for cmd in commands:
        console.print(f"Running: [bold cyan]{cmd}[/bold cyan]")
        result = subprocess.run(cmd.split(), capture_output=True, text=True)
        if result.returncode == 0:
            console.print("✅ Success", style="green")
        else:
            console.print(f"❌ Failed: {result.stderr}", style="red")

@app.command()
def test():
    """🧪 Run tests with pytest."""
    console.print(Panel("🧪 Running tests", style="bold green"))
    subprocess.run(["uv", "run", "pytest", "-v"])

@app.command()
def lint():
    """🔍 Run linting with ruff and black."""
    console.print(Panel("🔍 Running linters", style="bold yellow"))
    
    commands = [
        ["uv", "run", "ruff", "check", "src/", "scripts/", "tests/"],
        ["uv", "run", "black", "--check", "src/", "scripts/", "tests/"],
        ["uv", "run", "mypy", "src/"],
    ]
    
    for cmd in commands:
        console.print(f"Running: [bold cyan]{' '.join(cmd)}[/bold cyan]")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            console.print("❌ Linting failed", style="red")
            sys.exit(1)
    
    console.print("✅ All linting passed!", style="green")

@app.command()
def format_code():
    """🎨 Format code with black and ruff."""
    console.print(Panel("🎨 Formatting code", style="bold magenta"))
    
    subprocess.run(["uv", "run", "ruff", "check", "--fix", "src/", "scripts/", "tests/"])
    subprocess.run(["uv", "run", "black", "src/", "scripts/", "tests/"])
    
    console.print("✅ Code formatted!", style="green")

@app.command()
def start_cli():
    """🖥️ Start the CLI application."""
    console.print(Panel("🖥️ Starting CLI application", style="bold blue"))
    subprocess.run(["uv", "run", "python", "scripts/cli.py"])

@app.command()
def start_web():
    """🌐 Start the web application."""
    console.print(Panel("🌐 Starting web application", style="bold blue"))
    subprocess.run(["uv", "run", "streamlit", "run", "scripts/streamlit.py", "--server.port", "8505"])

@app.command()
def info():
    """ℹ️ Show project information."""
    table = Table(title="📊 MCP Agents Starter Project Info")
    table.add_column("Aspect", style="cyan")
    table.add_column("Details", style="magenta")
    
    table.add_row("Project", "MCP Agents Starter")
    table.add_row("UV Version", subprocess.getoutput("uv --version"))
    table.add_row("Python Version", subprocess.getoutput("uv run python --version"))
    table.add_row("Environment", str(Path(".venv").absolute()) if Path(".venv").exists() else "Not created")
    
    console.print(table)

if __name__ == "__main__":
    app() 