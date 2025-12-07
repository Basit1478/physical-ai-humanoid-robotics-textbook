# Data Model: AI Humanoid Robotics Textbook

## Overview
This document defines the data models for the AI Humanoid Robotics Textbook project, based on the entities identified in the feature specification and requirements.

## Core Entities

### Module
**Description**: Major section of the textbook containing 2-3 related chapters covering a specific aspect of humanoid robotics

**Fields**:
- `id` (string): Unique identifier for the module (e.g., "module1", "module2")
- `title` (string): Display title of the module (e.g., "The Robotic Nervous System")
- `description` (string): Brief description of the module content
- `order` (integer): Sequential order of the module (1-4)
- `chapters` (array): List of chapter IDs belonging to this module

**Relationships**:
- One-to-many with Chapter (one module contains multiple chapters)

### Chapter
**Description**: Subsection within a module containing detailed explanations, examples, diagrams, learning outcomes, and summaries

**Fields**:
- `id` (string): Unique identifier for the chapter (e.g., "module1-chapter1")
- `moduleId` (string): Reference to the parent module
- `title` (string): Display title of the chapter
- `content` (string): Main content of the chapter in Markdown format
- `learningOutcomes` (array): List of learning outcomes for the chapter
- `summary` (string): Chapter summary
- `order` (integer): Sequential order of the chapter within the module (1-3)
- `textDiagrams` (array): Text descriptions of diagrams included in the chapter

**Relationships**:
- Many-to-one with Module (many chapters belong to one module)

### LearningOutcome
**Description**: Specific, measurable skill or knowledge that a reader should acquire from each chapter

**Fields**:
- `id` (string): Unique identifier for the learning outcome
- `chapterId` (string): Reference to the parent chapter
- `description` (string): Detailed description of the learning outcome
- `measurableCriteria` (string): How to measure if the outcome has been achieved

**Relationships**:
- Many-to-one with Chapter (many learning outcomes belong to one chapter)

### User
**Description**: Represents students, instructors, or developers using the textbook

**Fields**:
- `id` (string): Unique identifier for the user
- `type` (enum): User type (STUDENT, INSTRUCTOR, DEVELOPER)
- `name` (string): User's name
- `email` (string): User's email address
- `enrolledModules` (array): List of module IDs the user is studying
- `progress` (object): Tracking progress per chapter
- `preferences` (object): Personalization preferences

### Progress
**Description**: Tracks user progress through the textbook content

**Fields**:
- `userId` (string): Reference to the user
- `chapterId` (string): Reference to the chapter
- `completed` (boolean): Whether the chapter is completed
- `completionDate` (datetime): When the chapter was completed
- `notes` (string): User's notes on the chapter
- `rating` (integer): User's rating of the chapter (1-5)

### Translation
**Description**: Stores translated content for multi-language support

**Fields**:
- `id` (string): Unique identifier for the translation
- `sourceId` (string): Reference to the original content (could be chapter or module)
- `sourceType` (enum): Type of source content (CHAPTER, MODULE)
- `language` (string): Language code (e.g., "ur", "en")
- `content` (string): Translated content in Markdown format
- `lastUpdated` (datetime): When the translation was last updated

### Citation
**Description**: Academic citations and references for the textbook content

**Fields**:
- `id` (string): Unique identifier for the citation
- `title` (string): Title of the cited work
- `authors` (array): List of authors
- `publicationDate` (date): Date of publication
- `source` (string): Where the work was published
- `url` (string): URL if available
- `doi` (string): Digital Object Identifier if available
- `citationType` (enum): Type of source (BOOK, ARTICLE, CONFERENCE, WEBSITE)

## Relationships Summary

```
Module (1) ---- (Many) Chapter (1) ---- (Many) LearningOutcome
     |
     |---- (Many) User.enrolledModules
     |
     |---- (Many) Translation

User (1) ---- (Many) Progress
Chapter (1) ---- (Many) Translation
Chapter (1) ---- (Many) Progress
```

## Validation Rules

### Module
- Must have exactly 2-3 chapters
- Title must not be empty
- Order must be between 1-4

### Chapter
- Must belong to a valid module
- Content must not be empty
- Must have at least one learning outcome
- Order must be between 1-3

### LearningOutcome
- Must belong to a valid chapter
- Description must not be empty
- Measurable criteria must be defined

### User
- Email must be valid if provided
- User type must be one of the defined enum values
- Progress tracking must reference valid chapters

### Progress
- Must reference a valid user and chapter
- Completion date must not be in the future if completed is true
- Rating must be between 1-5 if provided

### Translation
- Language code must follow ISO 639-1 standard
- Must reference a valid source content
- Content must not be empty

### Citation
- Must have at least a title
- Publication date must not be in the future
- At least one of URL or DOI must be provided for verification