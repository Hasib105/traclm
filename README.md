# LLM Tracer 🚀

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A **LangSmith-like** observability platform for LangChain and LangGraph applications. Self-hosted, open-source, and easy to deploy.

## ✨ Features

- **🔍 Full LLM Observability** - Track all LLM calls, inputs, outputs, token usage, and latency
- **🛠️ Tool Call Tracking** - Monitor tool/function calls with inputs, outputs, and errors
- **📊 Beautiful Dashboard** - React-based waterfall view of traces with detailed inspection
- **🔑 API Key Management** - Secure authentication for your applications
- **📁 Project Organization** - Organize traces by project
- **🚀 Auto-Instrumentation** - Just call `init()` and all LangChain calls are traced automatically (like Sentry!)
- **💾 Self-Hosted** - Full control over your data
- **🐳 Docker Ready** - One command to deploy with Docker Compose
- **🐘 PostgreSQL + SQLite** - Production PostgreSQL with SQLite fallback for development

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Your Application                          │
│  ┌─────────────┐    ┌─────────────────────┐                     │
│  │  LangChain  │◀───│   llm-tracer-sdk    │                     │
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
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                React Dashboard (Vite + Tailwind)            ││
│  │   • Traces List  • Trace Detail  • Projects/Keys           ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Project Structure

```
llm-tracer/
├── packages/
│   ├── llm-tracer/              # Server package (PyPI: llm-tracer)
│   │   └── src/llm_tracer/
│   │       ├── api/v1/          # Versioned REST API
│   │       ├── db/models/       # Database models
│   │       ├── app.py           # FastAPI app factory
│   │       └── config.py        # Settings management
│   └── llm-tracer-sdk/          # SDK package (PyPI: llm-tracer-sdk)
│       └── src/llm_tracer_sdk/
│           ├── callback.py      # LangChain callback handler
│           ├── instrumentation.py # Auto-patching
│           └── sdk.py           # Main interface
├── apps/
│   └── web/                     # React dashboard (Vite + Tailwind)
├── .github/workflows/           # CI/CD (Docker, PyPI, Tests)
├── docker-compose.yml           # Production deployment
├── docker-compose.dev.yml       # Development with SQLite
├── Dockerfile                   # Multi-stage build
└── pyproject.toml               # Workspace configuration
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/llm-tracer.git
cd llm-tracer

# Copy and configure environment
cp .env.example .env
# Edit .env to set SECRET_KEY

# Start with PostgreSQL
docker compose up -d

# Or use the development setup (SQLite)
docker compose -f docker-compose.dev.yml up -d
```

The server will be available at `http://localhost:8000`

### Option 2: Use Pre-built Docker Image

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/yourusername/llm-tracer:latest

# Run with SQLite
docker run -d -p 8000:8000 \
  -e DATABASE_URL=sqlite:///data/llmtracer.db \
  -e SECRET_KEY=your-secret-key \
  -v llmtracer_data:/app/data \
  ghcr.io/yourusername/llm-tracer:latest
```

### Option 3: Local Development

```bash
# Prerequisites: Python 3.10+, uv, Node.js 20+

# Install uv (if not already)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Clone and setup
git clone https://github.com/yourusername/llm-tracer.git
cd llm-tracer

# Install Python dependencies
uv sync

# Run the server
cd packages/llm-tracer
uv run llm-tracer

# In another terminal, run the frontend
cd apps/web
npm install
npm run dev
```

## 🔌 SDK Integration

### Installation

```bash
pip install llm-tracer-sdk
# or
uv add llm-tracer-sdk
```

### Basic Usage

```python
import llm_tracer_sdk

# Initialize once at startup
llm_tracer_sdk.init(
    api_key="lt-your-api-key",
    endpoint="http://localhost:8000"
)

# All LangChain calls are now automatically traced!
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")
response = llm.invoke("Hello!")  # Automatically traced!

# Add context to traces
with llm_tracer_sdk.set_user("user-123"):
    with llm_tracer_sdk.set_session("session-456"):
        response = llm.invoke("Who are you?")

# Shutdown gracefully (flushes pending traces)
llm_tracer_sdk.shutdown()
```

### Environment Variables

```bash
export LLM_TRACER_ENDPOINT=http://localhost:8000
export LLM_TRACER_API_KEY=lt-your-api-key
export LLM_TRACER_PROJECT=my-project
```

```python
# With env vars set, just call init()
llm_tracer_sdk.init()
```

### Manual Callback Handler

```python
from llm_tracer_sdk import LLMTracerCallback

# Use with LangChain's callback system
handler = LLMTracerCallback(
    api_key="lt-your-api-key",
    endpoint="http://localhost:8000"
)

llm = ChatOpenAI(model="gpt-4", callbacks=[handler])
response = llm.invoke("Hello!")
```

## 🔐 Configuration

### Server Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///llmtracer.db` |
| `SECRET_KEY` | Secret for signing tokens | Required in production |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Enable debug mode | `false` |
| `CORS_ORIGINS` | Comma-separated origins | `http://localhost:3000` |

### SDK Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_TRACER_ENDPOINT` | Server URL | Required |
| `LLM_TRACER_API_KEY` | API key | Required |
| `LLM_TRACER_PROJECT` | Project name | `default` |
| `LLM_TRACER_ENABLED` | Enable tracing | `true` |

## 🌐 API Endpoints

The server exposes a REST API under `/api/v1`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | User authentication |
| `/api/v1/auth/register` | POST | User registration |
| `/api/v1/projects` | GET/POST | List/create projects |
| `/api/v1/api-keys` | GET/POST | List/create API keys |
| `/api/v1/traces` | GET | List traces |
| `/api/v1/traces/{id}` | GET | Get trace details |
| `/api/v1/ingest` | POST | SDK trace ingestion |
| `/health` | GET | Health check |

## 🧪 Development

```bash
# Install all dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=packages

# Type checking
uv run mypy packages/

# Linting and formatting
uv run ruff check packages/
uv run ruff format packages/

# Frontend development
cd apps/web
npm install
npm run dev

# Build frontend
npm run build
```

## 🚢 Deployment

### Docker Compose (Production)

```bash
# Configure environment
cp .env.example .env
# Set SECRET_KEY, POSTGRES_PASSWORD, etc.

# Deploy
docker compose up -d

# View logs
docker compose logs -f app
```

### GitHub Actions

The repository includes GitHub Actions workflows:

- **CI** (`ci.yml`): Runs tests, linting, and frontend build on every push
- **Docker** (`docker-publish.yml`): Builds and pushes Docker images to GHCR on release
- **PyPI** (`publish.yml`): Publishes packages to PyPI on release

### Manual Docker Build

```bash
# Build the image
docker build -t llm-tracer:latest .

# Run
docker run -d -p 8000:8000 \
  -e DATABASE_URL=sqlite:///data/llmtracer.db \
  -e SECRET_KEY=your-secret-key \
  llm-tracer:latest
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.
