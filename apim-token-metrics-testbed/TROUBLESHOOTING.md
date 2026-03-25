---
title: "APIM Token Metrics Troubleshooting Guide"
description: "Complete debugging journey and root cause analysis for APIM emit-metric with Bicep-provisioned APIs, covering three silent failure modes."
author: "Arturo Quiroga"
ms.date: 2026-03-24
ms.topic: troubleshooting
---

## Overview

This document captures the full debugging journey for getting APIM token
metrics to flow into Application Insights `customMetrics`. We spent
significant time on this because **three independent root causes** combined
to produce the same symptom: zero custom metrics despite successful API calls.

If you are setting up APIM AI Gateway token billing with infrastructure as
code (Bicep, Terraform, ARM), read the quick checklist first. If you need to
understand *why*, continue to the detailed analysis.

## Quick checklist

Before debugging further, verify every item below. All three must be true for
`emit-metric` (or `azure-openai-emit-token-metric`) to work:

- [ ] **API imported via portal** — If using `azure-openai-emit-token-metric`
  or `llm-emit-token-metric`, the API *must* be imported through the Azure
  OpenAI import flow in the portal. Bicep/ARM-created APIs have
  `apiType: http` and these policies silently skip them. Use generic
  `emit-metric` as a workaround.
- [ ] **`metrics: true` on diagnostic** — The `applicationinsights` diagnostic
  entity *must* have `"metrics": true`. Without it, `emit-metric` succeeds
  silently but data never reaches App Insights.
- [ ] **Streaming guard** — If your API supports streaming, wrap all
  `context.Response.Body?.As<string>()` calls in a Content-Type check.
  SSE responses (`text/event-stream`) throw an exception when read, causing
  500 errors.

## Symptom

After deploying the full APIM testbed via Bicep and running dozens of
successful test requests (HTTP 200), the `customMetrics` table in Application
Insights remained empty. The standard telemetry pipeline was confirmed
working — `requests` and `dependencies` tables had data.

```kusto
-- This returned data
requests | summarize count()           -- 49 rows ✅

-- This returned nothing
customMetrics | summarize count()      -- 0 rows ❌
```

## Debugging timeline

### Phase 1 — Initial deployment with `llm-emit-token-metric`

We deployed using Bicep with the `llm-emit-token-metric` policy in the
inbound section:

```xml
<llm-emit-token-metric namespace="LLM Token Metrics">
  <dimension name="Tenant ID" value="@(...)" />
  <!-- more dimensions -->
</llm-emit-token-metric>
```

Tests passed (HTTP 200), but `customMetrics` stayed at zero.

**What we checked**:

| Component | Status | Finding |
|---|---|---|
| APIM Logger | ✅ | `appinsights-logger` correctly configured with iKey |
| APIM Diagnostic | ✅ | `applicationinsights` diagnostic with 100% sampling |
| App Insights config | ✅ | `CustomMetricsOptedInType=WithDimensions` |
| App Insights ingestion | ✅ | `requests: 49`, `dependencies: 49`, `exceptions: 2` |
| Custom metrics | ❌ | 0 rows |

The diagnostic pipeline was working. Something specific to the token metric
policy was failing silently.

### Phase 2 — Switch to `azure-openai-emit-token-metric`

We discovered that `llm-emit-token-metric` supports "Azure AI Model Inference
API or OpenAI-compatible models served through third-party inference providers"
but does not explicitly list the Responses API.

The `azure-openai-emit-token-metric` docs explicitly list "Responses (preview)"
as supported. We switched policies and redeployed.

Result: still 0 `customMetrics`.

### Phase 3 — Root cause 1 discovered: API type mismatch

We checked the API properties via REST API:

```bash
az rest --method GET \
  --url ".../apis/azure-openai-api?api-version=2024-05-01" \
  --query "properties.{apiType:apiType,type:type}"
```

**Result**:

```json
{
  "apiType": null,
  "type": "http"
}
```

Both `azure-openai-emit-token-metric` and `llm-emit-token-metric` require
the API to be imported through the Azure OpenAI import flow in the portal.
This sets an internal `apiType` property that these policies check. When
`apiType` is null or `http` (the Bicep default), the policies **silently
skip metric emission** — no error, no warning, no log entry.

> **Key insight**: The documentation says these policies "support" various
> API surfaces, but the prerequisite is that the API itself must be of the
> correct type. Creating an API via Bicep with matching URL patterns is not
> enough.

### Phase 4 — Switch to generic `emit-metric`

Since we cannot set `apiType` via Bicep and recreating the API through the
portal defeats the purpose of IaC, we switched to the generic `emit-metric`
policy. This required:

1. Moving metric emission from inbound to **outbound** (we need the response
   body to parse token counts)
2. Manually parsing the `usage` JSON from the response body
3. Supporting both the Responses API field names (`input_tokens`,
   `output_tokens`) and Chat Completions API field names (`prompt_tokens`,
   `completion_tokens`)

```xml
<set-variable name="response-body"
  value="@(context.Response.Body?.As<string>(preserveContent: true))" />
<set-variable name="usage-json" value="@{
    var body = (string)context.Variables[&quot;response-body&quot;];
    var json = JObject.Parse(body);
    var usage = json[&quot;usage&quot;];
    if (usage == null) { return &quot;{}&quot;; }
    return usage.ToString();
}" />
<!-- Parse individual token counts, then emit-metric -->
```

First deployment attempt failed: the APIM policy expression parser does not
support `try`/`catch` blocks or `//` comments in multi-line expressions. We
simplified the expressions (null checks via `if` statements, no comments
inside expression blocks).

Second deployment succeeded. Non-streaming tests passed (2/2). But streaming
tests returned **500 Internal Server Error**.

### Phase 5 — Root cause 3 discovered: streaming body read crash

The error occurred because
`context.Response.Body?.As<string>(preserveContent: true)` throws an
exception when the response has `Content-Type: text/event-stream` (SSE).
The streaming response body is a one-time-read event stream that cannot be
buffered by the APIM policy engine.

**Fix**: Check the Content-Type before reading the body:

```xml
<set-variable name="is-streaming"
  value="@(context.Response.Headers.GetValueOrDefault(
    &quot;Content-Type&quot;,&quot;&quot;).Contains(
    &quot;text/event-stream&quot;))" />
<choose>
  <when condition="@(!context.Variables.GetValueOrDefault&lt;bool&gt;(
    &quot;is-streaming&quot;))">
    <!-- Safe to read response body here -->
  </when>
</choose>
```

This guard was needed in **two places**: the Approach 1 token metric section
and the Approach 2 Event Hub audit section. Both were reading the response
body unconditionally.

After this fix: 4/4 tests passed (non-streaming HTTP, streaming HTTP,
non-streaming SDK, streaming SDK).

### Phase 6 — Root cause 2 discovered: missing `metrics: true`

Despite 4/4 tests passing, `customMetrics` remained at zero after waiting
5+ minutes. We re-read the
[Emit custom metrics](https://learn.microsoft.com/azure/api-management/api-management-howto-app-insights#emit-custom-metrics)
documentation more carefully and found step 2:

> Add the `"metrics": true` property to the `applicationInsights` diagnostic
> entity that's configured in API Management.

We checked the diagnostic via REST API:

```bash
az rest --method GET \
  --url ".../diagnostics/applicationinsights?api-version=2024-05-01" \
  --query "properties.metrics"
```

**Result**: `null` — the property was not set.

We added it:

```bash
az rest --method PUT \
  --url ".../diagnostics/applicationinsights?api-version=2024-05-01" \
  --body '{"properties":{"loggerId":"...","metrics":true,...}}'
```

And in Bicep:

```bicep
resource apimDiagnostic '...' = {
  properties: {
    loggerId: apimLogger.id
    metrics: true  // <-- THIS WAS MISSING
  }
}
```

After this fix: ran 6 test calls, waited 3 minutes, and ran validation:

```text
=== Health Check ===
PASS: Token metrics are being emitted to Application Insights!
  Found 1 distinct subscription/user/costCenter combinations.
```

**customMetrics finally had data**:

| Metric | Value |
|---|---|
| Total Tokens | 1,020 (2 calls) |
| Prompt Tokens | 136 |
| Completion Tokens | 884 |

## Root cause summary

| # | Root cause | Symptom | Detection method | Fix |
|---|---|---|---|---|
| 1 | API type is `http` (Bicep default) instead of portal-imported | `azure-openai-emit-token-metric` and `llm-emit-token-metric` silently skip all metrics | Check `apiType` via REST API; compare App Insights `requests` (has data) vs `customMetrics` (empty) | Use generic `emit-metric` with manual usage JSON parsing |
| 2 | `applicationinsights` diagnostic missing `metrics: true` | `emit-metric` calls succeed but data never reaches App Insights | Check diagnostic properties via REST API; verify `properties.metrics` is `true` | Add `metrics: true` to diagnostic in Bicep and via REST API |
| 3 | Response body read crashes on SSE streaming | 500 Internal Server Error on streaming requests | Test with `--streaming` flag; check APIM exceptions in App Insights | Add `is-streaming` Content-Type check before any `context.Response.Body` call |

## Diagnostic commands

### Check API type

```bash
az rest --method GET \
  --url "https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ApiManagement/service/{apim}/apis/{api}?api-version=2024-05-01" \
  --query "properties.{apiType:apiType,type:type}" -o json
```

If `apiType` is null, `azure-openai-emit-token-metric` and
`llm-emit-token-metric` will not work. Use `emit-metric` instead.

### Check diagnostic metrics property

```bash
az rest --method GET \
  --url "https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ApiManagement/service/{apim}/diagnostics/applicationinsights?api-version=2024-05-01" \
  --query "properties.metrics" -o json
```

Must return `true`. If null or missing, set it:

```bash
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ApiManagement/service/{apim}/diagnostics/applicationinsights?api-version=2024-05-01" \
  --body '{"properties":{"loggerId":"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.ApiManagement/service/{apim}/loggers/{logger}","metrics":true,"alwaysLog":"allErrors","sampling":{"samplingType":"fixed","percentage":100}}}'
```

### Broad App Insights table check

```kusto
union withsource=tableName requests, dependencies, customMetrics,
  customEvents, traces, exceptions
| summarize count() by tableName
| order by count_ desc
```

If `requests` and `dependencies` have data but `customMetrics` is absent,
the diagnostic pipeline works but the metric emission specifically is failing.

### Check for streaming exceptions

```kusto
exceptions
| where timestamp > ago(1h)
| project timestamp, type, outerMessage, innermostMessage
| order by timestamp desc
```

Look for `ClientConnectionFailure` or body-read-related exceptions on
streaming requests.

## APIM policy expression gotchas

These are additional lessons learned from writing C# expressions inside APIM
policy XML:

| Pitfall | Example | Fix |
|---|---|---|
| `try`/`catch` not supported | `try { ... } catch { ... }` | Use `if (val == null)` null checks instead |
| `//` comments not allowed in multi-line expressions | `// This is a comment` | Remove comments from expression blocks; use XML comments outside |
| `context.Response.Body` throws for SSE | `context.Response.Body?.As<string>(preserveContent: true)` | Check `Content-Type` for `text/event-stream` first |
| Must use `preserveContent: true` | `context.Response.Body?.As<string>()` | Always pass `preserveContent: true` to avoid consuming the body |
| Variable type matters for `GetValueOrDefault` | `context.Variables["var"]` | Use typed accessor: `context.Variables.GetValueOrDefault<bool>("var")` |
| XML entity encoding in attributes | `value="@(a < b)"` | Use `&lt;` and `&gt;` inside XML attribute expressions |

## Policy structure reference

The final working policy structure (simplified):

```text
<policies>
  <inbound>
    <base />
    <set-backend-service />
    <authentication-managed-identity />

    <!-- Approach 1: capture dimension values -->
    <set-variable name="dim-client-ip" />
    <set-variable name="dim-tenant-id" />
    <set-variable name="dim-subscription-name" />

    <!-- Approach 2: inbound audit → Event Hub -->
    <set-variable name="inbound-audit-payload" />
    <send-request>  (MI auth to Event Hub REST API)

  </inbound>
  <backend><base /></backend>
  <outbound>
    <base />

    <!-- Streaming guard (shared by both approaches) -->
    <set-variable name="is-streaming" />

    <!-- Approach 1: emit token metrics (non-streaming only) -->
    <choose>
      <when condition="!is-streaming">
        <set-variable name="response-body" />
        <choose>
          <when condition="response-body != null">
            parse usage JSON → total-tokens, prompt-tokens, completion-tokens
            <choose>
              <when condition="total-tokens > 0">
                <emit-metric name="Total Tokens" />
                <emit-metric name="Prompt Tokens" />
                <emit-metric name="Completion Tokens" />
              </when>
            </choose>
          </when>
        </choose>
      </when>
    </choose>

    <!-- Approach 2: outbound audit → Event Hub (non-streaming only) -->
    <choose>
      <when condition="!is-streaming">
        <set-variable name="outbound-audit-payload" />
        <send-request>  (MI auth to Event Hub REST API)
      </when>
    </choose>

  </outbound>
  <on-error><base /></on-error>
</policies>
```

## Verified working configuration

As of 2026-03-24, the following exact configuration produces token metrics
in App Insights `customMetrics`:

| Component | Value |
|---|---|
| APIM SKU | Basicv2 |
| API type | `http` (Bicep-created, not portal-imported) |
| Model | `gpt-5.4-mini` version `2026-03-17` |
| API surface | Responses API (`/openai/v1/responses`) |
| Token metric policy | `emit-metric` (generic, outbound section) |
| Audit policy | `send-request` + `authentication-managed-identity` |
| Logger type | `applicationInsights` with instrumentation key |
| Diagnostic `metrics` | `true` |
| App Insights | `CustomMetricsOptedInType=WithDimensions`, `IngestionMode=LogAnalytics` |
| Streaming | Gracefully skipped (no metrics emitted, no 500 error) |
| Test results | 4/4 pass (non-streaming HTTP, streaming HTTP, non-streaming SDK, streaming SDK) |
| Metric names | "Total Tokens", "Prompt Tokens", "Completion Tokens" |
| Metric namespace | "LLM Token Metrics" |
| Dimensions | Client IP, Tenant ID, Subscription Name, API ID, Subscription ID |
