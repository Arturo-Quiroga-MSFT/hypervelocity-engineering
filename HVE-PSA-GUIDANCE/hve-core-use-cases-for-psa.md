# HVE Core — Use Cases for Partner Solutions Architects

> **Audience**: Partner Solutions Architects (PSAs) enabling partners to build pro-code apps and services on Azure AI & Agent AI  
> **Repository**: <https://github.com/microsoft/hve-core>  
> **Documentation**: <https://microsoft.github.io/hve-core/>  
> **VS Code Extension**: [Install HVE Core](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core)  
> **Date**: April 8, 2026

---

## What Is HVE Core?

Hypervelocity Engineering (HVE) Core is an **enterprise-ready prompt engineering framework for GitHub Copilot**. It provides 34 specialized agents, 68 coding instructions, 40 reusable prompts, and 3 skill packages — all with JSON schema validation and CI/CD enforcement.

The core methodology is **RPI (Research → Plan → Implement)** — a structured workflow where AI operates under explicit constraints rather than guessing. This changes the optimization target from "plausible code" to "verified truth."

---

## Why It Matters for Our Role

As PSAs, we help partners move from idea to production on Azure AI services. HVE Core provides structured AI guardrails across the entire engagement lifecycle — from architecture design through implementation. It's a force multiplier that makes our Copilot interactions more reliable and repeatable across partner engagements.

---

## Use Cases Mapped to Our Work

### 1. Accelerating Partner Proof-of-Concepts

The RPI workflow maps directly to how we run PoCs:

| RPI Phase | Agent | What It Does for Us |
|---|---|---|
| **Research** | `task-researcher` | Investigates Azure AI service options (OpenAI, AI Search, Document Intelligence, Speech) and surfaces relevant APIs before coding |
| **Plan** | `task-planner` | Generates structured implementation plans with tasks, dependencies, and architecture considerations |
| **Implement** | `task-implementor` | Executes the plan with constraint-based coding — Copilot explicitly knows what it *cannot* do, reducing hallucinated API calls |

**Example scenario**: A partner wants to build a RAG-based customer support agent using Microsoft Agent Framework (MAF) on Foundry Agent Services with Azure OpenAI + AI Search. The RPI workflow researches the right SDK versions, plans the architecture, and scaffolds the implementation — all in a structured, auditable sequence.

---

### 2. Solution Architecture & Design

Several agents are purpose-built for the architecture work we do daily:

| Agent | Use Case |
|---|---|
| `arch-diagram-builder` | Generate Mermaid architecture diagrams for partner solution designs (Azure AI + data flows) |
| `system-architecture-reviewer` | Review a partner's proposed architecture — catch misconfigurations or anti-patterns |
| `adr-creation` | Document Architecture Decision Records (e.g., "Why Azure OpenAI over a self-hosted model?") |
| `security-plan-creator` | Create security plans for partner apps handling sensitive data via Azure AI services |

---

### 3. Requirements & Business Planning

For formalizing partner requirements before technical work begins:

| Agent | Use Case |
|---|---|
| `brd-builder` | Help partners build a Business Requirements Document for their AI-powered product |
| `prd-builder` | Build a Product Requirements Document — structures what the partner's end-customer app needs |
| `product-manager-advisor` | Help partners prioritize AI features by business impact |

---

### 4. Design Thinking Workshops

When running ideation or design sessions with partners:

| Agent | Use Case |
|---|---|
| `dt-coach` | Guides through Design Thinking phases (Empathize, Define, Ideate, Prototype, Test) applied to the partner's AI product |
| `dt-learning-tutor` | Teaches Design Thinking concepts — useful when onboarding partner teams new to the methodology |

**Example scenario**: A partner wants to build a document processing SaaS using Azure Document Intelligence. The `dt-coach` helps frame the problem from their customer's perspective before jumping to tech.

---

### 5. Pro-Code Scaffolding — Coding Standards by Stack

HVE Core auto-applies coding instructions by file pattern. When a partner's project has these file types, Copilot follows the right conventions automatically:

| Instruction Set | Partner Scenario |
|---|---|
| **C#** (`.cs`) | Partners building .NET APIs with Azure OpenAI SDK, Microsoft Agent Framework (MAF) |
| **Python** (`.py`) | Partners building AI agents with Microsoft Agent Framework (MAF) and Foundry Agent Services on Azure |
| **Bicep** (`.bicep`) | IaC for provisioning Azure AI resources (Cognitive Services, AI Search, OpenAI) |
| **Terraform** (`.tf`) | Alternative IaC for Azure resource provisioning |
| **Bash** (`.sh`) | Deployment scripts for Azure CLI-based pipelines |

---

### 6. Data & AI Prototyping

For partners building data-driven AI solutions or needing quick demos:

| Agent | Use Case |
|---|---|
| `gen-data-spec` | Generate data specifications for AI features (input schemas, training data formats) |
| `gen-jupyter-notebook` | Scaffold Jupyter notebooks for AI model experimentation or Azure AI SDK demos |
| `gen-streamlit-dashboard` | Rapidly build demo dashboards to showcase AI service outputs to partner stakeholders |

---

### 7. Project Management During Engagements

When embedded with a partner dev team:

| Agent | Use Case |
|---|---|
| `agile-coach` | Advise on sprint planning, backlog grooming, and velocity for AI dev projects |
| `ux-ui-designer` | Guide the UX for AI-powered interfaces (chat UX, document upload flows, etc.) |

---

### 9. Security Reviews Before Production

The **Security Planner** orchestrates a full multi-skill security review without requiring you to be a security expert. A single prompt triggers the `Codebase Profiler`, which detects what's in the repo and activates only the relevant OWASP skill sets automatically.

| Partner's Stack | Skills That Activate Automatically |
|---|---|
| Any repo | `owasp-top-10` (web app vulnerabilities), `secure-by-design` (UK Gov + ASD/ACSC principles) |
| Python/C# agent code (MAF, Foundry) | `owasp-agentic` (agent-specific risks, e.g. prompt injection chains) |
| Azure OpenAI, RAG pipelines | `owasp-llm` (LLM Top 10, data leakage, insecure output handling) |
| MCP server code | `owasp-mcp` (MCP Top 10, tool poisoning, excessive permissions) |
| `.bicep` or `.tf` IaC files | `owasp-infrastructure` (Infrastructure Top 10, public endpoints, missing NSGs) |

**Prompt to start:**

```text
Analyse the code and produce a vulnerability report.
```

The report is written to `.copilot-tracking/security/` with findings organized by severity (Critical, High, Medium, Low) and OWASP category. See [Quick Start 7](hve-quick-start-7-security-review.md) for a step-by-step walkthrough.

---

Using the `prompt-builder` agent, we can create **our own custom agents** tailored to repeatable engagement patterns:

- An **"Azure AI Architecture Review"** agent with our org's best practices baked in
- A **"Partner Onboarding"** prompt that collects the right technical context upfront
- A **"Foundry Agent Scaffolder"** agent that generates MAF-based boilerplate for Microsoft Foundry Agent Services projects

These become shareable artifacts across our PSA team.

---

### 10. Recommended Agents for the PSA Role

After installation, these are the agents most relevant to our daily work enabling partners on Azure AI and Agent AI:

| Agent | When to Use |
|---|---|
| **RPI Agent** | Full Research → Plan → Implement workflow for partner engagements |
| **Task Planner** | Generate structured implementation plans for partner PoCs |
| **Task Implementor** | Execute plans with constraint-based coding |
| **Researcher Subagent** | Deep-dive into Azure AI / MAF SDK questions before coding |
| **AIAgentExpert** | AI agent architecture guidance — directly relevant to MAF work |
| **Azure IaC Generator** | Scaffold Bicep/Terraform for Azure AI resources |
| **Azure IaC Exporter** | Export existing Azure resource configs to IaC |
| **AzureCostOptimizeAgent** | Cost analysis for partner Azure AI deployments |
| **Security Planner** | Security reviews before production — auto-detects and applies the right OWASP skills based on the partner's stack |
| **PR Review** | Review partner code contributions for functional correctness and coding standards |
| **Memory** | Store context about your preferences (MAF, Foundry, partner details) across sessions |
| **Prompt Builder** | Create custom agents tailored to your engagement patterns |
| **Doc Ops** | Generate documentation for partner deliverables |
| **DataAnalysisExpert** | Data analysis for AI solution design |
| **Plan Validator** | Validate implementation plans before execution |
| **Implementation Validator** | Verify completed implementations against the plan |

**First thing to do after install**: Select the **Memory** agent and tell it your role and stack:

> *"Remember that I am a Partner Cloud Solutions Architect. I work with partners to technically enable them to build apps and services using Azure AI services. My AI agents are built with Microsoft Agent Framework (MAF) and Microsoft Foundry Agent Services (pro code)."*

This persists your context so every subsequent agent interaction is grounded in your role and stack.

---

## Quick Start (30 Seconds)

1. **Install** the [VS Code extension](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core)
2. **Verify** — Open Copilot Chat (`Ctrl+Alt+I` / `Cmd+Alt+I`) and check that HVE Core agents appear in the agent picker (`task-researcher`, `task-planner`, `rpi-agent`)
3. **Try it** — Select the `memory` agent and type: *"Remember that I'm exploring HVE Core for the first time."*

Full installation options (CLI, submodules, multi-root workspaces): [Installation Guide](https://github.com/microsoft/hve-core/blob/main/docs/getting-started/install.md)

---

## Key Links

| Resource | URL |
|---|---|
| GitHub Repository | <https://github.com/microsoft/hve-core> |
| Documentation Site | <https://microsoft.github.io/hve-core/> |
| VS Code Extension | [Marketplace](https://marketplace.visualstudio.com/items?itemName=ise-hve-essentials.hve-core) |
| Getting Started Guide | [Getting Started](https://github.com/microsoft/hve-core/blob/main/docs/getting-started/README.md) |
| RPI Workflow Deep Dive | [RPI Docs](https://microsoft.github.io/hve-core/docs/category/rpi) |
| Contributing / Custom Artifacts | [Contributing](https://github.com/microsoft/hve-core/blob/main/CONTRIBUTING.md) |
| License | MIT |

---

*Prepared for the Partner Solutions Architects (PSA) team — April 2026*
