---
title: "HVE How-To: Pioneer Innovation with HVE Core"
description: "Detailed workflows for PSAs to execute Pioneer Innovation deliverables (Tech Briefing, Workshop, Hackathons, Strategic Deal Activation) using HVE Core agents"
author: Arturo Quiroga
ms.date: 2026-04-08
ms.topic: how-to
keywords:
  - hve-core
  - pioneer innovation
  - tech briefing
  - workshop
  - hackathon
  - strategic deal activation
  - psa
  - gcps
estimated_reading_time: 12
---

# Pioneer Innovation with HVE Core

Pioneer Innovation is about discovery: driving awareness, identifying opportunities, and qualifying partners for the "Build to Consume" path. This guide provides step-by-step workflows for executing each Pioneer Innovation deliverable using HVE Core agents.

---

## 1.1 Tech Briefing

**Goal**: Deliver a compelling technical presentation on Azure AI capabilities to drive partner commitment to invest time and energy in building.

**Frontier PSA capabilities used**: Researcher, Architect

### Workflow

#### Step 1: Research the Topic (Researcher Subagent)

Before the briefing, get current information on the Azure AI services you will present.

1. Open Copilot Chat and select **Researcher Subagent**.
2. Provide context and ask targeted questions:

```text
Research the latest Azure OpenAI capabilities for enterprise deployments.
Include: available models on Azure, regional availability, pricing tiers,
rate limits, and any recent changes in the last 90 days. Also compare
GPT-4o vs GPT-4.1 capabilities for customer support use cases.
```

3. The agent returns a structured research document with citations.
4. Save the output for reference during your presentation.

#### Step 2: Build the Architecture Diagram (Arch Diagram Builder)

1. Select **Arch Diagram Builder**.
2. Describe the reference architecture you want to present:

```text
Create an architecture diagram for an enterprise RAG application on Azure.
Components: Azure Front Door, Azure App Service (Python backend),
Azure OpenAI (GPT-4o), Azure AI Search (vector + hybrid), Azure Cosmos DB
(chat history), Azure Key Vault (secrets), Azure Monitor (observability).
Show data flow from user query through to AI response.
```

3. The agent generates a Mermaid diagram you can drop into slides or render in GitHub.

#### Step 3: Build a Live Demo (Gen Streamlit Dashboard)

Instead of static slides, show the technology working.

1. Select **Gen Streamlit Dashboard** (or use `gen-streamlit-dashboard` from the agent picker).
2. Describe what you want to demo:

```text
Build a Streamlit demo app that shows a RAG-powered Q&A interface.
The app should have: a text input for questions, a response area showing
the AI answer, a sidebar showing which source documents were retrieved
from the knowledge base, and a simple metrics panel showing token usage
and response time.
```

3. Run it locally: `streamlit run demo_app.py`.
4. Screenshare during the briefing.

#### Step 4: Store Context for Follow-Up (Memory)

After the briefing, record partner context so future interactions have continuity.

1. Select **Memory**.
2. Record what matters:

```text
Remember that Partner Contoso attended a tech briefing on Azure OpenAI + AI Search
for RAG applications on April 8, 2026. Their CTO was interested in enterprise
SLA guarantees and content filtering. They have a customer support use case with
approximately 50,000 documents. Next step: schedule a Workshop to explore their
specific data and architecture requirements.
```

---

## 1.2 Workshop

**Goal**: Run hands-on sessions to uncover partner business goals, identify tech projects, assess workforce technical intensity, and create awareness of new features and roadmap.

**Frontier PSA capabilities used**: Researcher, Analyst

### Workflow

#### Step 1: Prepare the Workshop Agenda (Researcher Subagent)

1. Select **Researcher Subagent**.
2. Research the partner's domain and prepare talking points:

```text
Research best practices for building AI-powered document processing
solutions on Azure. The partner is in the insurance industry and wants
to automate claims processing. Include: Azure Document Intelligence
capabilities for form extraction, Azure OpenAI for summarization,
and Microsoft Agent Framework for workflow automation.
```

#### Step 2: Run Design Thinking Exercises (DT Coach)

Use Design Thinking to frame the problem from the end-user's perspective before jumping to technology.

1. Select **DT Coach**.
2. Start the empathize phase:

```text
We are running a workshop with an insurance partner. Their claims adjusters
currently spend 45 minutes per claim reviewing documents manually.
Help us run an empathy exercise to understand the claims adjuster's
pain points, workarounds, and unmet needs.
```

3. The agent guides you through structured exercises:
   - Empathy mapping for the claims adjuster persona
   - "How Might We" statement generation
   - Ideation clustering
4. Capture outputs as workshop artifacts.

#### Step 3: Build Hands-On Labs (Gen Jupyter Notebook)

Give the partner's technical team something to experiment with during the session.

1. Select **Gen Jupyter Notebook** (or use `gen-jupyter-notebook`).
2. Describe the lab:

```text
Create a Jupyter notebook that demonstrates Azure Document Intelligence
for processing insurance claim forms. The notebook should:
1. Load a sample PDF claim form
2. Call the Document Intelligence API to extract key-value pairs
3. Display the extracted fields (claimant name, date of loss, claim amount)
4. Call Azure OpenAI to generate a claim summary from the extracted data
5. Include markdown cells explaining each step for a hands-on lab audience
```

3. Run it in VS Code or JupyterLab during the workshop.

#### Step 4: Show Interactive Demos (Gen Streamlit Dashboard)

1. Select **Gen Streamlit Dashboard**.
2. Build a demo the partner can explore:

```text
Build a Streamlit app that processes uploaded PDF documents using
Azure Document Intelligence, displays extracted fields in a table,
and generates an AI summary using Azure OpenAI. Include a file uploader,
a results table, and a summary text area.
```

---

## 1.3 Hackathons

**Goal**: Align new builds or sales opportunities by solving specific problems, exploring use cases, and creating working prototypes in a compressed timeframe.

**Frontier PSA capabilities used**: Rapid Prototype, GHCP, Architect

### Workflow

#### Step 1: Set Up Each Team's Context (Memory)

At the start of the hackathon, have each team configure their Copilot context.

1. Select **Memory**.
2. Each team records their scenario:

```text
Remember that we are Team Alpha at the Contoso Hackathon.
Our scenario: build an AI-powered customer support agent using
Microsoft Agent Framework on Azure Foundry Agent Services.
Stack: Python, Azure OpenAI (GPT-4o), Azure AI Search, Azure Cosmos DB.
We have 48 hours.
```

#### Step 2: Research the Scenario (RPI — Research Phase)

1. Select **Researcher Subagent**.
2. Research the specific scenario:

```text
Research how to build a customer support agent using Microsoft Agent Framework
(MAF) on Azure Foundry Agent Services. Include: required SDK packages,
recommended architecture pattern, Azure AI Search integration for RAG,
and Cosmos DB for conversation history. Focus on the latest MAF SDK version.
```

#### Step 3: Plan the Implementation (RPI — Plan Phase)

1. Select **Task Planner**.
2. Generate the implementation plan:

```text
Create an implementation plan for a customer support AI agent using MAF
on Foundry Agent Services. The plan should cover:
1. Azure resource provisioning (OpenAI, AI Search, Cosmos DB, App Service)
2. MAF agent scaffolding with tool definitions
3. RAG pipeline integration with AI Search
4. Conversation history storage in Cosmos DB
5. Basic Streamlit demo UI
Timeline: 48 hours. Two developers.
```

#### Step 4: Scaffold Infrastructure (Azure IaC Generator)

1. Select **Azure IaC Generator**.
2. Generate the infrastructure:

```text
Generate Bicep templates for a customer support AI agent:
- Azure OpenAI (GPT-4o deployment)
- Azure AI Search (Standard tier, vector search enabled)
- Azure Cosmos DB (serverless, NoSQL API)
- Azure App Service (Linux, Python 3.12)
- Azure Key Vault (for API keys and connection strings)
All resources in East US, with managed identity for App Service to access
OpenAI, AI Search, and Cosmos DB without keys.
```

#### Step 5: Implement (RPI — Implement Phase)

1. Select **Task Implementor**.
2. Execute the plan step by step, referencing the plan from Step 3.
3. Coding instructions auto-apply Python and Bicep conventions to every file.

#### Step 6: Build the Demo (Gen Streamlit Dashboard)

1. Select **Gen Streamlit Dashboard** to build the hackathon demo UI.
2. Present to judges/stakeholders with the live demo.

---

## 1.4 Strategic Deal Activation

**Goal**: Provide technical consultation for transformational deals: RFP/RFI responses, reference architecture, and driving adoption of Microsoft best practices (CAF/WAF/LNZ).

**Frontier PSA capabilities used**: Researcher, Analyst, Architect

### Workflow

#### Step 1: Analyze the RFP Technical Requirements (Researcher Subagent)

1. Select **Researcher Subagent**.
2. Provide the RFP requirements and ask for a mapping:

```text
The partner received an RFP for an enterprise AI-powered customer service
platform. Key requirements:
- Handle 10,000 concurrent conversations
- Multi-language support (English, Spanish, Japanese)
- Integration with Salesforce CRM
- 99.9% uptime SLA
- Data residency in EU
- SOC 2 Type II compliance

Map each requirement to the recommended Azure services and explain
how each requirement is met.
```

#### Step 2: Build the Reference Architecture (Arch Diagram Builder)

1. Select **Arch Diagram Builder**.
2. Generate the architecture based on the RFP analysis:

```text
Create an architecture diagram for an enterprise AI customer service platform.
Requirements: 10,000 concurrent conversations, multi-region (EU primary),
Salesforce CRM integration. Components should include: Azure Front Door,
Azure Container Apps (agent runtime), Azure OpenAI, Azure AI Search,
Azure Cosmos DB (multi-region writes), Azure Service Bus (async CRM sync),
Azure Key Vault, Azure Monitor. Show data flow and security boundaries.
```

#### Step 3: Validate Against WAF (System Architecture Reviewer)

1. Select **System Architecture Reviewer**.
2. Review the proposed architecture:

```text
Review this architecture for an enterprise AI customer service platform
against the Azure Well-Architected Framework. Check all five pillars:
Reliability (multi-region, failover), Security (data residency, SOC 2),
Cost Optimization (right-sizing for 10K concurrent), Operational Excellence
(observability, CI/CD), Performance Efficiency (latency targets).
Flag any gaps or anti-patterns.
```

#### Step 4: Document Architecture Decisions (ADR Creation)

1. Select **ADR Creation**.
2. Document key decisions for the deal package:

```text
We chose Azure Container Apps over Azure Kubernetes Service for the AI agent
runtime. The partner needs autoscaling from 0 to 10,000 concurrent sessions,
with KEDA-based scaling on queue depth. They don't have Kubernetes expertise
on their team. Container Apps provides managed infrastructure, Dapr integration
for microservices communication, and meets the 99.9% SLA requirement.
```

#### Step 5: Structure the Business Case (BRD Builder)

1. Select **BRD Builder**.
2. Formalize the business requirements:

```text
Build a Business Requirements Document for the enterprise AI customer
service platform deal. The partner is responding to an RFP from a
Fortune 500 retailer. Business objectives: reduce average handle time
by 40%, support 3 languages from day one, integrate with existing
Salesforce CRM, achieve SOC 2 Type II compliance within 6 months.
```

#### Step 6: Estimate Costs (AzureCostOptimizeAgent)

1. Select **AzureCostOptimizeAgent**.
2. Provide the architecture and ask for a cost estimate to include in the deal package.

---

## What You Have After Pioneer Innovation

At the end of this stage, you should have produced:

| Deliverable | Artifacts Created with HVE Core |
|---|---|
| Tech Briefing | Research doc, architecture diagram, live demo dashboard, partner context in Memory |
| Workshop | Design Thinking outputs, hands-on Jupyter notebooks, interactive Streamlit demo |
| Hackathon | Implementation plan, IaC templates, working prototype, demo UI |
| Strategic Deal Activation | RFP analysis, reference architecture, WAF review, ADRs, BRD, cost estimate |

These artifacts feed directly into the **Commit to Build** stage. See [Commit to Build How-To](hve-howto-commit-to-build.md) for the next stage.

---

*Part 1 of 3 in the HVE How-To series for Partner Solutions Architects*
