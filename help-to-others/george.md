---
title: "Helping George: APIM AI Gateway Streaming Logging & Billing"
description: Notes and recommended approaches for George Bittencourt's partner (Blip, Brazil) facing expensive Log Analytics costs when using APIM as an AI model gateway in streaming mode.
author: Arturo Quiroga
ms.date: 2026-03-24
---

## Problem Statement

**From George Bittencourt:** I'm facing an issue with a partner in Brazil who wants to use APIM as a model gateway. At the moment, logging requests in streaming mode is only possible through Log Analytics, which can become expensive in high-volume situations. I've already raised this with the product team, and they plan to support log pushing with OTel. As more SDC partners use this for billing, it could become a concern. The partner is Blip. This is the only partner where I've noticed this issue so far, but it's also the only one I'm working with to deploy APIM as an AI Gateway. I think this "issue" will likely occur with other partners as well.

**Response/question from Ellie Nosrat to George:** George how are they going around this? Like are they using an APIM inbound policy to forward request metadata to Azure Event Hub. From there, a stream-processing pipeline (e.g., Azure Functions) can potentially handle real-time logging and storage for billing purposes.

---

## Arturo's Research & Recommended Approaches

After reviewing this workspace's existing architecture patterns, Microsoft documentation, and community solutions, here are three concrete approaches George can share with Blip, ordered from lightest to most comprehensive.

### Approach 1: `llm-emit-token-metric` Policy (Simplest, No Event Hub Needed)

APIM now has a built-in LLM token metric emission policy that works with **both streaming and non-streaming** responses. This is the lowest-effort option and may already solve Blip's billing/metering problem without Event Hub at all.

```xml
<llm-emit-token-metric namespace="llm-metrics">
    <dimension name="Client IP" value="@(context.Request.IpAddress)" />
    <dimension name="API ID" value="@(context.Api.Id)" />
    <dimension name="Subscription" value="@(context.Subscription.Id)" />
    <dimension name="User ID" value="@(context.Request.Headers.GetValueOrDefault("x-user-id", "N/A"))" />
</llm-emit-token-metric>
```

* Emits `Total Tokens`, `Prompt Tokens`, and `Completion Tokens` as custom metrics to Application Insights
* Supports **streaming** ChatCompletions (completion tokens are estimated during stream)
* Custom dimensions allow slicing by team, app, subscription, or any arbitrary key
* Metrics can be visualized via the built-in APIM analytics workbook or Azure Monitor dashboards
* Cost impact: Application Insights custom metrics are significantly cheaper than raw Log Analytics log ingestion at high volume

**Docs:**

* [Emit token consumption metrics](https://learn.microsoft.com/azure/api-management/llm-emit-token-metric-policy)
* [Logging token usage, prompts, and completions](https://learn.microsoft.com/azure/api-management/api-management-howto-llm-logs)

**When to use:** If Blip only needs token-level billing/metering per consumer (not full request/response body logging), this approach avoids Log Analytics costs entirely.

### Approach 2: `log-to-eventhub` Policy (Ellie's Suggestion, Production-Grade)

This is the pattern Ellie suggested. APIM has a native `log-to-eventhub` policy that can send request metadata to Event Hub on every API call:

```text
Client --> APIM (inbound policy: log-to-eventhub) --> Azure Event Hub
                                                   --> Azure Functions (aggregate/transform)
                                                   --> Blob Storage / SQL / Cosmos DB (billing records)
```

```xml
<log-to-eventhub logger-id="billing-logger">
    @{
        return new JObject(
            new JProperty("EventTime", DateTime.UtcNow.ToString()),
            new JProperty("RequestId", context.RequestId),
            new JProperty("SubscriptionId", context.Subscription.Id),
            new JProperty("ApiId", context.Api.Id),
            new JProperty("OperationName", context.Operation.Name),
            new JProperty("ClientIP", context.Request.IpAddress),
            new JProperty("UserId", context.Request.Headers.GetValueOrDefault("x-user-id", "N/A"))
        ).ToString();
    }
</log-to-eventhub>
```

**Key considerations:**

* Event Hub Standard tier costs ~$11/month base + ~$0.028/million events (vastly cheaper than Log Analytics at scale)
* Event Hub is designed for millions of events/second and decouples log production from consumption
* Max message size is 200 KB per event (truncated automatically if exceeded)
* Downstream Azure Functions can aggregate, enrich with token counts, and store to cheaper storage (Blob, SQL)
* This runs in the **inbound** section so it does not interfere with the streaming response

**The streaming response challenge:** The `log-to-eventhub` policy works well for request metadata in the inbound section. For **response body** logging in streaming mode, there is a known challenge: SSE streams support only one subscriber, so consuming the stream for logging would prevent the client from receiving it. See Approach 3 for a solution.

**Docs:**

* [How to log events to Azure Event Hubs in APIM](https://learn.microsoft.com/azure/api-management/api-management-howto-log-event-hubs)
* [Monitor APIs with APIM, Event Hubs, and Moesif](https://learn.microsoft.com/azure/api-management/api-management-log-to-eventhub-sample)
* [GenAI gateway reference architecture: Monitoring via Custom Events](https://learn.microsoft.com/ai/playbook/solutions/genai-gateway/reference-architectures/apim-based#reference-design-for-key-individual-capabilities)

**When to use:** If Blip needs request-level audit trails, custom aggregation, or needs to feed billing data into a third-party system.

### Approach 3: Azure Function Proxy Pattern (Full Streaming + Logging)

For full response body logging in streaming mode, there is a documented pattern using a lightweight Azure Function as a proxy between APIM and Azure OpenAI:

```text
Client --> APIM --> Azure Function Proxy --> Azure OpenAI
                         |
                         +--> Event Hub (complete request/response + token counts)
```

The Function uses FastAPI's `StreamingResponse` to tee the SSE stream: one copy flows back to the client, the other gets buffered and logged to Event Hub. This is the approach documented in the Microsoft Tech Community post [Implementing Event Hub Logging for Azure OpenAI Streaming APIs](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/implementing-event-hub-logging-for-azure-openai-streaming-apis/4296593).

**When to use:** If Blip requires full prompt/completion body logging in streaming mode for compliance, debugging, or detailed billing reconciliation.

### Cost Comparison Summary

| Approach                   | Streaming Support | Data Captured                   | Approximate Monthly Cost (High Volume) |
|----------------------------|-------------------|---------------------------------|----------------------------------------|
| Log Analytics only         | Limited           | Full logs                       | $$$ (per-GB ingestion, expensive)      |
| `llm-emit-token-metric`   | Yes (estimated)   | Token counts + dimensions       | $ (custom metrics, very cheap)         |
| `log-to-eventhub` inbound | Yes (metadata)    | Request metadata                | $ (Event Hub + Functions)              |
| Function Proxy + Event Hub | Yes (full)        | Full request/response + tokens  | $$ (Functions compute + Event Hub)     |

### What Exists in This Workspace

The architecture patterns in this repo already showcase APIM as the AI gateway front door:

* [copilot-outputs/customer-support-app-architecture.md](../copilot-outputs/customer-support-app-architecture.md) shows APIM with rate limiting, auth, and analytics
* [copilot-outputs/profisee-mdm-insights-architecture-diagram.md](../copilot-outputs/profisee-mdm-insights-architecture-diagram.md) includes APIM + Azure Monitor observability patterns
* [copilot-outputs/profisee-azure-infrastructure.bicep](../copilot-outputs/profisee-azure-infrastructure.bicep) has reusable Bicep for Log Analytics + App Insights provisioning (could be extended with Event Hub resources)

### Recommendation for George

1. **Start with Approach 1** (`llm-emit-token-metric`). It is zero-infrastructure overhead, works with streaming, and may fully address the billing/metering use case. Share the policy snippet above.
2. **If Blip needs audit-level logging**, layer in Approach 2 (`log-to-eventhub`) for inbound request metadata.
3. **If full streaming response capture is required**, evaluate Approach 3 (Function Proxy), referencing the Microsoft Tech Community post above.
4. **For the longer term**, the OTel support George mentioned is on the product roadmap and would provide native, cost-efficient telemetry export. Once available, it replaces the need for custom Event Hub plumbing.

---

## George's Follow-Up (2026-03-24)

> The `llm-emit-token-metric` is one that I thought about, but I didn't test. We need to extract a few information from the request headers to identify the tenant. In addition, they want to save the request for audit/evaluations purposes as well.
>
> I talked to the PM and he said to me they are working to have a second way to push the metrics using OTel.

### Analysis: Two Distinct Requirements

George's feedback confirms Blip has **two separate needs** that require different mechanisms:

| Need | What Solves It | Approach |
|---|---|---|
| **Billing/metering per tenant** (token counts, tenant identity from headers) | `llm-emit-token-metric` with custom dimensions | Approach 1 |
| **Audit/evaluation logging** (full request prompts and responses saved) | `log-to-eventhub` in inbound + outbound sections | Approach 2 |

These are not mutually exclusive. The recommended architecture combines both policies in the same APIM policy file.

### Tenant Identification from Headers: Already Supported

The `llm-emit-token-metric` policy supports up to **5 custom dimensions** extracted from request headers, context variables, or expressions. Here is a concrete example tailored for Blip's multi-tenant scenario:

```xml
<policies>
    <inbound>
        <base />
        <set-backend-service backend-id="ai-backend" />
        <authentication-managed-identity resource="https://cognitiveservices.azure.com" />

        <!-- BILLING: Token metrics with tenant dimensions from headers -->
        <llm-emit-token-metric>
            <dimension name="Tenant ID"
                       value="@(context.Request.Headers.GetValueOrDefault("x-tenant-id", "unknown"))" />
            <dimension name="App ID"
                       value="@(context.Request.Headers.GetValueOrDefault("x-app-id", "unknown"))" />
            <dimension name="Environment"
                       value="@(context.Request.Headers.GetValueOrDefault("x-environment", "production"))" />
            <dimension name="Client IP"
                       value="@(context.Request.IpAddress)" />
        </llm-emit-token-metric>

        <!-- AUDIT: Log full request body to Event Hub for evaluation -->
        <log-to-eventhub logger-id="audit-logger">
            @{
                var body = context.Request.Body?.As<string>(preserveContent: true);
                return new JObject(
                    new JProperty("EventTime", DateTime.UtcNow.ToString("o")),
                    new JProperty("Direction", "request"),
                    new JProperty("RequestId", context.RequestId),
                    new JProperty("TenantId", context.Request.Headers.GetValueOrDefault("x-tenant-id", "unknown")),
                    new JProperty("AppId", context.Request.Headers.GetValueOrDefault("x-app-id", "unknown")),
                    new JProperty("SubscriptionId", context.Subscription.Id),
                    new JProperty("ApiId", context.Api.Id),
                    new JProperty("OperationName", context.Operation.Name),
                    new JProperty("ClientIP", context.Request.IpAddress),
                    new JProperty("RequestBody", body)
                ).ToString();
            }
        </log-to-eventhub>

    </inbound>
    <backend>
        <base />
    </backend>
    <outbound>
        <base />

        <!-- AUDIT: Log response body to Event Hub (works for non-streaming) -->
        <log-to-eventhub logger-id="audit-logger">
            @{
                var body = context.Response.Body?.As<string>(preserveContent: true);
                return new JObject(
                    new JProperty("EventTime", DateTime.UtcNow.ToString("o")),
                    new JProperty("Direction", "response"),
                    new JProperty("RequestId", context.RequestId),
                    new JProperty("TenantId", context.Request.Headers.GetValueOrDefault("x-tenant-id", "unknown")),
                    new JProperty("StatusCode", context.Response.StatusCode),
                    new JProperty("ResponseBody", body)
                ).ToString();
            }
        </log-to-eventhub>

    </outbound>
    <on-error>
        <base />
    </on-error>
</policies>
```

### Combined Architecture for Blip

```text
                                    ┌─────────────────────────┐
                                    │   Application Insights   │
                                    │   customMetrics table    │
                               ┌───▶│   (token billing data)   │
                               │    └─────────────────────────┘
                               │
Client ──▶ APIM Gateway ───────┤───▶ Azure OpenAI / AI Foundry
           │                   │
           │ Policy:           │    ┌─────────────────────────┐
           │ • llm-emit-       │    │   Azure Event Hub        │
           │   token-metric    └───▶│   (audit log stream)     │
           │ • log-to-eventhub      │         │                │
           │                        └─────────┼───────────────┘
           │                                  ▼
           │                        ┌─────────────────────────┐
           │                        │ Azure Function / Stream  │
           │                        │ Analytics (optional)     │
           │                        │   ▼                      │
           │                        │ Blob / Cosmos / SQL      │
           │                        │ (audit archive)          │
           │                        └─────────────────────────┘
```

**How the two policies work together:**

* `llm-emit-token-metric` runs in **inbound** and automatically tracks the full request–response lifecycle. It emits `Total Tokens`, `Input Tokens`, and `Output Tokens` as custom metrics to Application Insights with the tenant dimensions. This handles billing. Works with streaming (tokens estimated).
* `log-to-eventhub` runs in **inbound** (captures the request body/prompt) and **outbound** (captures the response body). Event Hub events include the tenant headers. A downstream Azure Function or Stream Analytics job writes these to cheap, durable storage (Blob, Cosmos, SQL) for audit and evaluation review.

### Streaming Caveat for Audit Logging

The `log-to-eventhub` outbound policy can capture response bodies for **non-streaming** calls. For **streaming** calls, the outbound `context.Response.Body` is an SSE stream that can only be consumed once, so the response body is not available for logging in the outbound section.

Two practical options for streaming audit:

1. **Log only the inbound request** (prompts) to Event Hub. For evaluation purposes, the prompt is often the primary artifact needed. Token counts from `llm-emit-token-metric` provide the completion-side data.
2. **Use the Function Proxy pattern** (Approach 3) if full streaming response capture is truly required. The proxy tees the SSE stream so both the client and the audit log receive the complete response.

For most evaluation workflows, option 1 is sufficient: the prompts are logged via Event Hub, and the token counts/dimensions are in App Insights. Full replays can be done by re-submitting the logged prompts.

### OTel Roadmap Confirmation

George confirmed the PM is actively working on OTel push support for APIM. When this ships, it will provide a native, standards-based export path that can replace the `log-to-eventhub` plumbing for audit logging. The `llm-emit-token-metric` policy for billing metrics will likely remain valuable regardless, since it is purpose-built for token-level cost attribution.

### Updated Recommendation for George

1. **Deploy `llm-emit-token-metric` now** for billing/metering. It already supports tenant identification from request headers via custom dimensions. See the policy snippet above. A ready-to-deploy test bed is available at [apim-token-metrics-testbed/](../apim-token-metrics-testbed/) using the Responses API with GPT-5.4 mini.
2. **Add `log-to-eventhub` in the same policy** for audit logging. Log full request bodies (prompts) on inbound. Log response bodies on outbound for non-streaming calls. Pipe to cheap storage (Blob/Cosmos) via Azure Functions.
3. **For streaming audit**, evaluate whether inbound-only logging (prompts + token metrics) meets Blip's evaluation needs. If full streaming response capture is required, layer in the Function Proxy (Approach 3).
4. **Wait for OTel push** as a longer-term simplification of the audit pipeline once the product team ships it.