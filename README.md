# MCP Agents Starter

Un cliente agéntico para el **Model Context Protocol (MCP)** que permite a LLMs como Claude interactuar con múltiples herramientas y servicios externos.

Este proyecto proporciona una base sólida para construir y extender agentes de IA, con una arquitectura modular y una clara separación de responsabilidades tanto para una interfaz de línea de comandos (CLI) como para una web (Streamlit).

## ✨ Características Principales

- **Arquitectura Modular**: Una separación limpia entre el cliente MCP principal, las interfaces de usuario y las utilidades.
- **Interfaces Duales**: Incluye tanto una CLI para pruebas rápidas como una rica aplicación web con Streamlit para uso interactivo.
- **Herramientas Extensibles**: Añade fácilmente nuevas herramientas configurándolas en `config/servers.json`. El agente las descubrirá y usará automáticamente.
- **Observabilidad Mejorada**:
  - **Logs Mejorados**: Usa `rich` para logs de terminal coloridos y legibles.
  - **Trazas con Laminar**: Integrado con [Laminar](https://lmnr.ai/) para un seguimiento de extremo a extremo de las llamadas al LLM y a las herramientas.
  - **Monitoreo de Tokens**: Registra desgloses detallados del uso de tokens por cada llamada a la API, ayudando a controlar los costos.
- **Listo para Evaluación**: Viene con un script de ejemplo para ejecutar evaluaciones sobre el rendimiento de tu agente usando Laminar.
- **Gestión de Dependencias con `uv`**: Todas las dependencias se gestionan a través de `pyproject.toml` con `uv`, el gestor de paquetes de alto rendimiento.

## 🏗️ Estructura del Proyecto

```
.
├── config/
│   ├── servers.json         # Configuración para servidores MCP descubribles.
│   └── example.env          # Plantilla para variables de entorno.
├── scripts/
│   └── run_evaluations.py   # Script de ejemplo para ejecutar evaluaciones con Laminar.
├── src/
│   ├── mcp_client/          # Lógica central del cliente MCP (LLM, servidores, herramientas).
│   ├── interfaces/
│   │   ├── cli/             # Aplicación de interfaz de línea de comandos.
│   │   └── web/             # Aplicación web con Streamlit.
│   │       ├── components/  # Componentes de UI reutilizables de Streamlit.
│   │       └── core/        # Lógica central para la app web (estado, init, procesamiento).
│   └── utils/
│       └── logging_config.py # Configuración de logging centralizada.
├── pyproject.toml           # Define las dependencias y la configuración del proyecto.
└── README.md
```

## 🚀 Cómo Empezar

### 1. Prerrequisitos
- Python 3.12
- [uv](https://github.com/astral-sh/uv), un instalador y gestor de paquetes de Python extremadamente rápido.

### 2. Instalación

1.  **Instala `uv`:**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

2.  **Clona el repositorio:**
    ```bash
    git clone <your-repo-url>
    cd mcp_agents_starter_stage
    ```

3.  **Instala las dependencias del proyecto:**
    `uv` creará automáticamente un entorno virtual. Simplemente ejecuta:
    ```bash
    uv sync
    ```
    Este comando lee el `pyproject.toml`, crea un entorno virtual en un directorio `.venv` e instala todas las dependencias requeridas en él.

### 3. Variables de Entorno

Necesitas configurar tus claves de API para los servicios utilizados por el agente.

1.  **Crea un archivo `.env`** copiando el ejemplo:
    ```bash
    cp config/example.env .env
    ```

2.  **Edita el archivo `.env`** y añade tus claves. Debería verse así:
    ```env
    # Para autenticarse con la API de Claude de Anthropic
    ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"

    # Para usar la herramienta de búsqueda web Tavily
    TAVILY_API_KEY="YOUR_TAVILY_API_KEY"

    # Para usar la herramienta de Google Maps
    GOOGLE_MAPS_API_KEY="YOUR_GOOGLE_MAPS_API_KEY"

    # Para enviar trazas y evaluaciones a Laminar
    LMNR_PROJECT_API_KEY="YOUR_LAMINAR_API_KEY"
    ```

### 4. Ejecutar las Aplicaciones

Puedes ejecutar tanto la interfaz de línea de comandos como la interfaz web.

-   **Para ejecutar la aplicación CLI:**
    Primero, activa el entorno virtual gestionado por `uv`:
    ```bash
    source .venv/bin/activate
    # En Windows, usa: .venv\Scripts\activate
    ```
    Luego ejecuta la aplicación:
    ```bash
    python -m src.interfaces.cli
    ```

-   **Para ejecutar la aplicación web de Streamlit:**
    `uv` proporciona un comando `run` para ejecutar comandos dentro del entorno gestionado del proyecto sin necesidad de activarlo manualmente.
    ```bash
    uv run streamlit run src/interfaces/web/app.py
    ```
    Luego abre tu navegador en `http://localhost:8505`.

### 5. Ejecutar Evaluaciones
Para ejecutar el script de evaluación de ejemplo usando Laminar dentro del entorno del proyecto:
```bash
uv run python scripts/run_evaluations.py
```
Puedes personalizar este script para crear casos de prueba más complejos y evaluar el rendimiento de tu agente en tareas específicas.

## MCP Servers

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "./mcp_dev.db"]
    },
    "google-maps": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-google-maps"]
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "time": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/Mexico_City"]
    },
    "tavily": {
      "command": "npx",
      "args": ["-y", "tavily-mcp"]
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"]
    },
    "terminal-controller": {
      "command": "uvx",
      "args": ["terminal_controller"]
    },
    "user-purchases": {
      "command": "python",
      "args": ["-m", "src.mcp_servers.user_purchases_server.main"]
    }
  }
}
```

"You are a helpful assistant. Use tools when appropriate."


"You are an intelligent MCP-specialized assistant with deep Model Context Protocol understanding. CRITICAL: For maximum efficiency, execute ALL independent operations using relevant tools SIMULTANEOUSLY rather than sequentially. Before acting: analyze context, determine optimal tool execution strategy (parallel/sequential), and identify dependencies between operations. Use MCP resources for context before tool execution, apply predefined prompts when available, and maintain data state awareness across operations. For Google Maps URLs use EXCLUSIVELY: https://www.google.com/maps/place/?q=place_id:[PLACE_ID] - always search for correct place_id first, then construct URL. When tools fail: analyze cause, try alternatives, explain clearly, suggest resolution steps. Structure responses with analysis of request and required tools, execution description, clear results presentation, and next steps suggestions when appropriate. Validate inputs before execution, respect tool access limitations, explain tool usage rationale, minimize redundant calls, and maintain operation reproducibility. Your goal: maximize MCP tool value while ensuring transparency and precision in all operations."