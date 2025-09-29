# Mermaid Diagrams for Antifragile Strategy Presentation

## Lost in Translation Problem

```mermaid
flowchart TD
    A[CEO Goal: "Focus on closing Q3 deals"] -->|Message| B[Sales Team]
    A -->|Message| C[Engineering Team]

    B --> D[Interprets: Prioritize renewals & existing customers]
    C --> E[Interprets: Delay or adjust new product roadmap]

    style A fill:#004488,stroke:#fff,stroke-width:2px,color:#fff
    style B fill:#88ccee,stroke:#333
    style C fill:#88ccee,stroke:#333
    style D fill:#ffeeaa,stroke:#333
    style E fill:#ffeeaa,stroke:#333
```

## Antifragile Strategy Flow

```mermaid
graph LR
    A[Input] --> B[Process]
    B --> C[Output]
    C --> D[Feedback]
    D --> B

    style A fill:#39FF14,stroke:#fff,stroke-width:2px,color:#000
    style B fill:#FF6F61,stroke:#fff,stroke-width:2px,color:#fff
    style C fill:#39FF14,stroke:#fff,stroke-width:2px,color:#000
    style D fill:#FF6F61,stroke:#fff,stroke-width:2px,color:#fff
```

## Workflow Architecture

```mermaid
graph TB
    subgraph "Temporal Workflows"
        A[Onboarding Workflow]
        B[Daily Leadership Interaction]
        C[Active AI Agents]
    end

    subgraph "Data Sources"
        D[CRM Systems]
        E[Project Management]
        F[Communication Tools]
    end

    A --> D
    B --> E
    C --> F

    style A fill:#001f3f,stroke:#39FF14,stroke-width:2px,color:#39FF14
    style B fill:#001f3f,stroke:#39FF14,stroke-width:2px,color:#39FF14
    style C fill:#001f3f,stroke:#39FF14,stroke-width:2px,color:#39FF14
    style D fill:#001f3f,stroke:#FF6F61,stroke-width:2px,color:#FF6F61
    style E fill:#001f3f,stroke:#FF6F61,stroke-width:2px,color:#FF6F61
    style F fill:#001f3f,stroke:#FF6F61,stroke-width:2px,color:#FF6F61
```
