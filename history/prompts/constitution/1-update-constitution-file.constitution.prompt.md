---
id: 1
title: "Update Constitution File"
stage: constitution
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "governance", "setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files: []
tests: []
---

# Update Constitution File

## Prompt Text
```
update constitution.md file # SpecKit Plus Constitution

This Constitution defines how the Claude Code CLI and SpecKit-Plus must behave in this project.

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
```

## Response Text
I have successfully updated the constitution file `.specify/memory/constitution.md` with the new content you provided. Here's what was done:

**Version Bump**: 1.0.0 → 1.1.0 (Minor version bump as new structured principles were added)

**Changes Made**:
- Replaced the previous template content with your structured constitution
- Added Purpose, Agent Behavior Rules, Allowed Tools, Output Rules, and Safety sections
- Removed the old Modes section
- Updated the governance section to align with the new structure
- Created a Sync Impact Report at the top of the file documenting all changes

**Files Updated**:
- `.specify/memory/constitution.md` - Updated with new constitution content
- `.specify/templates/plan-template.md` - Updated Constitution Check section to align with new principles

**Templates Requiring Manual Follow-up**:
- `.specify/templates/spec-template.md` - May need alignment with new output rules
- `.specify/templates/tasks-template.md` - May need alignment with new project structure expectations

**Suggested Commit Message**: `docs: amend constitution to v1.1.0 (structured principles and governance update)`

The updated constitution now clearly defines the project's purpose for generating a Physical AI & Humanoid Robotics textbook, establishes clear agent behavior rules, specifies allowed tools, defines output rules, and includes safety guidelines.