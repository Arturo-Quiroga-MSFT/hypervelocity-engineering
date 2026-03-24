# APIM Token Metrics + Audit Logging Test Bed

**Purpose**: Test two complementary APIM AI Gateway approaches for cost-effective billing and audit logging in streaming mode — without relying on expensive Log Analytics ingestion.

| Approach | Policy | Destination | Use Case |
|---|---|---|---|
| **1. Token Billing** | `llm-emit-token-metric` | App Insights custom metrics | Per-tenant token counts for chargeback |
| **2. Audit Logging** | `log-to-eventhub` | Azure Event Hub | Full request/response bodies for evaluation |

**Context**: Partner scenario where APIM serves as an AI model gateway for multiple tenants. Streaming mode prevents traditional request/response logging. Approach 1 emits token counts as Application Insights **custom metrics** (cheap). Approach 2 sends full request bodies to Event Hub for audit (also cheap).

**API**: Uses the **Responses API** (`/openai/v1/responses`) — the newer API surface that replaces Chat Completions — with **GPT-5.4 mini** (`reasoning_effort=low`).

---

## Architecture

```
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
                      │  • llm-emit-token-metric (billing)│
                      │    + 5 custom dimensions          │
                      │  • log-to-eventhub (audit)        │
                      │    inbound: request body           │
                      │    outbound: response body         │
                      └────────┬──────────────────────────┘
                               │
                               │    ┌─────────────────────────┐
                               └───▶│   Azure Event Hub        │
                                    │   audit-logs             │
                                    │ (Approach 2: audit)      │
                                    └─────────────────────────┘
                      ┌───────────────────────────────────┐
                      │   Application Insights            │
                      │   customMetrics table             │
                      │   (WithDimensions enabled)        │
                      └───────────────┬───────────────────┘
                                      │
                                      ▼
                      ┌─────────────────────────────────── ┐
                      │   KQL Queries (validate_metrics.py)│
                      │   • Per-tenant token usage         │
                      │   • Prompt vs completion breakdown │
                      │   • Time series analysis           │
                      └───────────────────────────────────┘
```

## Key Technical Details

| Aspect | Detail |
|---|---|
| **API** | **Responses API** (`POST /openai/v1/responses`) — not Chat Completions |
| **Model** | `gpt-5.4-mini` with `reasoning_effort=low` (GPT-5.4 family reasoning model) |
| **Approach 1 policy** | `llm-emit-token-metric` (inbound) — supports Responses API (preview) |
| **Approach 2 policy** | `log-to-eventhub` (inbound + outbound) — full request/response audit |
| **Streaming support** | Approach 1: Yes (tokens estimated). Approach 2: Inbound only (outbound SSE not capturable) |
| **APIM tiers** | All tiers (Consumption, Developer, Basic, Standard, Premium, Basicv2, Standardv2) |
| **Metrics emitted** | Total Tokens, Input Tokens, Output Tokens → App Insights custom metrics |
| **Audit events** | Full request body (inbound) + response body (outbound, non-streaming) → Event Hub |
| **Default dimensions** | API ID, Operation ID, Product ID, User ID, Subscription ID, Location, Gateway ID, Backend ID |
| **Custom dimensions** | Up to 5 per policy (we use: Tenant ID, Client IP, User ID, Cost Center, Environment) |
| **Billing destination** | App Insights `customMetrics` table |
| **Audit destination** | Event Hub `audit-logs` (Standard tier, 3-day retention) |
| **Billing cost** | Custom metrics ≈ **$0.00 for first 150M data points/month**, then ~$0.001/1K |
| **Audit cost** | Event Hub Standard ~$11/month base + ~$0.028/million events |
| **Latency** | Metrics: 3-5 min to App Insights. Events: near real-time to Event Hub |

## Prerequisites

- Azure CLI (`az`) logged in with a subscription that has permission to create resources
- Python 3.10+ with `pip`
- `jq` (for deploy script output parsing)

## Quick Start

### 1. Configure

Edit [main.parameters.json](main.parameters.json) — update `apimPublisherEmail` with your email.

### 2. Deploy

```bash
cd apim-token-metrics-testbed
./deploy.sh
```

This creates:

- Resource group `rg-apim-token-metrics-testbed`
- Log Analytics Workspace
- Application Insights (with `customMetricsOptedInType: WithDimensions`) — Approach 1 destination
- Event Hub Namespace + `audit-logs` hub (Standard tier) — Approach 2 destination
- APIM instance (Basicv2) with combined policy (both `llm-emit-token-metric` + `log-to-eventhub`) and Responses API operations
- AI Services account with `gpt-5.4-mini` deployment (reasoning model)
- 3 APIM subscriptions (tenant-a, tenant-b, tenant-c) for multi-tenant testing

**Note**: APIM provisioning takes ~10-15 minutes. RBAC propagation needs ~5 minutes after that.

### 3. Install Python deps

```bash
pip install -r requirements.txt
```

### 4. Run Tests

```bash
# Non-streaming tests (basic validation)
python test_token_metrics.py --gateway-url https://apim-xxx.azure-api.net --api-key YOUR_KEY

# Streaming tests (the critical scenario)
python test_token_metrics.py --gateway-url https://apim-xxx.azure-api.net --api-key YOUR_KEY --streaming

# All tests
python test_token_metrics.py --gateway-url https://apim-xxx.azure-api.net --api-key YOUR_KEY --all

# Multi-tenant test (pass JSON dict of tenant:key pairs)
python test_token_metrics.py \
  --gateway-url https://apim-xxx.azure-api.net \
  --api-key YOUR_KEY \
  --all \
  --multi-tenant-keys '{"tenant-a":"KEY_A","tenant-b":"KEY_B","tenant-c":"KEY_C"}'
```

### 5. Validate Metrics (wait 3-5 min after tests)

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
- `total_tokens_summary` — Token totals grouped by subscription, user, cost center
- `prompt_vs_completion` — Breakdown of prompt vs completion tokens per subscription
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
| `main.bicep` | IaC: APIM, App Insights, Event Hub, AI Services (gpt-5.4-mini), RBAC, subscriptions |
| `main.parameters.json` | Deployment parameters (SKU, region, model, tenants) |
| `policy.xml` | Combined policy: `llm-emit-token-metric` (billing) + `log-to-eventhub` (audit) |
| `deploy.sh` | One-click deploy script (creates RG, deploys Bicep, fetches keys) |
| `test_token_metrics.py` | Responses API test client: non-streaming, streaming, SDK, multi-tenant |
| `validate_metrics.py` | KQL queries to verify metrics in App Insights |
| `cleanup.sh` | Delete all test resources |
| `requirements.txt` | Python dependencies |

## What to Look For

### Approach 1 — Token Billing (App Insights)

1. **Metrics appear for streaming calls** — The whole point. Verify `customMetrics` table has entries from streaming Responses API requests.
2. **Token counts are reasonable** — Streaming uses estimation; compare with non-streaming actuals.
3. **Custom dimensions populated** — Tenant ID, Client IP, User ID, Cost Center, Environment should all appear.
4. **Per-subscription segregation** — Different APIM subscriptions (tenant-a/b/c) appear as distinct `Subscription ID` dimension values.

### Approach 2 — Audit Logging (Event Hub)

5. **Inbound events captured** — Full request bodies (prompts) appear in Event Hub `audit-logs`.
6. **Outbound events for non-streaming** — Response bodies captured for non-streaming calls.
7. **Streaming caveat** — Outbound events for streaming calls have empty/partial response bodies (SSE single-consumer limitation). This is expected.
8. **Tenant headers propagated** — `TenantId`, `UserId`, `CostCenter` fields in Event Hub events match the request headers.

### Both Approaches

9. **Responses API compatibility** — Confirm both policies work correctly with `/v1/responses` (preview support).
10. **Cost at scale** — Custom metrics: ~150M free data points/month. Event Hub: ~$11/month + $0.028/million events. Compare vs Log Analytics at $2.76/GB.

## References

- [llm-emit-token-metric policy reference](https://learn.microsoft.com/azure/api-management/llm-emit-token-metric-policy)
- [log-to-eventhub policy reference](https://learn.microsoft.com/azure/api-management/api-management-howto-log-event-hubs)
- [Azure OpenAI Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses)
- [Monitor and log LLM token usage](https://learn.microsoft.com/azure/api-management/api-management-howto-llm-logs)
- [GenAI Gateway capabilities in APIM](https://learn.microsoft.com/azure/api-management/genai-gateway-capabilities)
- [Azure-Samples/ai-gateway (token-metrics-emitting lab)](https://github.com/Azure-Samples/ai-gateway/tree/main/labs/token-metrics-emitting)
