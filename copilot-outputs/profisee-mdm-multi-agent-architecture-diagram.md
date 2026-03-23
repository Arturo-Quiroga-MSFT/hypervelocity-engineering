# Profisee MDM Multi-Agent System — Architecture Diagram

> Generated 2026-03-20 · Microsoft Agent Framework (MAF) on Azure AI Foundry Agent Services

## System Overview

A multi-agent architecture that provides AI-driven insights into Profisee's Master Data Management (MDM) system. An orchestrator agent routes user queries to five specialized agents, each focused on a distinct MDM concern. Profisee's MCP Server enables direct connectivity between agents and the MDM platform.

## Architecture Diagram

```mermaid
graph TB
    %% ── User Layer ──
    User["👤 User / Analyst\n(Browser or Copilot Chat)"]

    %% ── API & Frontend ──
    User --> APIM["Azure API Management\n(Gateway & Rate Limiting)"]
    APIM --> AppService["Azure App Service\n(Streamlit Dashboard)"]

    %% ── Orchestrator ──
    AppService --> Orchestrator["🤖 Orchestrator Agent\n(Microsoft Agent Framework)"]

    %% ── Specialized Agents ──
    Orchestrator --> QualityAgent["🔍 Data Quality Agent\n· Completeness Analysis\n· Accuracy Scoring\n· Consistency Checks"]
    Orchestrator --> ValidationAgent["✅ Data Validation Agent\n· Schema Validation\n· Business Rule Checks\n· Regulatory Compliance"]
    Orchestrator --> EnrichmentAgent["✨ Data Enrichment Agent\n· Missing Field Inference\n· External Data Lookup\n· Semantic Matching"]
    Orchestrator --> ResolutionAgent["🔗 Data Resolution Agent\n· Duplicate Detection\n· Conflict Resolution\n· Entity Merging"]
    Orchestrator --> GovernanceAgent["🛡️ Data Governance Agent\n· Audit Trail Logging\n· Policy Compliance\n· Data Lineage Tracking"]

    %% ── Profisee MDM ──
    QualityAgent --> MCP["Profisee MCP Server\n(MCP Protocol)"]
    ValidationAgent --> MCP
    EnrichmentAgent --> MCP
    ResolutionAgent --> MCP
    GovernanceAgent --> MCP
    MCP --> Profisee["Profisee MDM\n(Master Data Hub in\nMicrosoft Fabric)"]

    %% ── Azure AI Services ──
    QualityAgent --> OpenAI["Azure OpenAI\n(GPT-4o)"]
    ValidationAgent --> OpenAI
    EnrichmentAgent --> OpenAI
    ResolutionAgent --> OpenAI
    GovernanceAgent --> OpenAI

    EnrichmentAgent --> AISearch["Azure AI Search\n(Vector + Hybrid Search)"]
    ResolutionAgent --> AISearch
    AISearch --> Blob["Azure Blob Storage\n(Reference Documents)"]

    %% ── Data Stores ──
    Orchestrator --> CosmosDB["Azure Cosmos DB\n(Session History &\nAgent State)"]
    GovernanceAgent --> SQL["Azure SQL Database\n(Governance Metadata\n& Audit Logs)"]

    %% ── Security & Governance ──
    AppService --> KeyVault["Azure Key Vault\n(Secrets & Certificates)"]
    OpenAI --> KeyVault
    MCP --> KeyVault

    %% ── Observability (dashed lines) ──
    Orchestrator -.-> Monitor["Azure Monitor\n(App Insights +\nLog Analytics)"]
    QualityAgent -.-> Monitor
    ValidationAgent -.-> Monitor
    EnrichmentAgent -.-> Monitor
    ResolutionAgent -.-> Monitor
    GovernanceAgent -.-> Monitor
    AppService -.-> Monitor
    MCP -.-> Monitor

    %% ── Analytics ──
    Profisee --> Fabric["Microsoft Fabric\n(Unified Analytics)"]
    GovernanceAgent --> Purview["Microsoft Purview\n(Data Catalog &\nLineage)"]

    %% ── Styles ──
    style User fill:#4FC3F7,stroke:#0288D1,color:#000
    style APIM fill:#7E57C2,stroke:#512DA8,color:#fff
    style AppService fill:#66BB6A,stroke:#388E3C,color:#000

    style Orchestrator fill:#FF7043,stroke:#E64A19,color:#fff
    style QualityAgent fill:#FFAB40,stroke:#FF6D00,color:#000
    style ValidationAgent fill:#FFAB40,stroke:#FF6D00,color:#000
    style EnrichmentAgent fill:#FFAB40,stroke:#FF6D00,color:#000
    style ResolutionAgent fill:#FFAB40,stroke:#FF6D00,color:#000
    style GovernanceAgent fill:#FFAB40,stroke:#FF6D00,color:#000

    style MCP fill:#CE93D8,stroke:#AB47BC,color:#000
    style Profisee fill:#BA68C8,stroke:#8E24AA,color:#fff

    style OpenAI fill:#42A5F5,stroke:#1E88E5,color:#000
    style AISearch fill:#AB47BC,stroke:#8E24AA,color:#fff
    style Blob fill:#FFCA28,stroke:#F9A825,color:#000
    style CosmosDB fill:#26A69A,stroke:#00897B,color:#fff
    style SQL fill:#5C6BC0,stroke:#3949AB,color:#fff
    style KeyVault fill:#EF5350,stroke:#E53935,color:#fff
    style Monitor fill:#FFB74D,stroke:#FB8C00,color:#000
    style Fabric fill:#29B6F6,stroke:#0288D1,color:#000
    style Purview fill:#78909C,stroke:#546E7A,color:#fff
```

## Data Flow

| Flow | Path | Description |
|------|------|-------------|
| **User Query** | User → APIM → App Service → Orchestrator | Natural-language question about master data quality, duplicates, compliance, etc. |
| **Agent Routing** | Orchestrator → Specialized Agent | MAF orchestrator classifies intent and delegates to the appropriate agent |
| **MDM Access** | Agent → Profisee MCP Server → Profisee MDM | Agents read/write master data via Profisee's MCP protocol |
| **LLM Reasoning** | Agent → Azure OpenAI (GPT-4o) | Each agent uses GPT-4o for analysis, summarization, and recommendations |
| **RAG Retrieval** | Agent → Azure AI Search → Blob Storage | Enrichment & Resolution agents retrieve reference data for matching |
| **Persistence** | Orchestrator → Cosmos DB | Session history and agent state stored for continuity |
| **Governance** | Governance Agent → Azure SQL / Purview | Audit logs, policy metadata, and data lineage captured |
| **Observability** | All agents -.-> Azure Monitor | Telemetry, traces, and logs via Application Insights |

## Agent Responsibilities

| Agent | Primary Function | Key Insights Provided |
|-------|-----------------|----------------------|
| **Data Quality** | Analyze completeness, accuracy, consistency | "47 customer records are missing postal codes; overall completeness is 92%" |
| **Data Validation** | Enforce schema and business rules | "12 records violate the email format rule; 3 fail regulatory address requirements" |
| **Data Enrichment** | Fill gaps using AI and external sources | "Inferred 31 missing industry codes from company descriptions with 94% confidence" |
| **Data Resolution** | Detect and merge duplicates | "Found 8 potential duplicate clusters across 23 records; recommended merge strategy ready" |
| **Data Governance** | Track lineage, audit, and compliance | "All changes since March 1 are fully audited; 2 policy violations flagged for review" |

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Framework | Microsoft Agent Framework (MAF) | Multi-agent orchestration and tool calling |
| Hosting | Azure AI Foundry Agent Services | Managed agent runtime |
| LLM | Azure OpenAI (GPT-4o) | Reasoning, analysis, summarization |
| Search | Azure AI Search (vector + hybrid) | RAG retrieval for enrichment and resolution |
| MDM Platform | Profisee (in Microsoft Fabric) | Master data hub |
| MDM Connectivity | Profisee MCP Server | MCP protocol bridge to MDM APIs |
| Data Stores | Cosmos DB, Azure SQL, Blob Storage | State, governance metadata, documents |
| Governance | Microsoft Purview | Data catalog and lineage |
| Analytics | Microsoft Fabric | Unified analytics over master data |
| Security | Azure Key Vault, APIM | Secrets management, API gateway |
| Observability | Azure Monitor + App Insights | Logging, tracing, alerting |

## Performance Targets

| Metric | Target |
|--------|--------|
| Data completeness score | ≥ 95% |
| Data accuracy score | ≥ 98% |
| Record processing throughput | 10,000 records/hour |
| Agent response latency (P95) | < 5 seconds |
| Duplicate detection precision | ≥ 97% |

---

*Diagram follows the Mermaid format — renders in VS Code Markdown preview, GitHub, and most documentation platforms. Export to PNG/SVG via Mermaid CLI or VS Code extensions.*
