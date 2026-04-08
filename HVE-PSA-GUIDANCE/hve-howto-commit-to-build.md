---
title: "HVE How-To: Commit to Build with HVE Core"
description: "Detailed workflows for PSAs to execute Commit to Build deliverables (Planning, Envisioning) using HVE Core agents"
author: Arturo Quiroga
ms.date: 2026-04-08
ms.topic: how-to
keywords:
  - hve-core
  - commit to build
  - planning
  - envisioning
  - design thinking
  - psa
  - gcps
estimated_reading_time: 10
---

# Commit to Build with HVE Core

Commit to Build is the critical inflection point where partner interest becomes executive commitment. This stage represents approximately 10% of PSA time and focuses on collaborative planning, priority alignment, and envisioning the technical roadmap. This guide provides step-by-step workflows for executing each Commit to Build deliverable using HVE Core agents.

---

## 2.1 Planning

**Goal**: Collaboratively plan with PDM, PTS, PSA, and GTM to agree on 1-3 priorities, secure executive commitment, and produce MVP execution timelines with specialization alignment.

**Frontier PSA capabilities used**: Researcher, Analyst

### Workflow

#### Step 1: Research the Partner's Technical Landscape (Researcher Subagent)

Before the planning session, gather intelligence on the partner's current state and the Azure services relevant to their goals.

1. Open Copilot Chat and select **Researcher Subagent**.
2. Frame the research around specific partner context:

```text
Research the current state of Azure AI services for building conversational
AI agents in the insurance industry. The partner (Contoso Insurance) currently
uses a rule-based chatbot on AWS Lex and wants to modernize to Azure.
Include: migration considerations from AWS Lex to Azure Bot Service or
Microsoft Agent Framework, available Azure AI services for claims processing
(Document Intelligence, OpenAI, AI Search), and MAICPP specialization
requirements for AI and Machine Learning.
```

3. Save the research output — it becomes your planning session preparation material.

#### Step 2: Build the Product Requirements Document (PRD Builder)

Translate the partner's goals into a structured product requirements document.

1. Select **PRD Builder**.
2. Start the guided conversation:

```text
Build a Product Requirements Document for Contoso Insurance's AI-powered
claims processing offering. The partner wants to:
1. Automate claims document intake and data extraction
2. Generate AI summaries for claims adjusters
3. Provide a conversational AI agent for customer claim status inquiries
4. Target Azure Marketplace listing within 6 months
Target users: claims adjusters (internal) and policyholders (external).
```

3. The agent asks guided questions about user personas, technical constraints, success criteria, and dependencies.
4. The result is a structured PRD ready for stakeholder review.

#### Step 3: Create the MVP Execution Plan (Task Planner)

1. Select the **RPI workflow** starting with **Task Planner**.
2. Reference the PRD from Step 2:

```text
Create an implementation plan for the Contoso Insurance AI claims processing
offering based on the PRD we just built. The plan should cover:
- Phase 1 (Month 1-2): Azure Document Intelligence integration for claims intake
- Phase 2 (Month 2-3): Azure OpenAI integration for claims summarization
- Phase 3 (Month 3-5): MAF agent for customer inquiries with RAG on claims data
- Phase 4 (Month 5-6): Marketplace listing and co-sell enablement
For each phase, include tasks, dependencies, skills required, and exit criteria.
Timeline: 6 months. Team: 2 backend developers, 1 frontend developer, 1 PSA.
```

3. The agent produces a phased plan with dependencies and milestones.

#### Step 4: Validate the Plan (Plan Validator)

Before presenting to stakeholders, validate the plan for completeness and consistency.

1. Select **Plan Validator**.
2. Point it at the generated plan:

```text
Validate this implementation plan against the PRD and research documents.
Check for:
- Missing dependencies between phases
- Unrealistic timelines given the team size
- Azure service prerequisites (subscriptions, quotas, approvals)
- Gaps in MAICPP specialization alignment
- Missing testing and security review phases
```

3. The agent returns severity-graded findings (Critical, Major, Minor).
4. Address any Critical or Major findings before the planning session.

#### Step 5: Design the MVE for Risky Assumptions (Experiment Designer)

If the plan has high-risk assumptions (e.g., "Document Intelligence can handle handwritten claim forms with 95% accuracy"), validate them before committing resources.

1. Select **Experiment Designer**.
2. Frame the risky assumption:

```text
We are assuming Azure Document Intelligence can extract key-value pairs
from handwritten insurance claim forms with at least 95% accuracy.
The partner processes approximately 500 claims/day, 30% of which are
handwritten. Help us design a Minimum Viable Experiment to validate
this assumption before committing to a 6-month build.
```

3. The agent guides you through hypothesis formation, experiment design, success criteria, and a run plan.
4. Document the MVE results — they strengthen the business case for executive commitment.

#### Step 6: Structure Sprint Cadence (Agile Coach)

1. Select **Agile Coach**.
2. Get sprint planning guidance:

```text
Help us structure the sprint cadence for a 6-month build with a team of
2 backend developers, 1 frontend developer, and 1 PSA providing
architecture guidance. The partner uses Azure DevOps for project management.
We want 2-week sprints with clear Definition of Done criteria.
Recommend the right ceremony cadence and backlog structure.
```

3. The agent provides sprint structure, ceremony cadence, and backlog organization recommendations.

---

## 2.2 Envisioning

**Goal**: Brainstorm, ideate, and explore the art of the possible. Identify current state, business goals, and motivations. Define "customer zero" for each build engagement and produce a tech roadmap.

**Frontier PSA capabilities used**: Researcher, Analyst, Architect

### Workflow

#### Step 1: Run Design Thinking (DT Coach)

This is where Design Thinking adds the most value — before committing to a technical direction, understand the real problem from the end-user's perspective.

1. Select **DT Coach**.
2. Start by framing the engagement:

```text
We are starting an envisioning engagement with Contoso Insurance.
They want to modernize their claims processing with AI.
Start with Method 1: Scope Conversations. The stakeholders are:
- VP of Claims Operations (budget holder)
- Claims Adjuster Team Lead (daily user)
- IT Director (infrastructure owner)
- "Customer Zero": MidWest Regional Hospital (their largest client)
Help us scope the engagement boundaries and identify frozen vs. fluid constraints.
```

3. The DT Coach guides you through the 9-method framework:
   - **Method 1**: Scope Conversations — stakeholder alignment, frozen vs. fluid constraints
   - **Method 2**: Design Research — interview techniques for claims adjusters and policyholders
   - **Method 3**: Input Synthesis — pattern recognition, theme development, problem statement
   - **Method 4**: Brainstorming — divergent ideation, convergent clustering
   - **Method 5**: User Concepts — concept articulation, three-lens evaluation
4. Each method produces structured artifacts that carry forward to the build.

#### Step 2: Map User Journeys (UX UI Designer)

1. Select **UX UI Designer**.
2. Map the end-user's experience:

```text
Run a Jobs-to-be-Done analysis for a claims adjuster at an insurance company.
Current workflow:
1. Receive claim packet (mix of digital and paper forms)
2. Manually extract key data (claimant, date of loss, amount, policy number)
3. Cross-reference against policy database
4. Write assessment summary
5. Route to supervisor for approval
Average time: 45 minutes per claim. Target: under 10 minutes with AI assistance.
Map the current journey, identify pain points, and propose the future state with AI.
```

3. The agent produces a JTBD analysis, current-state journey map, and future-state journey map.

#### Step 3: Capture Business Requirements (BRD Builder)

1. Select **BRD Builder**.
2. Formalize what you learned in Design Thinking:

```text
Build a Business Requirements Document for Contoso Insurance's AI claims
processing modernization. Based on our Design Thinking workshops:
- Problem: Claims adjusters spend 45 min/claim on data extraction and summarization
- Opportunity: Reduce to 10 min/claim with AI, saving approximately $2M/year
- Stakeholders: VP Claims Ops (sponsor), IT Director (tech owner)
- Customer Zero: MidWest Regional Hospital (processes 200 claims/month)
- Constraints: HIPAA compliance, data residency in US, existing Salesforce CRM
- Success metrics: 80% reduction in data extraction time, 95% extraction accuracy
```

#### Step 4: Sketch the Architecture (Arch Diagram Builder)

1. Select **Arch Diagram Builder**.
2. Produce an early-stage architecture:

```text
Create a high-level architecture diagram for an AI claims processing system.
This is an envisioning-stage sketch, not a final design. Components:
- Claims intake (web portal + mobile app)
- Document processing pipeline (Azure Document Intelligence)
- AI summarization (Azure OpenAI)
- Knowledge base (Azure AI Search over claims history)
- Claims adjuster dashboard (web app)
- Integration with existing Salesforce CRM
Show the major data flows. Mark areas where architecture decisions are still open
(e.g., "App Service vs. Container Apps — TBD in ADS").
```

3. This sketch becomes the starting point for the Architecture Design Session (ADS) in Build to Consume.

#### Step 5: Prioritize Scenarios (Product Manager Advisor)

When the envisioning surfaces multiple possible scenarios, use the Product Manager Advisor to prioritize.

1. Select **Product Manager Advisor**.
2. Present the scenarios for evaluation:

```text
We identified 4 potential AI scenarios for Contoso Insurance during envisioning:
1. Claims document intake automation (Document Intelligence + OCR)
2. Claims summary generation (Azure OpenAI)
3. Customer-facing claims status chatbot (MAF agent)
4. Predictive claims fraud detection (ML model)

Help us prioritize by business impact, technical feasibility, time to market,
and alignment with Azure AI specialization requirements. The partner can
realistically build 2 of these in the first 6 months.
```

3. The agent provides a prioritized recommendation with rationale.

#### Step 6: Record Decisions and Next Steps (Memory + ADR)

1. Select **Memory** to save the envisioning outcomes:

```text
Remember that Contoso Insurance envisioning completed on April 8, 2026.
Prioritized scenarios: (1) Claims document intake automation, (2) Claims
summary generation. Customer zero: MidWest Regional Hospital.
Technical constraints: HIPAA, US data residency, Salesforce CRM integration.
Next step: Architecture Design Session to finalize the technical approach.
```

2. Select **ADR Creation** for key decisions:

```text
Document our decision to prioritize claims document intake automation
over the customer-facing chatbot. The intake automation has 3x higher
ROI ($2M savings vs $600K), lower technical risk (well-understood Azure
Document Intelligence APIs), and faster time to market (3 months vs 5 months).
The chatbot moves to Phase 2 after the first offering is in market.
```

---

## What You Have After Commit to Build

At the end of this stage, you should have produced:

| Deliverable | Artifacts Created with HVE Core |
|---|---|
| Planning | Research brief, PRD, MVP execution plan (validated), MVE results for risky assumptions, sprint cadence |
| Envisioning | DT workshop outputs (Methods 1-5), user journey maps (JTBD), BRD, early-stage architecture sketch, prioritized scenario list, ADRs, partner context in Memory |

These artifacts are the foundation for the **Build to Consume** stage. The PRD feeds the ADS. The execution plan feeds the Build. The DT outputs feed validation. See [Build to Consume How-To](hve-howto-build-to-consume.md) for the next stage.

---

## Key Differences from Pioneer Innovation

| Aspect | Pioneer Innovation | Commit to Build |
|---|---|---|
| **Depth** | Breadth-first: show the art of the possible | Depth-first: commit to specific priorities |
| **Artifacts** | Exploratory (demos, research, diagrams) | Binding (PRDs, plans, MVEs, ADRs) |
| **Stakeholders** | Technical audiences | Executive decision-makers |
| **HVE agents** | Researcher, Arch Diagram Builder, Gen Streamlit | PRD Builder, Task Planner, DT Coach, Plan Validator |
| **Output** | Interest and excitement | Signed-off plan with budget and timeline |

---

*Part 2 of 3 in the HVE How-To series for Partner Solutions Architects*
