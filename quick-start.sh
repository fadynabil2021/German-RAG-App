#!/bin/bash
# Quick Start Script for German Learning RAG SaaS

echo "🚀 Starting German Learning RAG SaaS Setup..."

# Install core dependencies (avoiding problematic ones)
echo "📦 Installing core dependencies..."
pip install fastapi uvicorn[standard] python-multipart python-dotenv pydantic-settings aiofiles -q

# Install database dependencies
echo "💾 Installing database dependencies..."
pip install SQLAlchemy asyncpg alembic psycopg2-binary pgvector -q

# Install LLM and NLP dependencies
echo "🤖 Installing AI dependencies..."
pip install openai cohere langchain -q

# Install task queue
echo "⚙️  Installing task queue..."
pip install celery redis kombu billiard vine -q

# Install monitoring
echo "📊 Installing monitoring..."
pip install prometheus-client starlette-exporter fastapi-health -q

# Install other dependencies
echo "📚 Installing remaining dependencies..."
pip install qdrant-client nltk -q

echo "✅ Dependencies installed!"
echo ""
echo "📝 Next steps:"
echo "1. Configure your .env file with API keys"
echo "2. Start PostgreSQL, RabbitMQ, and Redis"
echo "3. Run database migrations: cd src/models/db_schemes/minirag && alembic upgrade head"
echo "4. Start the app: cd src && uvicorn main:app --reload"
echo ""
echo "🎉 Setup complete!"
