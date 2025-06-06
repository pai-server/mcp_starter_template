"""Módulo de ejemplo para una herramienta de FastMCP.

Este módulo contiene una herramienta simple que genera un saludo.
"""
from fastmcp import FastMCP

mcp = FastMCP(
    name="ExampleTool", 
    instructions="This is a simple example tool."
)

@mcp.tool
def saludar(nombre: str):
    """Genera un saludo personalizado para el nombre proporcionado.

    Args:
        nombre (str): El nombre de la persona a saludar.

    Returns:
        str: Un saludo en formato de cadena de texto.
    """
    return f"Hola, {nombre}!"


def run_server():
    """Inicializa y ejecuta el servidor FastMCP.

    Esta función pone en marcha el servidor, haciéndolo disponible
    para recibir peticiones y ejecutar las herramientas definidas.
    """
    mcp.run()

if __name__ == "__main__":
    run_server()
