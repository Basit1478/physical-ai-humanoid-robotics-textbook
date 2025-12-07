# Specification — Textbook + Docusaurus + FastAPI RAG Chatbot

Tech Stack
Frontend:
- Docusaurus v3 (TypeScript)
- MDX for chapters
- Custom Chatbot React widget
- API calls → FastAPI WebSocket + REST

Backend:
- FastAPI (Python)
- Qdrant for vector search
- Postgres for metadata
- Redis for memory
- OpenAI Agents SDK for RAG + tools
- PDF/MDX ingestion → chunk → embed → upsert

Functionality
1. Textbook Website
   - Hosted on GitHub Pages or Vercel
   - Sidebar navigation auto-generated from `/docs/*`
   - Search from Docusaurus default theme (Fuse.js)

2. RAG Chatbot
   - React component injected in `/src/components/Chatbot`
   - Talks to backend WebSocket `/ws/chat/{session}`
   - Uses OpenAI Agents tools:
       - qdrant_search
       - citation_formatter
   - Returns answers + citations referencing MDX chapters

3. Backend Features
   - POST /api/v1/ingest — upload MDX or PDF chapters
   - Background worker to index files
   - GET /api/v1/search — semantic
   - WS /api/v1/ws/chat — stream