<!--
Sync Impact Report:
Version change: 1.0.0 -> 1.1.0
List of modified principles: All principles replaced with new structured principles.
Added sections: Purpose, Agent Behavior Rules, Allowed Tools, Output Rules, Safety sections
Removed sections: Modes section
Templates requiring updates:
- .specify/templates/plan-template.md: ⚠ pending
- .specify/templates/spec-template.md: ⚠ pending
- .specify/templates/tasks-template.md: ⚠ pending
Follow-up TODOs: None
-->
# Constitution — Physical AI & Humanoid Robotics Textbook Project

## 1. Purpose
To generate a complete Physical AI & Humanoid Robotics textbook and supporting AI systems following the Hackathon specification.

## 2. Agent Behavior Rules
- Always follow the Spec → Plan → Tasks → Implementation → Clarify workflow.
- Never skip steps.
- Always produce deterministic, reproducible outputs.
- Always work inside the project folder.
- Always prefer modular design.
- Always output Markdown for book content and TypeScript/Python for code.
- Never hallucinate technologies not requested by the user.
- Never use Gemini unless explicitly asked.

## 3. Allowed Tools
- Docusaurus for textbook
- SpecKit-Plus for spec-driven generation
- Claude Code CLI for automation
- FastAPI for backend
- Qdrant + Postgres for RAG
- JavaScript/TypeScript + React components for front-end enhancements

## 4. Output Rules
- Every step must produce files in `/book`, `/backend`, or `/docs`.
- Code must be minimal, clean, and production-oriented.
- Documentation must be clear, human-readable, and structured.

## 5. Safety
- Avoid ambiguous instructions.
- Ask clarification via `/sp.clarify.md` whenever needed.

## Governance

Constitution supersedes all other practices; Amendments require documentation, approval, migration plan

All PRs/reviews must verify compliance; Complexity must be justified; Use CLAUDE.md for runtime development guidance

**Version**: 1.1.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-07