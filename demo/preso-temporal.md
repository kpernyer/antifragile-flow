---
marp: true
title: Temporal — Reliable Orchestration for Modern Systems
paginate: true
html: true
style: |
  /* Global slide style */
  section {
    background-color: #001f3f; /* midnight blue */
    color: #C0C0C0;            /* silver text */
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    line-height: 1.35;
  }

  /* Accent colors */
  :root {
    --accent-green: #39FF14; /* neon green */
    --accent-coral: #FF6F61; /* coral red */
  }

  a { color: var(--accent-green); }
  strong, em, code { color: var(--accent-coral); }

  /* “Efficient corporate yet demo-fun”: clean spacing */
  h1, h2, h3 {
    letter-spacing: 0.2px;
    text-transform: none;
  }

  /* Improve H1 readability with steel/silver tone and reduced glow */
  h1 {
    color: #CCCCCC; /* silver */
    text-shadow: 0 0 2px rgba(0,0,0,0.35);
  }

  /* Accent utility classes */
  .accent-green { color: var(--accent-green); }
  .accent-coral { color: var(--accent-coral); }

---

# Temporal — Reliable Orchestration for Modern Systems
### Kenneth Pernyer

---

## The Core Problem It Solves

- Distributed systems need to run **multi-step, long-running workflows**
- Traditional options:
  - Cron jobs / Celery / ad-hoc queues
  - Hard to restart safely, state lost after crash
  - Manual retry, error handling, backoff, audit trails
- **Need:** deterministic orchestration with **durable state** and visibility

---

## What Temporal Is

- **Open source orchestration platform**
- Write workflows in normal code (Python, Go, Java, TypeScript)
- Temporal server persists state and event history so you can:
  - Pause/resume safely
  - Survive restarts or crashes
  - Query or signal workflows externally

---

## Key Building Blocks

- **Workflow** — orchestration logic (deterministic, no heavy lifting)
- **Activity** — actual work (I/O, ML, API calls)
- **Worker** — process executing workflows & activities
- Opinionated structure:
  - Workflows stay *thin*
  - Activities are small, testable
  - Workers can be specialized (e.g., LLM calls vs doc processing)

---

## How I Use It

- **Document ingestion pipeline**
  - Upload → chunk → embed → store in Weaviate/Neo4j → metadata in Postgres
  - LLM summarization, embedding, graph writing, file storage as activities
- **Daily interaction flow**
  - CEO’s prioritized inbox
  - Signals from humans (approve, refine, escalate) mid-workflow
- State & progress are **durable** — can stop workers, upgrade code, resume

---

## Benefits I See

- **Resiliency** — retries, backoff, no lost state on crash
- **Simpler code** — no custom queue glue; business logic in Python
- **Visibility** — Temporal Web UI shows runs & payloads
- **Scalability** — single dev worker, scale out in prod
- **Auditability** — full execution history

---

## Performance in My System

- Handles long document processing jobs reliably
- Activities scale horizontally (CPU/LLM heavy work separated)
- Minimal ops overhead — one Temporal cluster for dev, expandable later

---

## Architecture Sketch

```mermaid
flowchart LR
    User[User / API] --> WF[Workflow<br/>(thin orchestration)]
    WF -->|calls| A1[Activity: Ingest]
    WF -->|calls| A2[Activity: ML/LLM]
    WF -->|calls| A3[Activity: Storage]
    WF -- state & history --> T[Temporal Server]
    T -- visibility & audit --> UI[Temporal Web UI]
````

---

## Practical Advice

- Keep workflows **pure & deterministic**
- Put external calls & heavy logic in **activities**
- Version workflows — Temporal supports safe upgrades
- Use **signals/queries** for human-in-the-loop steps and status checks

---

## Closing

- Temporal removed a huge amount of custom reliability code for me
- Perfect for **Organizational Twin / RAG + LLM workflows**
- Gives confidence to **scale complex, long-running processes**
