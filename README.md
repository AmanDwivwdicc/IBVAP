# IBVAP Central Server & Command Center

The Intelligent Border Video Analytics Platform (IBVAP) transforms existing standard CCTV networks into an AI-driven smart surveillance grid without requiring expensive, dedicated hardware.

## Project Structure
- `backend/`: FastAPI application handling Edge ingestion, SSE config push, and biometric profiling.
- `frontend/`: Next.js 15 Command Center utilizing Supabase SSR and WebSockets for real-time situational awareness.
- `docs/`: System architecture, API contracts, and integration specs.

## Deployment Strategy
The current tech stack is designed for a split-deployment architecture:
- **Backend (FastAPI)**: Hosted on a containerized PaaS or VPS.
- **Frontend (Next.js)**: Deployed serverlessly (e.g., Vercel) connecting directly to the Supabase database.
- **Database (Supabase)**: Provides PostgreSQL, pgvector, Realtime sockets, and object storage.
