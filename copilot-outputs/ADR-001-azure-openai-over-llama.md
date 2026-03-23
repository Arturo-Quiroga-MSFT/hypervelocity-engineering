---
title: "ADR-001: Azure OpenAI over Self-Hosted Llama for Customer Support Agent"
description: "Architecture decision record selecting Azure OpenAI as the LLM provider for the partner's customer support agent"
author: PSA Team
ms.date: 2026-03-21
ms.topic: concept
keywords:
  - adr
  - azure openai
  - llama
  - customer support
  - llm selection
status: Accepted
---

## Context

The partner requires an LLM to power their customer support agent, which handles customer queries using a RAG pattern backed by Azure AI Search. The agent must operate in a regulated environment where compliance, uptime guarantees, and content safety are non-negotiable.

The partner's engineering team has strong application development skills but no dedicated ML operations staff. They need a solution that minimizes operational overhead while meeting enterprise requirements.

Two candidates were evaluated: Azure OpenAI Service (managed GPT-4o) and a self-hosted Meta Llama model on Azure Kubernetes Service or Azure Machine Learning.

## Decision

We selected **Azure OpenAI Service** with a GPT-4o deployment as the LLM provider for the customer support agent.

## Alternatives Considered

### Option A: Azure OpenAI Service (GPT-4o) — Selected

A fully managed service providing REST API access to GPT-4o with built-in content filtering, enterprise SLA, and native integration with Azure AI Search.

**Strengths:**

- 99.9% SLA with financially backed uptime guarantees
- Built-in content filtering (Azure AI Content Safety) satisfies compliance without additional tooling
- Managed scaling via Provisioned Throughput Units (PTU) or pay-as-you-go token-based pricing
- Native "On Your Data" integration with Azure AI Search (though migrating to Foundry Agent Service)
- No infrastructure to manage: no GPU provisioning, no model versioning, no patching
- RBAC and private endpoints via Azure networking

**Weaknesses:**

- Per-token cost is higher than self-hosted at sustained high volume
- Model selection limited to OpenAI's catalog (no custom fine-tuned open-source models)
- Data residency depends on Azure OpenAI regional availability

### Option B: Self-Hosted Llama on AKS or Azure ML

Deploying Meta's Llama 3 (or newer) on Azure infrastructure using Azure Kubernetes Service with GPU node pools or Azure Machine Learning managed endpoints.

**Strengths:**

- Lower per-token cost at high sustained throughput (after amortizing GPU costs)
- Full model customization: fine-tuning, LoRA adapters, custom tokenizers
- No vendor lock-in to OpenAI's API surface
- Data never leaves the partner's own compute boundary

**Weaknesses:**

- Requires GPU capacity planning, node pool management, and model deployment pipelines
- No built-in content filtering; the partner would need to build or integrate a separate safety layer
- No managed SLA on model inference quality or latency; SLA only covers infrastructure uptime
- The partner lacks an ML ops team to handle model updates, A/B testing, and monitoring
- Cold start and autoscaling complexity with GPU workloads

## Rationale

Three factors drove this decision:

1. **Enterprise SLA:** The partner's customer support system is customer-facing in production. A 99.9% financially backed SLA from Azure OpenAI eliminates the risk of self-managed GPU infrastructure outages. The partner cannot staff an on-call rotation for model serving issues.

2. **Compliance and content filtering:** The partner operates in a regulated industry. Azure AI Content Safety provides configurable severity filters for hate, violence, self-harm, and sexual content out of the box. Building equivalent filtering on a self-hosted Llama deployment would require months of additional engineering and ongoing maintenance.

3. **Operational burden:** Without a dedicated ML ops team, the partner would need to hire or retrain staff to manage model deployments, GPU scaling, model versioning, and inference monitoring. Azure OpenAI offloads all of this to the platform.

The cost premium of Azure OpenAI (roughly 2–4x per token vs. self-hosted at scale) is acceptable given the partner's moderate query volume (estimated 10K–50K queries/day) and the operational savings from not maintaining GPU infrastructure.

## Consequences

### Positive

- The partner's engineering team can focus on application logic rather than model infrastructure
- Time-to-production is reduced by 4–6 weeks compared to a self-hosted deployment
- Content safety compliance is addressed at the platform level from day one
- Integration with Azure AI Search, Azure Monitor, and Microsoft Entra ID is native

### Negative

- At volumes exceeding 100K queries/day, the cost differential with self-hosted becomes significant; the partner should revisit this decision at that scale
- The partner depends on Azure OpenAI model availability and deprecation timelines (GPT-4o lifecycle)
- Fine-tuning options are limited compared to full control over an open-source model

### Mitigations

- Monitor token consumption monthly; set up Azure Cost Management alerts at 75% of budget threshold
- Abstract the LLM client behind an interface so switching providers (or adding a self-hosted fallback) requires minimal code changes
- Track Azure OpenAI model deprecation announcements and plan migration windows quarterly

## Related Decisions

- ADR-002 (pending): Selection of Azure AI Search tier and indexing strategy
- ADR-003 (pending): Authentication model (Entra ID vs. API key rotation)
