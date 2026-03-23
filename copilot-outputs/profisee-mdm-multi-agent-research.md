# Profisee MDM × Azure Multi-Agent System — Partner Call Research

> **Prepared:** 2026-03-20 | **Partner:** PROFISEE | **Focus:** Multi-Agent System for MDM

---

## 1. Partner Context: Profisee & Aisey

Profisee is the leading MDM provider natively embedded in **Microsoft Fabric**. Their recent product **Aisey** (2025 R3+) is the industry's first AI-driven agentic assistant for MDM, powered by **Azure OpenAI**.

### Aisey Capabilities
| Mode | Description |
|------|-------------|
| **Aisey Chat** | Conversational NL interface for data model config, rules, imports |
| **Aisey Agents** | Autonomous agents for continuous stewardship, match/survivorship, quality checks |
| **Aisey Skills** | On-demand tasks — file imports, DQ rule generation, schema operations |

### Profisee Azure Integrations (Already in Place)
- **Microsoft Fabric** — First MDM embedded in Fabric; Open Mirroring support
- **Azure Data Factory** — Data movement and ETL pipelines
- **Microsoft Purview** — Governance, cataloging, lineage
- **Azure OpenAI** — Powers Aisey's LLM reasoning
- **Profisee MCP Server** — Copilot connectivity via Model Context Protocol
- **Power BI / Synapse** — Analytics and reporting

---

## 2. Recommended Azure Services for Multi-Agent MDM

### Core Agent Services

| Service | Role in Architecture | Why It Matters |
|---------|---------------------|----------------|
| **Azure AI Foundry Agent Service** | Managed agent hosting, orchestration, observability | Enterprise-grade multi-agent runtime with built-in guardrails |
| **Azure OpenAI Service** | LLM backbone (GPT-4o, GPT-4.1) | Powers reasoning, NL understanding, tool-use for agents |
| **Microsoft Agent Framework (MAF)** | SDK for building & orchestrating agents | Unified Python/.NET framework; replaces AutoGen + Semantic Kernel |
| **Azure AI Search** | Vector + hybrid search over master data | Enables RAG patterns for data quality and entity resolution |

### Data & Integration Services

| Service | Role |
|---------|------|
| **Microsoft Fabric** | Unified analytics; Profisee native integration; OneLake storage |
| **Azure Data Factory** | Orchestrate data pipelines between Profisee and downstream systems |
| **Microsoft Purview** | Data governance, lineage, classification across the MDM estate |
| **Azure Logic Apps** | 1,400+ connectors for system-to-system integration |
| **Azure Event Grid / Service Bus** | Event-driven agent triggers (e.g., new record, DQ alert) |

### Security & Observability

| Service | Role |
|---------|------|
| **Microsoft Entra ID** | Identity for agents; RBAC; zero-trust agent authentication |
| **Azure Monitor / App Insights** | Agent telemetry, tracing (OpenTelemetry), cost dashboards |
| **Azure Key Vault** | Secret management for API keys, connection strings |

---

## 3. Python SDK Versions (Current as of March 2026)

| Package | Version | Purpose |
|---------|---------|---------|
| `azure-ai-projects` | **2.0.1** (2026-03-12) | Unified client for agents, datasets, evals, search indexes |
| `azure-ai-agents` | **1.1.0** (2025-08-05) | Foundational agent creation and management |
| `agent-framework` | **1.0.0rc5** (pre-release) | Microsoft Agent Framework — multi-agent orchestration |
| `agent-framework-azure-ai` | **1.0.0rc5** (pre-release) | MAF Azure AI Foundry provider |
| `azure-identity` | Latest stable | Entra ID auth (`DefaultAzureCredential`) |
| `azure-search-documents` | Latest stable | Azure AI Search integration |
| `semantic-kernel` | Maintenance | Legacy; migrate to MAF for new projects |

### Quick Install
```bash
pip install azure-ai-projects azure-ai-agents azure-identity
pip install agent-framework --pre  # MAF (release candidate)
```

> **Note:** Python ≥ 3.10 required for MAF. `azure-ai-projects` requires Python ≥ 3.9.

---

## 4. Key Limitations & Constraints

### Azure AI Foundry Agent Service Quotas

| Limit | Value |
|-------|-------|
| Max files per agent/thread | 10,000 |
| Max file size | 512 MB |
| Max total uploaded files per agent | 300 GB |
| Max vector store tokens per file | 2,000,000 |
| Max messages per thread | 100,000 |
| Max text content per message | 1,500,000 chars |
| Max tools per agent | 128 |
| Max agent resources per subscription/region | 2,000,000 |

### Important Constraints
- **Rate limits** are governed at the **model deployment level** (Azure OpenAI quotas), not the agent service itself
- **Regional availability** varies — not all tools (e.g., File Search) available in every region
- **Multi-agent quotas** apply per-agent/per-thread; orchestrating N agents means N × individual quotas
- **MAF is pre-release** (RC5) — expect breaking changes; `azure-ai-projects` is the stable alternative for production today
- **MCP protocol** is still maturing — Profisee's MCP server is an early adopter; ensure version compatibility
- **Context window limits** apply when agents share conversation threads; design for context-efficient handoffs

---

## 5. Recommended Architecture Patterns

### Pattern 1: Hub-and-Spoke Multi-Agent (Recommended for Profisee)
An **Orchestrator Agent** coordinates specialized domain agents:

```
                    ┌──────────────────┐
                    │   Orchestrator   │
                    │     Agent        │
                    │  (MAF / Foundry) │
                    └────────┬─────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
   ┌────────▼───────┐ ┌─────▼──────┐ ┌───────▼────────┐
   │  Data Quality  │ │  Entity    │ │  Stewardship   │
   │  Agent         │ │  Resolution│ │  Agent         │
   │                │ │  Agent     │ │                │
   └────────┬───────┘ └─────┬──────┘ └───────┬────────┘
            │                │                │
            └────────────────┼────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   Profisee MDM   │
                    │   (via REST API  │
                    │    / MCP Server) │
                    └──────────────────┘
```

**When to use:** Complex MDM workflows requiring DQ checks, entity matching, and human-in-the-loop stewardship.

### Pattern 2: Event-Driven Agent Pipeline
Agents trigger sequentially based on data events:

```
  Data Ingestion ──► Event Grid ──► DQ Agent ──► Match Agent ──► Merge Agent ──► Profisee
                                       │              │              │
                                       ▼              ▼              ▼
                                   Azure AI       Azure AI       Profisee
                                   Search         Search         REST API
```

**When to use:** High-volume, streaming MDM scenarios (e.g., real-time customer data onboarding).

### Pattern 3: Connected Agents (Peer-to-Peer)
Agents delegate directly to each other using Foundry's **Connected Agents** feature:

```
  Aisey Chat ◄──► Config Agent ◄──► Validation Agent ◄──► Import Agent
                                                              │
                                                        Profisee MDM
```

**When to use:** Extending Aisey's existing capabilities with custom specialized agents.

---

## 6. Architecture Overview: Profisee Multi-Agent MDM on Azure

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AZURE AI FOUNDRY                                │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    Agent Service (Managed)                        │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │  │
│  │  │ Orchestrator │  │  DQ Agent   │  │  Entity Res │              │  │
│  │  │    Agent     │──│             │──│    Agent    │              │  │
│  │  └──────┬───────┘  └──────┬──────┘  └──────┬──────┘              │  │
│  │         │                 │                 │                     │  │
│  │  ┌──────▼─────────────────▼─────────────────▼──────┐             │  │
│  │  │           Azure OpenAI (GPT-4o / 4.1)           │             │  │
│  │  └─────────────────────────────────────────────────┘             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Azure AI    │  │  Azure       │  │  Azure       │                  │
│  │  Search      │  │  Monitor     │  │  Key Vault   │                  │
│  │  (RAG/Vector)│  │  (Telemetry) │  │  (Secrets)   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    Profisee MCP Server  │
                    │   (Model Context Proto) │
                    └───────────┬────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                         PROFISEE MDM                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Master Data │  │  Aisey       │  │  Match /     │                  │
│  │  Models      │  │  (Native AI) │  │  Survivorship│                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│                      MICROSOFT FABRIC                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  OneLake     │  │  Power BI    │  │  Purview     │                  │
│  │  (Storage)   │  │  (Analytics) │  │  (Governance)│                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Talking Points for Partner Call

### Alignment Opportunities
1. **Profisee already uses Azure OpenAI** — natural extension to Azure AI Foundry Agent Service for multi-agent orchestration
2. **MCP Server exists** — Profisee has published an MCP server for Copilot connectivity; this is the bridge for custom agent integration
3. **Fabric-native** — Profisee in Fabric means agents can access OneLake data directly; unified governance via Purview
4. **Aisey complements, doesn't compete** — Custom agents built on MAF/Foundry extend Aisey's built-in capabilities

### Key Questions to Explore
- What MDM workflows are they looking to automate beyond Aisey's current scope?
- Are they targeting real-time (event-driven) or batch agent workflows?
- What data domains (customer, product, supplier) are highest priority?
- How do they envision agent-to-agent communication between Aisey and custom agents?
- What are their production scale requirements (records/sec, concurrent agents)?

### Potential Risks
- **MAF is RC** — recommend `azure-ai-projects` for production today; MAF for prototyping
- **MCP maturity** — protocol is evolving; version pinning and compatibility testing required
- **Cost management** — multi-agent = multiplied LLM token costs; design for efficiency
- **Data residency** — confirm regional availability matches Profisee's deployment regions

---

## 8. References

| Resource | URL |
|----------|-----|
| Azure AI Foundry Agent Service | https://azure.microsoft.com/en-us/products/ai-foundry/agent-service/ |
| Foundry Agent Quotas & Limits | https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/limits-quotas-regions |
| Microsoft Agent Framework (PyPI) | https://pypi.org/project/agent-framework/ |
| azure-ai-projects (PyPI) | https://pypi.org/project/azure-ai-projects/ |
| Profisee + Azure | https://profisee.com/solutions/microsoft-enterprise/azure/ |
| Profisee Aisey | https://profisee.com/platform/ai-assistant-aisey/ |
| Profisee MCP + Fabric (FabCon 2026) | https://profisee.com/press-release/profisee-brings-end-to-end-master-data-management-fully-into-microsoft-fabric-at-fabcon-2026-adds-fabric-open-mirroring-support-and-copilot-connectivity-via-profisee-mcp-server/ |
| MAF Orchestration Patterns | https://azure-samples.github.io/azure-ai-travel-agents/MAF-README.html |
| MCP on Azure | https://learn.microsoft.com/en-us/azure/developer/ai/intro-agents-mcp |
| Purview + Profisee MDM | https://learn.microsoft.com/en-us/purview/data-governance-master-data-management-profisee |
