# LLM Tracer Server

Self-hosted observability platform for LangChain and LangGraph applications.

## Installation

```bash
pip install llm-tracer
```

## Quick Start

```bash
# Run the server
llm-tracer

# Or with uvicorn
uvicorn llm_tracer.app:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`.

## Configuration

Configure via environment variables or `.env` file:

```bash
# Database (SQLite default, PostgreSQL for production)
DATABASE_URL=postgresql://user:password@localhost:5432/llm_tracer

# Or use individual PostgreSQL vars
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=llm_tracer

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Security (change in production!)
SECRET_KEY=your-secure-secret-key

# CORS origins (comma-separated)
CORS_ORIGINS=["http://localhost:3000"]
```

## Docker

```bash
docker run -p 8000:8000 ghcr.io/yourusername/llm-tracer:latest
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`

## License

MIT
