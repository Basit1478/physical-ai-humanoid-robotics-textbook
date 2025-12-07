---
id: 1
title: Update Physical AI Robotics Textbook Constitution
stage: constitution
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: unknown
command: /sp.constitution # Constitution — Physical AI & Humanoid Robotics Textbook (Docusaurus Edition) Purpose - Deliver a Docusaurus-based textbook website using MDX chapters derived from the PDF. - Integrate a RAG chatbot using a separate FastAPI backend + Qdrant. - Output must be fully text-only and usable with Claude CLI and speckit-plus. Core Principles - Use Docusaurus v3 (TypeScript mode). - Use `/docs/` folder for textbook chapters. - Each chapter = `/docs/chapter-X-title.mdx`. - Backend is independent: FastAPI + Qdrant + OpenAI Agent tools. - Chatbot is embedded using a React component inside Docusaurus. - Only cite retrieved content from the indexed textbook. - Deterministic ingestion pipeline: chunk → embed → Qdrant. Modes - `/sp.constitution` to install this document. - `/sp.specify` to define detailed specification. - `/sp.plan` to define build plan. - `/sp.task` granular tasks. - `/sp.implement` full file generation. Output Rules - Frontend: TypeScript MDX (Docusaurus). - Backend: Python FastAPI. - Chatbot co
labels: ["constitution"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
- .specify/memory/constitution.md
tests:

---

## Prompt

# Constitution — Physical AI & Humanoid Robotics Textbook (Docusaurus Edition)

Purpose
- Deliver a Docusaurus-based textbook website using MDX chapters derived from the PDF.
- Integrate a RAG chatbot using a separate FastAPI backend + Qdrant.
- Output must be fully text-only and usable with Claude CLI and speckit-plus.

Core Principles
- Use Docusaurus v3 (TypeScript mode).
- Use `/docs/` folder for textbook chapters.
- Each chapter = `/docs/chapter-X-title.mdx`.
- Backend is independent: FastAPI + Qdrant + OpenAI Agent tools.
- Chatbot is embedded using a React component inside Docusaurus.
- Only cite retrieved content from the indexed textbook.
- Deterministic ingestion pipeline: chunk → embed → Qdrant.

Modes
- `/sp.constitution` to install this document.
- `/sp.specify` to define detailed specification.
- `/sp.plan` to define build plan.
- `/sp.task` granular tasks.
- `/sp.implement` full file generation.

Output Rules
- Frontend: TypeScript MDX (Docusaurus).
- Backend: Python FastAPI.
- Chatbot co

## Response snapshot

The project constitution has been successfully updated in .specify/memory/constitution.md to version 1.0.0. This includes purpose, core principles, modes, output rules, and governance details. Review of dependent templates for alignment is pending.

## Outcome

- ✅ Impact: Constitution updated.
- 🧪 Tests: N/A
- 📁 Files: 1 file modified.
- 🔁 Next prompts: Review updated constitution, review templates for alignment.
- 🧠 Reflection: Initial constitution successfully created/updated. PHR created.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
