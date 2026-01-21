# Product Requirements Document (PRD)

## Project Title
Automated Blog Post Content Pipeline for Tistory

## Overview
This project builds an **end-to-end automated content generation pipeline** for publishing high-quality blog posts to **Tistory** using **LangChain**, **RAG (Retrieval-Augmented Generation)**, and **LangGraph**. The system is designed to research, generate, review, and publish blog posts with minimal human intervention while maintaining factual accuracy, structure, and consistent writing style.

The pipeline targets technical and AI-focused blog content but is extensible to other domains.

---

## Goals

### Primary Goals
- Automate the full lifecycle of blog content creation
- Ensure factual grounding using RAG
- Enable multi-step reasoning and control using LangGraph
- Publish directly to Tistory via API or browser automation

### Success Metrics
- Time to publish reduced by >80%
- Zero hallucinated factual claims in generated posts
- Consistent blog tone and formatting
- Ability to regenerate or update posts automatically

---

## Non-Goals
- Fully autonomous social media marketing
- Image generation (v1 text-only)
- Real-time news publishing

---

## Target Users
- Solo developers
- AI engineers / researchers
- Technical bloggers
- Indie hackers

---

## High-Level Architecture

```
User Topic / Trigger
        ↓
LangGraph Orchestrator
        ↓
Research Agent → RAG Retrieval
        ↓
Outline Generator
        ↓
Content Writer Agent
        ↓
Critic / Fact Checker Agent
        ↓
SEO + Formatter Agent
        ↓
Tistory Publisher
```

---

## Core Components

### 1. LangGraph Orchestration Layer
**Purpose:** Control flow, retries, branching, and state management.

Responsibilities:
- Define DAG-based content pipeline
- Handle failures and retries
- Enable conditional steps (e.g., rewrite if quality < threshold)

---

### 2. Research & RAG Module
**Tech Stack:** LangChain, Vector DB (FAISS / Chroma / Weaviate)

Responsibilities:
- Search internal knowledge base
- Load external sources (Markdown, PDFs, blogs)
- Chunk and embed documents
- Retrieve contextually relevant information

Outputs:
- Verified knowledge context
- Source metadata

---

### 3. Outline Generation Agent
**Purpose:** Convert topic + research into structured blog outline.

Features:
- Section hierarchy (H1–H3)
- Logical narrative flow
- Estimated word count per section

---

### 4. Content Writing Agent
**Purpose:** Generate long-form blog content.

Capabilities:
- Markdown formatting
- Code block support
- Examples and explanations
- Style consistency

Constraints:
- Must only use RAG-provided facts
- No unsupported claims

---

### 5. Critic / QA Agent
**Purpose:** Quality assurance and safety.

Checks:
- Factual correctness
- Logical flow
- Redundancy
- Hallucination detection

Actions:
- Approve
- Request rewrite
- Request additional research

---

### 6. SEO & Formatting Agent
**Purpose:** Optimize post for discoverability and platform compliance.

Features:
- SEO-friendly title & headings
- Meta description generation
- Keyword density optimization
- Tistory-compatible Markdown/HTML

---

### 7. Tistory Publishing Module
**Purpose:** Automatic post publication.

Options:
- Tistory Open API
- Headless browser automation (Playwright)

Features:
- Draft vs publish mode
- Tag assignment
- Category selection
- Scheduled publishing

---

## Data Flow

| Stage | Input | Output |
|------|------|--------|
| Topic Input | User prompt / cron | Topic spec |
| Research | Topic spec | Context docs |
| Outline | Context docs | Blog outline |
| Writing | Outline + context | Draft content |
| QA | Draft | Approved content |
| SEO | Approved content | Final content |
| Publish | Final content | Live post |

---

## Configuration & Controls

- Model selection (GPT-4 / local LLM)
- Temperature per agent
- Max iterations per node
- Fact confidence threshold
- Manual approval toggle

---

## Security & Safety

- API key encryption
- Source attribution tracking
- Logging via LangSmith
- Prompt injection protection

---

## Observability

- LangSmith traces
- Node-level metrics
- Failure analytics
- Content quality scoring

---

## Extensibility (Future Work)

- Image generation agent
- Multilingual publishing
- Auto cross-posting (Medium, Dev.to)
- Feedback loop from reader analytics
- Continuous content updates

---

## Risks & Mitigations

| Risk | Mitigation |
|----|----|
| Hallucinations | Strict RAG enforcement |
| API rate limits | Caching + retries |
| Platform changes | Adapter-based publisher |
| Content duplication | Embedding similarity checks |

---

## Milestones

1. MVP pipeline (local run)
2. RAG grounding
3. LangGraph orchestration
4. Tistory draft publishing
5. Full automation + scheduling

---

## Final Notes

This system is designed as a **portfolio-grade AI infrastructure project**, demonstrating practical use of LangChain, RAG, and LangGraph in a real-world publishing workflow. It emphasizes reliability, observability, and extensibility over raw generation speed.

