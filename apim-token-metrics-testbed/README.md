---
title: "APIM Token Metrics + Audit Logging Testbed"
description: "Testbed for two complementary APIM AI Gateway approaches: token billing via emit-metric and audit logging via Event Hub REST API with managed identity."
author: "Arturo Quiroga"
ms.date: 2026-03-24
ms.topic: how-to
---

## Purpose

Test two complementary APIM AI Gateway approaches for cost-effective billing
and audit logging — without relying on expensive Log Analytics ingestion.

| Approach | Policy | Destination | Use case |
|---|---|---|---|
| **1. Token billing** | `emit-metric` (generic) | App Insights `customMetrics` | Per-tenant token counts for chargeback |
| **2. Audit logging** | `send-request` + managed identity | Azure Event Hub | Full request/response bodies for evaluation |

**Context**: Partner scenario where APIM serves as an AI model gateway for
multiple tenants. Streaming mode prevents traditional request/response logging.
Approach 1 emits token counts as Application Insights custom metrics (cheap).
Approach 2 sends full request bodies to Event Hub for audit (also cheap).

**API**: Uses the **Responses API** (`/openai/v1/responses`) — the newer API
surface that replaces Chat Completions — with **GPT-5.4 mini**
(`reasoning_effort=low`).

> **Important**: This testbed uncovered several non-obvious pitfalls when
> combining APIM, Bicep-provisioned APIs, and token metric emission.
> See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for the full debugging journey
> and the three root causes we discovered.

## Architecture

```text
                                    ┌─────────────────────────┐
                                    │   Application Insights   │
                                    │   customMetrics table    │
                               ┌───▶│ (Approach 1: billing)    │
                               │    └─────────────────────────┘
                               │
┌──────────────┐      ┌────────┴──────────────────────────┐     ┌──────────────────┐
│  Test Client │────▶ │  Azure API Management (APIM)      │────▶│  AI Foundry      │
│  (Python SDK)│      │  POST /openai/v1/responses        │     │  GPT-5.4 mini    │
└──────────────┘      │                                   │     └──────────────────┘
                      │  Policies:                        │
                      │  • emit-metric (token billing)    │
                      │    outbound — parses usage JSON    │
                      │    + 5 custom dimensions           │
                      │  • send-request (audit)            │
                      │    inbound: request body            │
                      │    outbound: response body          │
                      │    (MI auth to Event Hub REST API) │
                      └────────┬──────────────────────────┘
                               │
                               │    ┌─────────────────────────┐
                               └───▶│   Azure Event Hub        │
                                    │   audit-logs             │
                                    │ (Approach 2: audit)      │
                                    └─────────────────────────┘
                      ┌───────────────────────────────────┐
                      │   KQL Queries (validate_metrics.py)│
                      │   • Per-tenant token usage         │
                      │   • Prompt vs completion breakdown │
                      │   • Time series analysis           │
                      └───────────────────────────────────┘
```

## Key technical details

| Aspect | Detail |
|---|---|
| **API** | **Responses API** (`POST /openai/v1/responses`) — not Chat Completions |
| **Model** | `gpt-5.4-mini` with `reasoning_effort=low` (GPT-5.4 family reasoning model) |
| **Approach 1 policy** | `emit-metric` (outbound) — generic policy with manual usage JSON parsing |
| **Approach 2 policy** | `send-request` + `authentication-managed-identity` (inbound + outbound) |
| **Streaming support** | Approach 1: non-streaming only (streaming body unavailable). Approach 2: inbound only (outbound SSE not capturable) |
| **APIM tiers** | All tiers (Consumption, Developer, Basic, Standard, Premium, Basicv2, Standardv2) |
| **Metrics emitted** | Total Tokens, Prompt Tokens, Completion Tokens → App Insights `customMetrics` |
| **Audit events** | Full request body (inbound) + response body (outbound, non-streaming) → Event Hub |
| **Custom dimensions** | Client IP, Tenant ID, Subscription Name, API ID, Subscription ID |
| **Billing destination** | App Insights `customMetrics` table |
| **Audit destination** | Event Hub `audit-logs` (Standard tier, 3-day retention) |
| **Billing cost** | Custom metrics ≈ **$0.00 for first 150M data points/month**, then ~$0.001/1K |
| **Audit cost** | Event Hub Standard ~$11/month base + ~$0.028/million events |
| **Latency** | Metrics: 3–5 min to App Insights. Events: near real-time to Event Hub |

## Why `emit-metric` instead of `azure-openai-emit-token-metric`

This is the single most important lesson from this testbed. We initially tried
both `llm-emit-token-metric` and `azure-openai-emit-token-metric` — neither
emitted any data. After extensive debugging, we found **three root causes**:

### Root cause 1 — API type mismatch (silent failure)

Both `azure-openai-emit-token-metric` and `llm-emit-token-metric` **silently
skip metric emission** when the API is created manually via Bicep or ARM
templates. These policies require the API to be imported through the Azure
OpenAI import flow in the portal, which sets an internal `apiType` property.
Bicep-created APIs have `apiType: http` (the default), and the policies
silently produce zero metrics with no error.

**Evidence**: The APIM diagnostic pipeline was verified working (49 `requests`
and 49 `dependencies` appeared in App Insights), but `customMetrics` was
always empty. Checking the API via REST API confirmed:

```json
{
  "apiType": null,
  "type": "http"
}
```

### Root cause 2 — Missing `metrics: true` on diagnostic

The `emit-metric` policy requires the `applicationinsights` diagnostic entity
to have `"metrics": true` explicitly set. This property is **not set by
default** when you create the diagnostic via Bicep or REST API. Without it,
`emit-metric` calls succeed silently but data never reaches App Insights.

This requirement is documented in the
[Emit custom metrics](https://learn.microsoft.com/azure/api-management/api-management-howto-app-insights#emit-custom-metrics)
section, but it is easy to miss.

**Fix in Bicep**:

```bicep
resource apimDiagnostic 'Microsoft.ApiManagement/service/diagnostics@2024-05-01' = {
  parent: apim
  name: 'applicationinsights'
  properties: {
    loggerId: apimLogger.id
    alwaysLog: 'allErrors'
    sampling: {
      samplingType: 'fixed'
      percentage: 100
    }
    metrics: true  // <-- REQUIRED for emit-metric to flow data
  }
}
```

### Root cause 3 — Streaming response body read crash

Both approaches tried to read `context.Response.Body?.As<string>(preserveContent: true)`
unconditionally in the outbound section. For SSE streaming responses
(`Content-Type: text/event-stream`), this call throws an exception and causes
a **500 Internal Server Error** returned to the client.

**Fix**: Check the Content-Type header before reading the body:

```xml
<set-variable name="is-streaming"
  value="@(context.Response.Headers.GetValueOrDefault(
    &quot;Content-Type&quot;,&quot;&quot;).Contains(&quot;text/event-stream&quot;))" />
<choose>
  <when condition="@(!context.Variables.GetValueOrDefault&lt;bool&gt;(
    &quot;is-streaming&quot;))">
    <!-- Safe to read response body here -->
  </when>
</choose>
```

### The solution

Use the **generic `emit-metric` policy** in the outbound section. This policy
works regardless of API type. We parse the `usage` JSON from the response body
manually, supporting both the Responses API (`input_tokens`/`output_tokens`)
and Chat Completions API (`prompt_tokens`/`completion_tokens`).

For streaming requests, metric emission is skipped because the SSE response
body cannot be read in the outbound section.

## Why `send-request` instead of `log-to-eventhub`

MCAPS policy (Microsoft corporate subscription governance) enforces
`disableLocalAuth: true` on Event Hub namespaces, which disables SAS keys
and connection strings. The `log-to-eventhub` policy requires a SAS-based
logger, so it cannot work in MCAPS subscriptions.

**Fix**: Use `send-request` with `authentication-managed-identity` to call the
Event Hub REST API directly. APIM's system-assigned managed identity
authenticates via Microsoft Entra ID — no SAS key needed.

## Prerequisites

- Azure CLI (`az`) logged in with a subscription that has permission to
  create resources
- Python 3.10+ with `pip`
- `jq` (for deploy script output parsing)

## Quick start

### 1. Configure

Edit [main.parameters.json](main.parameters.json) — update `apimPublisherEmail`
with your email.

### 2. Deploy

```bash
cd apim-token-metrics-testbed
./deploy.sh
```

This creates:

- Resource group `rg-apim-token-metrics-testbed`
- Log Analytics workspace
- Application Insights (with `customMetricsOptedInType: WithDimensions`)
- Event Hub namespace + `audit-logs` hub (Standard tier)
- APIM instance (Basicv2) with combined policy (`emit-metric` + `send-request`)
  and Responses API operations
- AI Services account with `gpt-5.4-mini` deployment (reasoning model)
- 3 APIM subscriptions (tenant-a, tenant-b, tenant-c) for multi-tenant testing
- APIM `applicationinsights` diagnostic with `metrics: true`

> **Note**: APIM provisioning takes ~10–15 minutes. RBAC propagation needs
> ~5 minutes after that.
- Event Hub Namespace + `audit-logs` hub (Standard tier) — Approach 2 destination
- APIM instance (Basicv2) with combined policy (both `llm-emit-token-metric` + `log-to-eventhub`) and Responses API operations
- AI Services account with `gpt-5.4-mini` deployment (reasoning model)
- 3 APIM subscriptions (tenant-a, tenant-b, tenant-c) for multi-tenant testing

**Note**: APIM provisioning takes ~10-15 minutes. RBAC propagation needs ~5 minutes after that.

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Run tests

```bash
# Non-streaming tests (basic validation)
python test_token_metrics.py \
  --gateway-url https://apim-xxx.azure-api.net \
  --api-key YOUR_KEY

# All tests (non-streaming + streaming, HTTP + SDK)
python test_token_metrics.py \
  --gateway-url https://apim-xxx.azure-api.net \
  --api-key YOUR_KEY --all

# Multi-tenant test
python test_token_metrics.py \
  --gateway-url https://apim-xxx.azure-api.net \
  --api-key YOUR_KEY --all \
  --multi-tenant-keys '{"tenant-a":"KEY_A","tenant-b":"KEY_B"}'
```

### 5. Validate metrics (wait 3–5 minutes after tests)

```bash
# Run all validation queries
python validate_metrics.py \
  --resource-group rg-apim-token-metrics-testbed \
  --app-insights-name appi-XXXXX

# Run a specific query
python validate_metrics.py \
  --resource-group rg-apim-token-metrics-testbed \
  --app-insights-name appi-XXXXX \
  --query total_tokens_summary

# Export results
python validate_metrics.py \
  --resource-group rg-apim-token-metrics-testbed \
  --app-insights-name appi-XXXXX \
  --export results.json
```

Available validation queries:

- `total_tokens_summary` — Token totals grouped by subscription, user,
  cost center
- `prompt_vs_completion` — Breakdown of prompt vs completion tokens per
  subscription
- `tokens_over_time` — Time series of token usage (5-min buckets)
- `all_dimensions_check` — Verify all custom dimensions are populated
- `streaming_vs_nonstreaming` — Compare metrics across operation types

### 6. Cleanup

```bash
./cleanup.sh
```

## Files

| File | Purpose |
|---|---|
| `main.bicep` | IaC: APIM, App Insights, Event Hub, AI Services, RBAC, diagnostic with `metrics: true` |
| `main.parameters.json` | Deployment parameters (SKU, region, model, tenants) |
| `policy.xml` | Combined policy: `emit-metric` (token billing) + `send-request` (Event Hub audit) |
| `deploy.sh` | One-click deploy script (creates RG, deploys Bicep, fetches keys) |
| `test_token_metrics.py` | Responses API test client: non-streaming, streaming, HTTP, SDK |
| `validate_metrics.py` | KQL queries to verify metrics in App Insights `customMetrics` |
| `cleanup.sh` | Delete all test resources |
| `requirements.txt` | Python dependencies |
| `TROUBLESHOOTING.md` | Full debugging journey and root cause analysis |

## What to look for

### Approach 1 — Token billing (App Insights)

1. **Metrics appear for non-streaming calls** — Verify `customMetrics` table
   has entries with metric names "Total Tokens", "Prompt Tokens", "Completion
   Tokens".
2. **Token counts are reasonable** — Compare totals against the model's
   reported usage in the test output.
3. **Custom dimensions populated** — Client IP, Tenant ID, Subscription Name,
   API ID, Subscription ID should all appear in `customDimensions`.
4. **Per-subscription segregation** — Different APIM subscriptions (tenant-a/b/c)
   appear as distinct Subscription ID dimension values.
5. **Streaming calls are gracefully skipped** — Streaming requests return 200
   (not 500) without emitting metrics. No exception in App Insights.

### Approach 2 — Audit logging (Event Hub)

6. **Inbound events captured** — Full request bodies (prompts) appear in Event
   Hub `audit-logs`.
7. **Outbound events for non-streaming** — Response bodies captured for
   non-streaming calls.
8. **Streaming caveat** — Outbound events for streaming calls are skipped
   entirely (SSE single-consumer limitation). This is expected.
9. **Managed identity auth working** — Events arrive despite `disableLocalAuth: true`
   on the Event Hub namespace.

### Both approaches

10. **Responses API compatibility** — Confirm both policies work correctly with
    `/v1/responses` (preview support).
11. **Cost at scale** — Custom metrics: ~150M free data points/month.
    Event Hub: ~$11/month + $0.028/million events. Compare vs Log Analytics at
    $2.76/GB.

## References

- [emit-metric policy reference](https://learn.microsoft.com/azure/api-management/emit-metric-policy)
- [Emit custom metrics (App Insights integration)](https://learn.microsoft.com/azure/api-management/api-management-howto-app-insights#emit-custom-metrics) — **critical**: documents the `metrics: true` prerequisite
- [send-request policy reference](https://learn.microsoft.com/azure/api-management/send-request-policy)
- [Event Hub REST API](https://learn.microsoft.com/azure/event-hubs/event-hubs-rest-api)
- [azure-openai-emit-token-metric policy](https://learn.microsoft.com/azure/api-management/azure-openai-emit-token-metric-policy) — requires portal-imported API
- [llm-emit-token-metric policy](https://learn.microsoft.com/azure/api-management/llm-emit-token-metric-policy) — requires portal-imported API
- [Azure OpenAI Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses)
- [Monitor and log LLM token usage](https://learn.microsoft.com/azure/api-management/api-management-howto-llm-logs)
- [GenAI Gateway capabilities in APIM](https://learn.microsoft.com/azure/api-management/genai-gateway-capabilities)
- [Azure-Samples/ai-gateway (token-metrics-emitting lab)](https://github.com/Azure-Samples/ai-gateway/tree/main/labs/token-metrics-emitting)
