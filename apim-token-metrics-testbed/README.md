# APIM Token Metrics Test Bed

**Purpose**: Test the `llm-emit-token-metric` APIM policy for cost-effective token-level billing and chargeback in streaming mode — without relying on expensive Log Analytics ingestion.

**Context**: Partner scenario where APIM serves as an AI model gateway for multiple tenants. Streaming mode prevents traditional request/response logging. This policy emits token counts as Application Insights **custom metrics**, which are significantly cheaper than log ingestion and work with streaming.

**API**: Uses the **Responses API** (`/openai/v1/responses`) — the newer API surface that replaces Chat Completions — with **GPT-5.4 mini** (`reasoning_effort=low`).

---

## Architecture

```
┌──────────────┐      ┌──────────────────────────────--───┐     ┌──────────────────┐
│  Test Client │────▶ │  Azure API Management (APIM)      │────▶│  AI Foundry      │
│  (Python SDK)│      │  POST /openai/v1/responses        │     │  GPT-5.4 mini    │
└──────────────┘      │  ┌─────────────────────────────┐  │     └──────────────────┘
                      │  │ llm-emit-token-metric policy│  │
                      │  │ • Total Tokens              │  │
                      │  │ • Input Tokens              │  │
                      │  │ • Output Tokens             │  │
                      │  │ + Custom Dimensions:        │  │
                      │  │   - Client IP               │  │
                      │  │   - User ID                 │  │
                      │  │   - Cost Center             │  │
                      │  │   - Environment             │  │
                      │  └────────────┬────────────────┘  │
                      └───────────────┼───────────────────┘
                                      │
                                      ▼
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
| **Policy** | `llm-emit-token-metric` (inbound) — supports Responses API (preview) |
| **Streaming support** | Yes — tokens are **estimated** during streaming |
| **APIM tiers** | All tiers (Consumption, Developer, Basic, Standard, Premium, Basicv2, Standardv2) |
| **Metrics emitted** | Total Tokens, Input Tokens, Output Tokens |
| **Default dimensions** | API ID, Operation ID, Product ID, User ID, Subscription ID, Location, Gateway ID, Backend ID |
| **Custom dimensions** | Up to 5 per policy (we use: Client IP, User ID, Cost Center, Environment) |
| **Metrics destination** | App Insights `customMetrics` table |
| **Cost model** | Custom metrics ingestion ≈ **$0.00 for first 150M data points/month**, then ~$0.001/1K — orders of magnitude cheaper than Log Analytics log ingestion |
| **Latency** | Metrics appear in App Insights within 3-5 minutes |

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
- Application Insights (with `customMetricsOptedInType: WithDimensions`)
- APIM instance (Basicv2) with the `llm-emit-token-metric` policy and Responses API operations
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
| `main.bicep` | Infrastructure-as-code: APIM with Responses API operations, App Insights, AI Services (gpt-5.4-mini), RBAC, subscriptions |
| `main.parameters.json` | Deployment parameters (SKU, region, model, tenants) |
| `policy.xml` | APIM policy with `llm-emit-token-metric` and 4 custom billing dimensions |
| `deploy.sh` | One-click deploy script (creates RG, deploys Bicep, fetches keys) |
| `test_token_metrics.py` | Responses API test client: non-streaming, streaming, SDK, multi-tenant — uses `reasoning_effort=low` |
| `validate_metrics.py` | KQL queries to verify metrics in App Insights |
| `cleanup.sh` | Delete all test resources |
| `requirements.txt` | Python dependencies |

## What to Look For

1. **Metrics appear for streaming calls** — The whole point. Verify `customMetrics` table has entries from streaming Responses API requests.
2. **Token counts are reasonable** — Streaming uses estimation; compare with non-streaming actuals. Reasoning tokens (`output_tokens_details.reasoning_tokens`) add overhead vs non-reasoning models.
3. **Custom dimensions are populated** — Client IP, User ID, Cost Center, Environment should all appear.
4. **Per-subscription segregation** — Different APIM subscriptions (tenant-a/b/c) should appear as distinct `Subscription ID` dimension values.
5. **Responses API compatibility** — Confirm `llm-emit-token-metric` works correctly with the `/v1/responses` endpoint (currently preview support).
6. **Cost at scale** — Custom metrics pricing is ~150M free data points/month, then $0.001/1K. Compare this against Log Analytics ingestion at $2.76/GB.

## References

- [llm-emit-token-metric policy reference](https://learn.microsoft.com/azure/api-management/llm-emit-token-metric-policy)
- [Azure OpenAI Responses API](https://learn.microsoft.com/azure/foundry/openai/how-to/responses)
- [Monitor and log LLM token usage](https://learn.microsoft.com/azure/api-management/api-management-howto-llm-logs)
- [GenAI Gateway capabilities in APIM](https://learn.microsoft.com/azure/api-management/genai-gateway-capabilities)
- [Azure-Samples/ai-gateway (token-metrics-emitting lab)](https://github.com/Azure-Samples/ai-gateway/tree/main/labs/token-metrics-emitting)
