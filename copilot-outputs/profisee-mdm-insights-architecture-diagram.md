# PROFISEE MDM Insights — Multi-Agent Architecture Diagram

**Partner**: PROFISEE
**Use Case**: AI-Driven Insights into Master Data Management Content
**Technologies**: Microsoft Agent Framework (MAF), Foundry Agent Services, Azure AI Services
**Date**: March 2026
**PSA**: Arturo Quiroga

---

## High-Level Architecture

```mermaid
graph LR
    User["Data Steward\n(Browser / Copilot)"] --> APIM["Azure API Management"]
    APIM --> Gateway["Profisee Gateway\n(App Service)"]
    Gateway --> ORCH["MAF Orchestrator\nAgent"]

    ORCH --> Insights["Insights Agent\n(Trends & Anomalies)"]
    ORCH --> Lineage["Lineage Agent\n(Impact Analysis)"]
    ORCH --> Quality["Quality Agent\n(Scoring & Profiling)"]
    ORCH --> NLQuery["NL Query Agent\n(Natural-Language → MDM)"]

    Insights --> AOAI["Azure OpenAI\n(GPT-4o)"]
    Lineage --> AOAI
    Quality --> AOAI
    NLQuery --> AOAI

    NLQuery --> MCP["Profisee MCP Server\n(MDM API)"]
    Insights --> MCP
    Quality --> MCP
    Lineage --> MCP

    MCP --> ProfMDM["Profisee MDM\n(Master Data)"]

    Insights --> Search["Azure AI Search\n(Vector Index)"]
    Quality --> Search
    Lineage --> Search

    ORCH --> Cosmos["Azure Cosmos DB\n(Session & History)"]
    Gateway --> KV["Azure Key Vault\n(Secrets)"]
    AOAI --> KV

    APIM -.-> Monitor["Azure Monitor\n(App Insights)"]
    Gateway -.-> Monitor
    ORCH -.-> Monitor
    AOAI -.-> Monitor
    MCP -.-> Monitor

    style User fill:#4FC3F7,stroke:#0288D1,color:#000
    style APIM fill:#7E57C2,stroke:#512DA8,color:#fff
    style Gateway fill:#66BB6A,stroke:#388E3C,color:#000
    style ORCH fill:#FF7043,stroke:#E64A19,color:#fff
    style Insights fill:#A5D6A7,stroke:#4CAF50,color:#000
    style Lineage fill:#A5D6A7,stroke:#4CAF50,color:#000
    style Quality fill:#A5D6A7,stroke:#4CAF50,color:#000
    style NLQuery fill:#A5D6A7,stroke:#4CAF50,color:#000
    style AOAI fill:#42A5F5,stroke:#1E88E5,color:#000
    style MCP fill:#CE93D8,stroke:#AB47BC,color:#000
    style ProfMDM fill:#EF5350,stroke:#E53935,color:#fff
    style Search fill:#AB47BC,stroke:#8E24AA,color:#fff
    style Cosmos fill:#26A69A,stroke:#00897B,color:#fff
    style KV fill:#EF5350,stroke:#E53935,color:#fff
    style Monitor fill:#FFB74D,stroke:#FB8C00,color:#000
```

Solid lines → primary data flow. Dashed lines → telemetry / observability.

---

## Detailed Agent Interaction Flow

```mermaid
sequenceDiagram
    actor Steward as Data Steward
    participant GW as Gateway
    participant Orch as Orchestrator Agent
    participant NL as NL Query Agent
    participant Ins as Insights Agent
    participant Qual as Quality Agent
    participant Lin as Lineage Agent
    participant MCP as Profisee MCP Server
    participant LLM as Azure OpenAI

    Steward->>GW: "Show me customer data quality trends<br/>for the last 90 days"
    GW->>Orch: Route request
    Orch->>LLM: Classify intent
    LLM-->>Orch: [insights, quality]

    par Parallel Agent Execution
        Orch->>Ins: Analyze trends (90 days)
        Ins->>MCP: Fetch quality snapshots
        MCP-->>Ins: Time-series data
        Ins->>LLM: Summarize trends
        LLM-->>Ins: Trend narrative
    and
        Orch->>Qual: Profile current state
        Qual->>MCP: Fetch entity profiles
        MCP-->>Qual: Entity statistics
        Qual->>LLM: Score & explain
        LLM-->>Qual: Quality scorecard
    end

    Ins-->>Orch: Trend report
    Qual-->>Orch: Quality scorecard
    Orch->>LLM: Synthesize final answer
    LLM-->>Orch: Combined insight
    Orch-->>GW: Response
    GW-->>Steward: Rendered insight with charts
```

---

## Agent Responsibilities

| Agent | Purpose | Key Tools |
|-------|---------|-----------|
| **Orchestrator** | Intent classification, agent routing, response synthesis | Azure OpenAI |
| **NL Query Agent** | Translates natural-language questions into Profisee MDM API calls | Profisee MCP Server, Azure OpenAI |
| **Insights Agent** | Trend detection, anomaly analysis, predictive summaries | Profisee MCP Server, AI Search, Azure OpenAI |
| **Quality Agent** | Data profiling, completeness/accuracy scoring, remediation advice | Profisee MCP Server, AI Search, Azure OpenAI |
| **Lineage Agent** | Impact analysis, dependency mapping, change propagation tracking | Profisee MCP Server, AI Search, Azure OpenAI |

---

## Profisee MCP Server Integration

The **Profisee MCP Server** is the single gateway through which all agents access MDM content. It exposes Profisee's REST API as MCP-compatible tool functions, enabling:

- **Entity CRUD** — read/write master data records
- **Hierarchy traversal** — navigate parent-child relationships
- **Match/merge operations** — invoke Profisee's matching engine
- **Workflow status** — query stewardship workflow states
- **Audit history** — retrieve change logs for lineage analysis

```mermaid
graph TB
    subgraph "MAF Agents"
        A1[NL Query Agent]
        A2[Insights Agent]
        A3[Quality Agent]
        A4[Lineage Agent]
    end

    subgraph "Profisee MCP Server"
        T1["get_entities()"]
        T2["get_hierarchy()"]
        T3["run_match()"]
        T4["get_workflow_status()"]
        T5["get_audit_history()"]
    end

    subgraph "Profisee MDM Platform"
        MDM["Master Data Store"]
        Match["Matching Engine"]
        WF["Workflow Engine"]
        Audit["Audit Log"]
    end

    A1 --> T1
    A1 --> T2
    A2 --> T1
    A2 --> T5
    A3 --> T1
    A3 --> T3
    A4 --> T5
    A4 --> T4

    T1 --> MDM
    T2 --> MDM
    T3 --> Match
    T4 --> WF
    T5 --> Audit

    style A1 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style A2 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style A3 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style A4 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style T1 fill:#CE93D8,stroke:#AB47BC,color:#000
    style T2 fill:#CE93D8,stroke:#AB47BC,color:#000
    style T3 fill:#CE93D8,stroke:#AB47BC,color:#000
    style T4 fill:#CE93D8,stroke:#AB47BC,color:#000
    style T5 fill:#CE93D8,stroke:#AB47BC,color:#000
    style MDM fill:#EF5350,stroke:#E53935,color:#fff
    style Match fill:#EF5350,stroke:#E53935,color:#fff
    style WF fill:#EF5350,stroke:#E53935,color:#fff
    style Audit fill:#EF5350,stroke:#E53935,color:#fff
```

---

## Azure Services Summary

| Service | Role |
|---------|------|
| **Azure OpenAI (GPT-4o)** | LLM reasoning for all agents |
| **Azure AI Search** | Vector index over MDM metadata for semantic retrieval |
| **Azure Cosmos DB** | Conversation history, cached insights, session state |
| **Azure API Management** | Auth, rate-limiting, routing |
| **Azure Key Vault** | Secrets & certificates |
| **Azure Monitor / App Insights** | Distributed tracing, agent metrics, alerting |
| **Foundry Agent Services** | MAF agent hosting, scaling, lifecycle management |

---

## Deployment Topology

```mermaid
graph TB
    subgraph "Azure Subscription"
        subgraph "Foundry Agent Services"
            ORCH2["Orchestrator Agent\n(2–10 replicas)"]
            INS2["Insights Agent\n(2–8 replicas)"]
            QUAL2["Quality Agent\n(2–8 replicas)"]
            NLQ2["NL Query Agent\n(2–8 replicas)"]
            LIN2["Lineage Agent\n(2–6 replicas)"]
        end

        subgraph "Platform Services"
            AOAI2["Azure OpenAI"]
            SEARCH2["Azure AI Search"]
            COSMOS2["Cosmos DB"]
            APIM2["API Management"]
            MON2["Azure Monitor"]
        end

        subgraph "Networking"
            VNET["Virtual Network"]
            PE["Private Endpoints"]
        end
    end

    subgraph "Profisee Cloud"
        MCP2["Profisee MCP Server"]
        MDM2["Profisee MDM Platform"]
    end

    APIM2 --> ORCH2
    ORCH2 --> INS2
    ORCH2 --> QUAL2
    ORCH2 --> NLQ2
    ORCH2 --> LIN2

    INS2 --> AOAI2
    QUAL2 --> AOAI2
    NLQ2 --> AOAI2
    LIN2 --> AOAI2

    INS2 --> MCP2
    QUAL2 --> MCP2
    NLQ2 --> MCP2
    LIN2 --> MCP2

    MCP2 --> MDM2

    INS2 --> SEARCH2
    QUAL2 --> SEARCH2
    LIN2 --> SEARCH2

    ORCH2 --> COSMOS2

    PE --> AOAI2
    PE --> SEARCH2
    PE --> COSMOS2
    VNET --> PE

    ORCH2 -.-> MON2
    INS2 -.-> MON2
    QUAL2 -.-> MON2
    NLQ2 -.-> MON2
    LIN2 -.-> MON2

    style ORCH2 fill:#FF7043,stroke:#E64A19,color:#fff
    style INS2 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style QUAL2 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style NLQ2 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style LIN2 fill:#A5D6A7,stroke:#4CAF50,color:#000
    style AOAI2 fill:#42A5F5,stroke:#1E88E5,color:#000
    style SEARCH2 fill:#AB47BC,stroke:#8E24AA,color:#fff
    style COSMOS2 fill:#26A69A,stroke:#00897B,color:#fff
    style APIM2 fill:#7E57C2,stroke:#512DA8,color:#fff
    style MON2 fill:#FFB74D,stroke:#FB8C00,color:#000
    style MCP2 fill:#CE93D8,stroke:#AB47BC,color:#000
    style MDM2 fill:#EF5350,stroke:#E53935,color:#fff
    style VNET fill:#90A4AE,stroke:#607D8B,color:#000
    style PE fill:#90A4AE,stroke:#607D8B,color:#000
```

---

*Architecture diagram for PROFISEE's MAF-based multi-agent MDM insights system. Render in VS Code Markdown preview or any Mermaid-compatible viewer.*
