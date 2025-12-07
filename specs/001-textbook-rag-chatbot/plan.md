# Implementation Plan: Docusaurus + RAG Backend

**Branch**: `001-textbook-rag-chatbot` | **Date**: 2025-12-06 | **Spec**: specs/001-textbook-rag-chatbot/spec.md
**Input**: Feature specification from `/specs/001-textbook-rag-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

The project aims to deliver a Docusaurus-based textbook website with MDX chapters and integrate a RAG chatbot. The chatbot will use a FastAPI backend with Qdrant for vector search, providing answers and citations referencing the MDX chapters.

## Technical Context

**Language/Version**: Python (FastAPI), TypeScript (Docusaurus v3)
**Primary Dependencies**: Docusaurus v3, FastAPI, Qdrant, OpenAI Agents SDK, React
**Storage**: Qdrant (vector search), Postgres (metadata), Redis (memory)
**Testing**: NEEDS CLARIFICATION (testing framework/strategy not specified)
**Target Platform**: Frontend: GitHub Pages or Vercel; Backend: Railway; Qdrant: Cloud; Postgres: Neon
**Project Type**: Web application (frontend + backend)
**Performance Goals**: NEEDS CLARIFICATION (specific performance metrics not defined)
**Constraints**: Output must be fully text-only and usable with Claude CLI and speckit-plus.
**Scale/Scope**: Textbook website with MDX chapters and an integrated RAG chatbot.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Use Docusaurus v3 (TypeScript mode). ✅ Aligns with plan.
- Use `/docs/` folder for textbook chapters. ✅ Aligns with plan.
- Each chapter = `/docs/chapter-X-title.mdx`. ✅ Aligns with plan.
- Backend is independent: FastAPI + Qdrant + OpenAI Agent tools. ✅ Aligns with plan.
- Chatbot is embedded using a React component inside Docusaurus. ✅ Aligns with plan.
- Only cite retrieved content from the indexed textbook. ✅ Aligns with plan.
- Deterministic ingestion pipeline: chunk → embed → Qdrant. ✅ Aligns with plan.

## Project Structure

### Documentation (this feature)

```text
specs/001-textbook-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/
```

**Structure Decision**: The project will adopt a `backend/` and `frontend/` split, aligning with the "Web application" option for a clear separation of concerns between the FastAPI backend and the Docusaurus React frontend.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| NEEDS CLARIFICATION: Testing Strategy | Not specified in plan or spec. Essential for ensuring quality. | Without a defined strategy, testing efforts could be inconsistent or insufficient, risking quality and maintainability. |
| NEEDS CLARIFICATION: Performance Goals | Not specified in plan or spec. Crucial for system scalability and user experience. | Without clear performance targets, there's no way to measure success or identify bottlenecks, potentially leading to a slow or unresponsive application. |
