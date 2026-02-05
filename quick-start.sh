#!/bin/bash
# Quick Start Script for German Learning RAG SaaS

echo " Starting German Learning RAG SaaS Setup..."

# 1. Backend Dependencies
echo " Installing backend dependencies from requirements.txt..."
if [ -f "src/requirements.txt" ]; then
    pip install -r src/requirements.txt -q
    echo " Backend dependencies installed!"
else
    echo " src/requirements.txt not found! Installing core packages manually..."
    pip install fastapi uvicorn[standard] python-multipart python-dotenv pydantic-settings aiofiles \
        SQLAlchemy asyncpg alembic psycopg2-binary pgvector \
        openai cohere langchain qdrant-client nltk \
        prometheus-client starlette-exporter fastapi-health \
        celery redis python-jose[cryptography] passlib[bcrypt] -q
fi

# 2. Frontend Dependencies
echo " Initializing frontend dependencies..."
if [ -d "frontend" ]; then
    cd frontend && npm install --quiet && cd ..
    echo " Frontend dependencies installed!"
else
    echo "  Frontend directory not found! Skipping frontend install."
fi

echo ""
echo " Setup complete! Now follow these steps to launch:"
echo ""
echo " Backend Configuration:"
echo "   1. Copy src/.env.example to src/.env and add your API keys (OpenAI, etc.)"
echo "   2. Ensure Postgres (with pgvector), Redis, and RabbitMQ are running."
echo "   3. Run migrations: cd src && alembic upgrade head"
echo "   4. Start API: cd src && uvicorn main:app --reload --port 5000"
echo ""
echo " Frontend Configuration:"
echo "   1. Ensure frontend/.env.local has: NEXT_PUBLIC_API_URL=http://localhost:5000"
echo "   2. cd frontend && npm run dev"
echo "   3. Access the app at http://localhost:3000"
echo ""
echo " Monitoring:"
echo "   - API Docs: http://localhost:5000/docs"
echo "   - Health Check: http://localhost:5000/health"
echo ""
echo "Happy learning! 🇩🇪"
