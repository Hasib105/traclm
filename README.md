# LLM Tracer 🚀

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet.svg)](https://docs.astral.sh/uv/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A **LangSmith-like** observability platform for LangChain and LangGraph applications. Self-hosted, open-source, and easy to deploy.

## ✨ Features

- **🔍 Full LLM Observability** - Track all LLM calls, inputs, outputs, token usage, and latency
- **🛠️ Tool Call Tracking** - Monitor tool/function calls with inputs, outputs, and errors
- **📊 Beautiful Dashboard** - Waterfall view of traces with detailed inspection
- **🔑 API Key Management** - Secure authentication for your applications
- **📁 Project Organization** - Organize traces by project
- **🚀 Auto-Instrumentation** - Just call `init()` and all LangChain calls are traced automatically (like Sentry!)
- **💾 Self-Hosted** - Full control over your data
- **🐘 PostgreSQL + SQLite** - Production PostgreSQL with SQLite fallback for development

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Application                          │
│  ┌─────────────┐    ┌─────────────────────┐                     │
│  │  LangChain  │◀───│   llm_tracer_sdk    │                     │
│  │     LLM     │    │  (auto-instrument)  │                     │
│  └─────────────┘    └──────────┬──────────┘                     │
└────────────────────────────────┼────────────────────────────────┘
                                 │ HTTP/API (async background)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                       LLM Tracer Server                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   FastAPI   │───▶│   Piccolo   │───▶│  PostgreSQL │         │
│  │     API     │    │     ORM     │    │  / SQLite   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│  ┌─────────────────────────────────────────────────────┐       │
│  │                    Web Dashboard                     │       │
│  │   • Traces List  • Trace Detail  • Projects/Keys   │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
llm-tracer/
├── src/
│   ├── llm_tracer/          # Main server application
│   │   ├── api/             # FastAPI routes and schemas
│   │   ├── db/              # Database models and migrations
│   │   ├── templates/       # Jinja2 HTML templates
│   │   ├── config.py        # Application configuration
│   │   └── main.py          # FastAPI app entry point
│   └── llm_tracer_sdk/      # Client SDK for instrumentation
│       ├── callback.py      # LangChain callback handler
│       ├── client.py        # HTTP client for API
│       ├── context.py       # Trace context management
│       ├── instrumentation.py
│       └── sdk.py           # Main SDK interface
├── tests/                   # Test suite
├── examples/                # Usage examples
├── pyproject.toml           # Project configuration (uv/hatch)
├── piccolo_conf.py          # Piccolo ORM configuration
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### 1. Install uv (if not already installed)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-tracer.git
cd llm-tracer

# Create virtual environment and install dependencies
uv sync

# Install with development dependencies
uv sync --all-extras
```

### 3. Configure Database

```bash
# SQLite (default, no config needed)
# Just run the server!

# PostgreSQL (production)
export DATABASE_URL="postgresql://user:password@localhost:5432/llm_tracer"
# Or use individual variables:
export POSTGRES_HOST="localhost"
export POSTGRES_PORT="5432"
export POSTGRES_USER="user"
export POSTGRES_PASSWORD="password"
export POSTGRES_DB="llm_tracer"
```

### 4. Run the Server

```bash
# Using uv run
uv run llm-tracer

# Or with uvicorn directly
uv run uvicorn llm_tracer.main:app --reload --host 0.0.0.0 --port 8000

# Or using the Python module
uv run python -m llm_tracer.main
```

The server will be available at `http://localhost:8000`

### 5. Create a Project and API Key

1. Open `http://localhost:8000` in your browser
2. Go to **Projects** → Create a new project
3. Go to **API Keys** → Create an API key for your project
4. **Copy the API key** (it's shown only once!)

### 6. Integrate the SDK

```bash
# Install the SDK in your project
uv add llm-tracer[sdk]
# or with pip
pip install llm-tracer[sdk]
```

```python
import llm_tracer_sdk

# Initialize once at startup - that's it!
llm_tracer_sdk.init(
    api_key="lt-your-api-key",
    endpoint="http://localhost:8000"
)

# All LangChain calls are now automatically traced!
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini")
response = llm.invoke("Hello!")  # <-- Automatically traced!
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_api.py -v
```

### Linting & Formatting

```bash
# Check code with ruff
uv run ruff check src tests

# Fix auto-fixable issues
uv run ruff check --fix src tests

# Format code
uv run ruff format src tests

# Type checking with mypy
uv run mypy src
```

### Pre-commit Hooks

```bash
# Install pre-commit hooks
uv run pre-commit install

# Run on all files
uv run pre-commit run --all-files
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Full database URL | `sqlite:///./llm_tracer.db` |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_USER` | PostgreSQL username | - |
| `POSTGRES_PASSWORD` | PostgreSQL password | - |
| `POSTGRES_DB` | PostgreSQL database | `llm_tracer` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `SECRET_KEY` | Secret key for security | `change-me-in-production` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:8000` |

### SDK Configuration

```python
import llm_tracer_sdk

llm_tracer_sdk.init(
    api_key="lt-your-api-key",      # Required
    endpoint="http://localhost:8000", # Server URL
    debug=True,                       # Enable debug logging
)

# Set user/session context
llm_tracer_sdk.set_user("user-123")
llm_tracer_sdk.set_session("session-456")
llm_tracer_sdk.set_tags(["production", "v2"])
llm_tracer_sdk.set_metadata({"environment": "prod"})
```

## 📝 Examples

See the [examples/](examples/) directory for complete usage examples:

- `basic_usage.py` - Basic auto-instrumentation
- More examples coming soon!

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [LangSmith](https://smith.langchain.com/)
- Built with [FastAPI](https://fastapi.tiangolo.com/), [Piccolo ORM](https://piccolo-orm.com/), and [LangChain](https://langchain.com/)
- Package management by [uv](https://docs.astral.sh/uv/)
