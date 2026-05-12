# 🇩🇪 German Learning RAG SaaS

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.111.0-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-v14-black?logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

A production-grade, AI-powered German language learning platform leveraging **Retrieval-Augmented Generation (RAG)**. This system transforms static study materials into interactive, level-aware tutoring experiences.

## 🚀 Key Features

- **Context-Aware Tutoring**: AI responses are grounded in your uploaded documents using vector search (PGVector/Qdrant).
- **Pedagogical Intelligence**: Multi-mode tutoring (Socratic, Grammar, Translate) tailored to CEFR levels (A1-C2).
- **Secure by Design**: Redis-backed per-user rate limiting, prompt injection sanitization, and JWT (HS256) authentication.
- **Async Pipeline**: Non-blocking LLM calls with Tenacity retries and background document processing via Celery & RabbitMQ.
- **Cloud Native**: Optimized for deployment on **Render** (Backend) and **Vercel** (Frontend).

---

## 🛠️ Architecture

The project follows **Domain-Driven Design (DDD)** principles.

```
├── src/                          # Backend (FastAPI)
│   ├── domains/                  # Core Business Logic (Identity, Learning, Tutor)
│   ├── infrastructure/           # LLM Providers (OpenAI/CoHere) & DB Clients
│   ├── routes/                   # Secure, versioned API Endpoints
│   ├── security/                 # Redis Rate Limiter, Sanitizers & Quota Guards
│   └── main.py                   # App Initialization & Middleware
├── frontend/                     # Frontend (Next.js 14)
│   ├── src/app/                  # App Router: Dashboard, Chat, Learning Path
│   └── src/services/             # Axios API Clients with JWT Interceptors
└── docker/                       # Full Stack Orchestration (Postgres, Redis, RabbitMQ)
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.11**
- **Node.js 18+** & npm
- **PostgreSQL** with [pgvector](https://github.com/pgvector/pgvector) extension
- **Redis** & **RabbitMQ**
- **OpenAI API Key**

### Backend Setup

1. **Install Dependencies**:
   ```bash
   cd src
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `src/.env.example` to `src/.env` and fill in your keys.

3. **Run Migrations**:
   ```bash
   cd src/models/db_schemes/minirag
   alembic upgrade head
   ```

4. **Start the API**:
   ```bash
   cd src
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

1. **Install Dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start Dev Server**:
   ```bash
   npm run dev
   ```
   Access at `http://localhost:3000`.

---

## ☁️ Deployment

### Backend (Render)
1. Create a **Web Service** for the FastAPI app.
2. Create a **Background Worker** for Celery.
3. Create a **Cron Job** for Celery Beat.
4. Use **Neon Postgres** and **Upstash Redis**.

### Frontend (Vercel)
1. Connect your GitHub repo.
2. Set `Root Directory` to `frontend/`.
3. Set `NEXT_PUBLIC_API_URL` to your Render backend URL.

---

## 🛡️ Security & Reliability

- **JWT Security**: Explicit `HS256` algorithm validation to prevent algorithm confusion attacks.
- **Rate Limiting**: Redis-based token bucket per user (Free: 20 req/min, Pro: 200 req/min).
- **Fault Tolerance**: Tenacity retries on LLM API calls (exponential backoff).
- **Observability**: Structured JSON logging via `structlog` and Sentry integration.

---

## 📄 License

Distributed under the **Apache License 2.0**. See `LICENSE` for more information.

*Built with ❤️ for German learners everywhere.*
