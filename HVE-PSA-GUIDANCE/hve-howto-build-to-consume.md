---
title: "HVE How-To: Build to Consume with HVE Core"
description: "Detailed workflows for PSAs to execute Build to Consume deliverables (ADS, POC, Build, Offering Validation, Commercialization, Activation) using HVE Core agents"
author: Arturo Quiroga
ms.date: 2026-04-08
ms.topic: how-to
keywords:
  - hve-core
  - build to consume
  - architecture design session
  - proof of concept
  - build
  - offering validation
  - marketplace
  - psa
  - gcps
estimated_reading_time: 18
---

# Build to Consume with HVE Core

Build to Consume represents approximately 60% of PSA time. This is where partner offerings take shape: from architecture design through production deployment to marketplace activation. This guide provides step-by-step workflows for executing each Build to Consume deliverable using HVE Core agents.

---

## 3.1 Architecture Design Sessions (ADS)

**Goal**: Refine broad ideas from Envisioning into specific, Well-Architected plans. Discuss options, approaches, and trade-offs. Produce an architecture diagram and contribute to SDC readiness.

**Frontier PSA capabilities used**: Rapid Prototype, Researcher, GHCP, Architect

### Workflow

#### Step 1: Prepare by Reviewing Envisioning Artifacts

Load the context from the Commit to Build stage so agents have continuity.

1. Select **Memory** and verify the partner context is loaded.
2. Open the PRD and BRD created during Envisioning — these drive the ADS scope.

#### Step 2: Generate the Architecture Diagram (Arch Diagram Builder)

1. Select **Arch Diagram Builder**.
2. Translate the PRD requirements into a concrete architecture:

```text
Create a detailed architecture diagram for Contoso Insurance's AI claims
processing system. Requirements from PRD:
- Claims intake: web portal (React) + mobile app (React Native)
- Document processing: Azure Document Intelligence (prebuilt invoice model)
- AI summarization: Azure OpenAI (GPT-4o, East US)
- Knowledge base: Azure AI Search (vector + semantic hybrid, claims history index)
- Claims adjuster dashboard: Azure App Service (Python/FastAPI backend)
- Conversation history: Azure Cosmos DB (NoSQL API, serverless)
- CRM integration: Azure Service Bus → Salesforce connector
- Security: Azure Key Vault, managed identity for all service-to-service auth
- Observability: Azure Monitor + Application Insights
- Networking: private endpoints for all data-plane services
Show: data flow from claim submission through AI processing to adjuster dashboard.
Include security boundaries and networking zones.
```

3. The agent produces a Mermaid diagram with all components and data flows.

#### Step 3: Review Against Well-Architected Framework (System Architecture Reviewer)

1. Select **System Architecture Reviewer**.
2. Review the architecture:

```text
Review this architecture for Contoso Insurance's AI claims processing
against all 5 WAF pillars:
- Reliability: single-region (East US) — is this sufficient for HIPAA workloads?
- Security: managed identity everywhere, private endpoints, HIPAA compliance
- Cost Optimization: serverless Cosmos DB, App Service vs Container Apps
- Operational Excellence: observability with App Insights, CI/CD pipeline
- Performance: Document Intelligence throughput at 500 claims/day, AI Search
  query latency for claims knowledge base

Flag any CRITICAL or MAJOR gaps. Recommend specific changes.
```

3. Address the findings before proceeding.

#### Step 4: Document Architecture Decisions (ADR Creation)

For every significant choice in the ADS, create an Architecture Decision Record.

1. Select **ADR Creation**.
2. Document each decision:

```text
Document our decision to use Azure App Service over Azure Container Apps
for the claims adjuster dashboard backend.
Context: The partner's team has 2 Python developers with Flask/FastAPI
experience but no container or Kubernetes experience.
Options considered: (1) App Service with Python, (2) Container Apps with Docker,
(3) Azure Functions with HTTP triggers.
Decision: App Service — lowest learning curve, built-in auto-scaling, meets
the 500 claims/day throughput requirement, supports managed identity.
Trade-off: Less granular scaling than Container Apps, but adequate for
the current workload. Revisit if volume exceeds 5,000 claims/day.
```

3. Repeat for other key decisions (database choice, networking model, AI model selection).

#### Step 5: Validate Infrastructure Deployability (Azure IaC Generator)

Prove the architecture is deployable by scaffolding the IaC.

1. Select **Azure IaC Generator**.
2. Generate the infrastructure code:

```text
Generate Bicep templates for the Contoso Insurance claims processing architecture:
- Azure OpenAI (GPT-4o deployment, East US)
- Azure AI Search (Standard S1, vector search enabled)
- Azure Document Intelligence (Standard S0)
- Azure Cosmos DB (serverless, NoSQL API)
- Azure App Service (Linux, Python 3.12, B2 plan)
- Azure Service Bus (Standard tier, 1 queue for CRM events)
- Azure Key Vault (RBAC access model)
- Azure Monitor workspace + Application Insights
All resources with managed identity. App Service gets Key Vault Secrets User,
Cognitive Services OpenAI User, Search Index Data Reader, and Cosmos DB
Data Contributor roles.
Use private endpoints for OpenAI, AI Search, Cosmos DB, and Key Vault.
```

3. This validates the architecture is technically sound and gives the partner a head start on provisioning.

#### Step 6: Create the Security Plan (Security Planner)

1. Select **Security Planner**.
2. Start the security assessment for the architecture:

```text
Create a security plan for the Contoso Insurance AI claims processing system.
The system handles Protected Health Information (PHI) under HIPAA.
Key components: Azure OpenAI, AI Search, Document Intelligence, Cosmos DB,
App Service, Key Vault, Service Bus.
Identity: managed identity for all service-to-service, Entra ID for user auth.
Data: claims documents (PDF, images), policyholder PII, medical records.
Integration: outbound to Salesforce CRM via Service Bus.
```

3. The agent produces a threat model and security recommendations aligned to the architecture.

---

## 3.2 Proof of Concept (POC)

**Goal**: Prove the value of the architecture chosen in the ADS. Build a working prototype that demonstrates feasibility with "customer zero." Secure commitment to a full build.

**Frontier PSA capabilities used**: GHCP, Rapid Prototype, Architect

### Workflow

#### Step 1: Scope the POC (Task Planner)

1. Start the **RPI workflow** with **Task Planner**.
2. Define a focused scope:

```text
Create a POC implementation plan for the Contoso Insurance claims processing
system. The POC should prove 2 things:
1. Azure Document Intelligence can extract key-value pairs from their
   specific claim form types with ≥95% accuracy
2. Azure OpenAI can generate accurate claims summaries from extracted data

Scope: Process 100 real claim documents from "customer zero" (MidWest Regional
Hospital). Build a minimal claims adjuster dashboard showing extraction
results and AI summaries side by side.

NOT in scope for POC: CRM integration, mobile app, full knowledge base.
Timeline: 3 weeks. Team: 1 PSA + 1 partner developer.
```

#### Step 2: Provision Resources (Azure IaC Generator or Azure Deploy)

1. Use the Bicep templates from the ADS (Step 5 above).
2. If templates exist, select **DeployToAzure** or run `azd up` directly.
3. If templates need adjustment for POC scope (e.g., fewer services), select **Azure IaC Generator** to produce a POC-scoped version.

#### Step 3: Research SDK Integration (Researcher Subagent)

1. Select **Researcher Subagent**.
2. Get the latest SDK guidance:

```text
Research the latest Azure Document Intelligence Python SDK (azure-ai-documentintelligence).
I need: current package version, how to use the prebuilt-invoice model,
how to extract key-value pairs from PDFs, and how to handle multi-page
documents. Also research the Azure OpenAI Python SDK for chat completions
with structured output to generate claims summaries.
```

#### Step 4: Implement the POC (Task Implementor)

1. Select **Task Implementor**.
2. Execute the plan from Step 1 phase by phase:

```text
Implement Phase 1 of the POC plan: Azure Document Intelligence integration.
Create a Python module that:
1. Accepts a PDF file path
2. Calls Azure Document Intelligence (prebuilt-invoice model) to extract
   key-value pairs
3. Returns a structured ClaimData object with: claimant_name, date_of_loss,
   claim_amount, policy_number, description
4. Handles errors (malformed PDFs, API timeouts, low-confidence extractions)
Use the azure-ai-documentintelligence SDK. Use managed identity for auth.
```

3. Coding instructions for Python auto-apply to every file, enforcing conventions.

#### Step 5: Build the POC Dashboard (Gen Streamlit Dashboard)

1. Select **Gen Streamlit Dashboard**.
2. Build the demo UI for stakeholder review:

```text
Build a Streamlit dashboard for the claims processing POC. Pages:
1. Upload page: drag-and-drop PDF upload for claim documents
2. Extraction results: side-by-side view of original PDF and extracted fields
3. AI Summary: generated claims summary with confidence scores
4. Batch results: table showing all 100 processed claims with accuracy metrics
Include a sidebar with processing statistics (avg extraction time,
accuracy rate, total claims processed).
```

3. Run it: `streamlit run poc_dashboard.py`.
4. Present to partner stakeholders and "customer zero."

#### Step 6: Validate POC Quality (Implementation Validator)

Before presenting results:

1. Select **Implementation Validator**.
2. Verify the implementation matches the plan:

```text
Validate the POC implementation against the plan. Check:
- Does the Document Intelligence integration handle all 5 required fields?
- Does the OpenAI summarization use the structured output format?
- Are error handling patterns consistent?
- Is managed identity used everywhere (no hardcoded keys)?
- Are the accuracy metrics calculated correctly?
```

---

## 3.3 Build

**Goal**: Support and guide the full technical design, development, and testing of the partner's offering. Maintain accountability for deployment timeline and commercial availability date.

**Frontier PSA capabilities used**: GHCP, Architect

### Workflow

#### Step 1: Set Up Sprint Structure (Agile Coach)

1. Select **Agile Coach**.
2. Establish the build cadence:

```text
The partner is starting a 4-month build for their AI claims processing offering.
Team: 2 backend Python developers, 1 frontend React developer, 1 QA engineer.
They use Azure DevOps. Help set up:
- 2-week sprint structure with ceremonies
- Definition of Done that includes security review
- Backlog organization (Epics → Features → User Stories → Tasks)
- Velocity tracking approach for the first 2 sprints
```

#### Step 2: Execute Implementation Phases (RPI Workflow)

The RPI workflow is the primary tool during the build phase: Research → Plan → Implement for each feature.

1. For each sprint's work, use **Task Planner** to break features into tasks.
2. Use **Task Implementor** to execute each task with coding instructions enforced.
3. Example for a Sprint 2 feature:

```text
Implement the claims knowledge base integration.
1. Create an Azure AI Search index schema for claims documents
   (fields: claim_id, claimant_name, date, amount, summary, embedding)
2. Build an indexer pipeline that processes extracted claims data
   and generates embeddings via Azure OpenAI text-embedding-3-large
3. Implement a RAG query function that takes a natural language question
   and returns relevant claims with citations
4. Add the RAG function as a tool in the MAF agent definition
```

#### Step 3: Review Code Contributions (PR Review + Code Review)

After each implementation, review the code before merging.

1. Select **PR Review** for pull request reviews with full functional + standards analysis.
2. Alternatively, use **Code Review Functional** for pre-PR checks on the working branch.
3. Use **Code Review Standards** when you want skill-based checks (e.g., Python conventions, test coverage).

```text
Review the pull request for the claims knowledge base integration.
Focus on: correct use of Azure AI Search SDK, embedding generation
pipeline efficiency, RAG query relevance, and error handling for
API failures. Check that managed identity is used consistently.
```

#### Step 4: Run Security Reviews (Security Planner)

Run security reviews at regular intervals during the build, not just at the end.

1. Select **Security Planner**.
2. The agent auto-detects the applicable OWASP skills based on the codebase:

| Stack Component | Skills That Activate |
|---|---|
| Python application code | `owasp-top-10`, `secure-by-design` |
| MAF agent definitions | `owasp-agentic` |
| Azure OpenAI / RAG pipeline | `owasp-llm` |
| Bicep infrastructure | `owasp-infrastructure` |

3. See [Quick Start 7](hve-quick-start-7-security-review.md) for detailed walkthrough.

#### Step 5: Keep Architecture Current (Arch Diagram Builder)

As the build evolves, update the architecture diagram to reflect reality.

1. Select **Arch Diagram Builder**.
2. Update with new components:

```text
Update the Contoso Insurance architecture diagram. Changes since ADS:
- Added Azure Container Registry for future containerization
- Changed from App Service B2 to B3 based on load testing
- Added Azure Front Door for WAF and global routing
- Added a second Azure OpenAI deployment in West US for failover
Keep all other components the same.
```

#### Step 6: Generate and Maintain IaC (Azure IaC Generator / Azure IaC Exporter)

1. Use **Azure IaC Generator** to produce Bicep/Terraform for new resources added during the build.
2. Use **Azure IaC Exporter** if the partner provisioned resources manually and needs to capture them as code.

---

## 3.4 Offering Validation

**Goal**: Assess the offering for readiness. Validate alignment with the taxonomy and Well-Architected Framework. Log the TTA and achieve Qualified status.

**Frontier PSA capabilities used**: Copilot

### Workflow

#### Step 1: WAF Validation (System Architecture Reviewer)

1. Select **System Architecture Reviewer**.
2. Run a full WAF assessment on the completed offering:

```text
Perform a comprehensive Well-Architected Framework review of the Contoso
Insurance AI claims processing offering. The offering is feature-complete
and preparing for marketplace listing. Assess all 5 pillars with specific
findings and remediation recommendations. The architecture includes:
Azure OpenAI, AI Search, Document Intelligence, Cosmos DB, App Service,
Front Door, Key Vault, Service Bus, Monitor/App Insights.
Deployment: Bicep with CI/CD via GitHub Actions.
```

3. Address all Critical and Major findings before proceeding.

#### Step 2: Security Validation (Security Planner)

1. Select **Security Planner**.
2. Run a pre-launch security review:

```text
Run a full security review on the Contoso Insurance claims processing offering.
This is the pre-marketplace validation. The system handles HIPAA-regulated
data (PHI). Check: authentication and authorization, data encryption
(at rest and in transit), input validation, API security, secret management,
logging and monitoring, HIPAA-specific controls.
```

3. Ensure no Critical findings remain.

#### Step 3: Implementation Completeness (Implementation Validator)

1. Select **Implementation Validator**.
2. Verify the final implementation against the approved plan and PRD:

```text
Validate the final implementation of the claims processing offering
against the original PRD and implementation plan. Check:
- All user stories marked as Done are actually implemented
- All API endpoints match the design specification
- Error handling covers the documented failure modes
- Observability instrumentation covers all critical paths
- Database schemas match the design
```

#### Step 4: Plan Completeness (Plan Validator)

1. Select **Plan Validator**.
2. Cross-check delivery against planning documents:

```text
Cross-check the completed offering against the original implementation plan.
Verify: all planned phases were completed, all exit criteria were met,
no planned features were dropped without documentation, and the
deployment automation covers all environments (dev, staging, production).
```

---

## 3.5 Offering Commercialization

**Goal**: Guide the partner through co-sell requirements and marketplace onboarding. Move from MCEM stage 1 to stages 2/3.

**Frontier PSA capabilities used**: Copilot

### Workflow

#### Step 1: Research co-sell Requirements (Researcher Subagent)

1. Select **Researcher Subagent**.
2. Get the current requirements:

```text
Research the current Azure Marketplace co-sell requirements for an
IP co-sell eligible offer. Include: required collateral (solution architecture
diagram, customer reference, one-pager), technical requirements for
transactable offers, and the co-sell review process timeline.
Also check requirements for the AI and Machine Learning specialization.
```

#### Step 2: Generate Listing Collateral (Arch Diagram Builder + BRD Builder)

1. Select **Arch Diagram Builder** to produce the reference architecture for the listing:

```text
Create a clean, customer-facing architecture diagram for the Contoso
Insurance AI Claims Processing offering. This is for the Azure Marketplace
listing page. Simplify the internal architecture into high-level components
that a buyer would understand: Claims Intake → AI Processing → Adjuster
Dashboard → CRM Integration. Show Azure services used but don't include
internal networking details. Make it presentation-ready.
```

2. Select **BRD Builder** for the business case one-pager:

```text
Create a one-page business case summary for the Azure Marketplace listing
of Contoso Insurance's AI Claims Processing offering. Key selling points:
- 80% reduction in claims processing time (45 min → 10 min/claim)
- 95% data extraction accuracy on standard claim forms
- Built on Azure AI services (OpenAI, AI Search, Document Intelligence)
- HIPAA compliant with SOC 2 Type II in progress
- Proven with customer zero (MidWest Regional Hospital, 200 claims/month)
```

#### Step 3: Create Repeatable Tooling (Prompt Builder)

Build the partner's self-sufficiency by creating custom agents for their ongoing commercialization tasks.

1. Select **Prompt Builder** (or the `agent-customization` skill):

```text
Create a custom prompt called "marketplace-listing-generator" that helps
the partner's marketing team generate Azure Marketplace listing content.
The prompt should ask for: offering name, target industry, key features
(up to 5), Azure services used, pricing model, and a customer testimonial.
It should output: a listing title, short description (100 chars), long
description (3000 chars), and 3 search keywords.
```

---

## 3.6 Offering Activation

**Goal**: Support the partner's first 3 customer wins. Coach the partner toward sales self-sufficiency.

**Frontier PSA capabilities used**: Architect, Copilot

### Workflow

#### Step 1: Build Customer Demo Materials (Gen Streamlit Dashboard)

1. Select **Gen Streamlit Dashboard**.
2. Build a customer-facing demo:

```text
Build a polished Streamlit demo app for the Contoso Insurance AI Claims
Processing offering. Target audience: prospective customers evaluating
the solution. The demo should:
1. Show a pre-loaded sample claim document being processed
2. Display real-time extraction of key fields with confidence scores
3. Show the AI-generated claims summary
4. Include a "Try It Yourself" tab where prospects can upload their own sample doc
5. Show a metrics dashboard with sample ROI projections
Use a professional theme. Include the partner's logo placeholder.
```

#### Step 2: Prepare Technical Sales Support (Researcher Subagent)

1. Select **Researcher Subagent**.
2. Prepare technical talking points for the partner's sales team:

```text
Prepare a technical FAQ document for Contoso Insurance's sales team
selling the AI Claims Processing offering. Cover the top 10 questions
a prospect's CTO would ask:
- How is PHI protected during AI processing?
- Where is data stored and processed (data residency)?
- What happens if Azure OpenAI is unavailable (failover)?
- How does the system scale for large claims volumes?
- What is the implementation timeline?
- How does it integrate with existing CRM systems?
- What training is needed for claims adjusters?
- What are the ongoing Azure costs at 1,000 claims/day?
- Is the system SOC 2 / HIPAA / ISO 27001 compliant?
- How are AI model updates handled?
```

#### Step 3: Generate Customer-Specific Architectures (Arch Diagram Builder)

When the partner's sales team engages specific prospects, generate tailored architecture diagrams.

1. Select **Arch Diagram Builder**.
2. Customize per customer:

```text
Create a customer-specific architecture diagram for Prospect ABC Corp.
They have specific requirements:
- Existing Azure environment with hub-spoke networking
- Express Route connectivity from on-premises
- Need to integrate with their SAP S/4HANA instead of Salesforce
- Data must stay in West Europe
Modify the standard claims processing architecture to accommodate these
requirements. Show how the offering plugs into their existing Azure
environment.
```

#### Step 4: Build Self-Sufficiency Tools (Prompt Builder)

Create custom agents the partner can use independently, reducing their dependency on PSA support.

1. Select **Prompt Builder**:

```text
Create a custom agent called "customer-onboarding-assistant" for the
partner's implementation team. The agent should guide a new customer
through deployment:
1. Collect Azure subscription details and region preference
2. Verify prerequisites (resource providers, quotas, networking)
3. Generate customer-specific parameter files for the Bicep deployment
4. Provide a step-by-step deployment guide
5. Run post-deployment validation checks
The agent should reference the partner's deployment documentation
and use azure-validate and azure-deploy skills.
```

2. Create another for customer support:

```text
Create a custom agent called "support-troubleshooter" for the partner's
L2 support team. The agent should help diagnose common issues:
- Document Intelligence extraction failures (bad quality scans, unsupported formats)
- OpenAI API errors (rate limiting, content filtering, timeouts)
- AI Search index sync issues
- Dashboard performance problems
Use azure-diagnostics skill. Include escalation criteria for when
the issue needs engineering involvement.
```

---

## What You Have After Build to Consume

At the end of this stage, the partner has a production-ready, commercially available offering:

| Deliverable | Artifacts Created with HVE Core |
|---|---|
| ADS | Architecture diagram, WAF review, ADRs, security plan, validated IaC templates |
| POC | Working prototype, accuracy metrics, stakeholder demo dashboard |
| Build | Production code (with coding instructions enforced), PR reviews, security reviews, updated architecture |
| Offering Validation | WAF assessment, security review, implementation validation, plan completeness check |
| Commercialization | Marketplace listing collateral, customer-facing architecture diagram, custom listing generator agent |
| Activation | Customer demo dashboard, technical FAQ, customer-specific architectures, self-sufficiency agents |

---

## End-to-End Artifact Flow

```
Pioneer Innovation          Commit to Build          Build to Consume
────────────────────       ────────────────────      ────────────────────
Research docs          →    PRD                  →    Implementation Plan
Architecture sketches  →    BRD                  →    ADRs
Demo dashboards        →    DT Workshop outputs  →    POC prototype
Partner context (Memory) → MVE results           →    Production code
                           Execution plan        →    Marketplace listing
                                                      Self-sufficiency agents
```

Each stage's outputs become the next stage's inputs. Memory persists partner context across all three stages.

---

*Part 3 of 3 in the HVE How-To series for Partner Solutions Architects*
