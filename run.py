"""Simple run script for LLM Tracer."""

import asyncio
import sys


async def main():
    """Initialize database and run server."""
    print("🚀 Starting LLM Tracer...")
    print("=" * 50)
    
    # Import and create tables
    print("📦 Creating database tables...")
    from llm_tracer.db.tables import User, Project, APIKey, LLMTrace
    from piccolo.table import create_db_tables
    
    await create_db_tables(User, Project, APIKey, LLMTrace, if_not_exists=True)
    print("✅ Database tables created!")
    
    # Check for users
    user_count = await User.count()
    print(f"👥 Users in database: {user_count}")
    
    if user_count == 0:
        print("\n📝 No users found. Register at http://localhost:8000/register")
    else:
        print("\n🔑 Login at http://localhost:8000/login")
    
    print("=" * 50)
    print("🌐 Starting server at http://localhost:8000")
    print("📚 API docs at http://localhost:8000/docs")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server\n")
    
    # Run server
    import uvicorn
    config = uvicorn.Config(
        "llm_tracer.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
        sys.exit(0)
