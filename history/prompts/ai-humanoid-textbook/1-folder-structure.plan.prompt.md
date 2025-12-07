---
id: 1
title: "Folder Structure"
stage: plan
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: ai-humanoid-textbook
branch: 002-ai-humanoid-textbook
user: user
command: /sp.plan
labels: ["structure", "architecture", "planning"]
links:
  spec: specs/002-ai-humanoid-textbook/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - "specs/002-ai-humanoid-textbook/plan.md"
  - "specs/002-ai-humanoid-textbook/research.md"
  - "specs/002-ai-humanoid-textbook/data-model.md"
  - "specs/002-ai-humanoid-textbook/contracts/textbook-api.yaml"
  - "specs/002-ai-humanoid-textbook/quickstart.md"
tests: []
---

# Folder Structure

## Prompt Text
```
# Folder Structure

## High-Level Structure
Create the following directories:

1. book/
   - Contains Docusaurus documentation and textbook content
2. backend/
   - FastAPI application, ingestion, retrieval, embeddings
3. agents/
   - Subagents, skills, and agent registry
4. personalization/
   - User profile, chapter variants, personalization API
5. translation/
   - Urdu translation modules and API
6. deployment/
   - GitHub Pages config, API deployment configs
7. references/
   - APA bibliography and citation files

## Detailed Layout

book/
  module1/
    chapter1.md
    chapter2.md
    chapter3.md
  module2/
    chapter1.md
    chapter2.md
    chapter3.md
  module3/
    chapter1.md
    chapter2.md
    chapter3.md
  module4/
    chapter1.md
    chapter2.md
    chapter3.md
  docusaurus.config.ts
  sidebars.ts

backend/
  app/
    main.py
    config.py
  ingestion/
  retrieval/
  embeddings/
  models/
  routes/

agents/
  skills/
  subagents/
  registry/

personalization/
  profile/
  chapter-variants/
  api/

translation/
  urdu/
  api/

deployment/
  docusaurus/
  api/
  github-pages/
  env/

references/
  bibliography.md
  citations.md

## Output Requirements
- Provide a hierarchical tree listing
- No extra commentary
- Consistent indentation
```

## Response Text
Successfully created the implementation plan for the AI Humanoid Robotics Textbook project. The following artifacts were created:

1. Implementation Plan: specs/002-ai-humanoid-textbook/plan.md
   - Detailed technical context with language versions and dependencies
   - Constitution compliance check
   - Project structure mapping to the requested folder hierarchy

2. Research Document: specs/002-ai-humanoid-textbook/research.md
   - Technology decisions for Docusaurus and FastAPI
   - Architecture patterns and best practices
   - Open issues and future considerations

3. Data Model: specs/002-ai-humanoid-textbook/data-model.md
   - Entity definitions for Module, Chapter, LearningOutcome, User, Progress, Translation, and Citation
   - Relationships between entities
   - Validation rules

4. API Contracts: specs/002-ai-humanoid-textbook/contracts/textbook-api.yaml
   - OpenAPI specification for textbook platform APIs
   - Endpoints for modules, chapters, user progress, translations, and citations

5. Quickstart Guide: specs/002-ai-humanoid-textbook/quickstart.md
   - Setup instructions for frontend and backend
   - API usage examples
   - Development workflow guidance

The plan follows the requested folder structure with book/, backend/, agents/, personalization/, translation/, deployment/, and references/ directories as specified.