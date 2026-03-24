"""
Validate Token Metrics in Application Insights
Queries customMetrics table via Azure CLI to confirm llm-emit-token-metric
policy is emitting token counts correctly.

Usage:
  python validate_metrics.py --resource-group <RG> --app-insights-name <NAME>
  python validate_metrics.py --resource-group <RG> --app-insights-name <NAME> --export results.json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime


# KQL queries for validating token metrics
QUERIES = {
    "total_tokens_summary": """
customMetrics
| where name == 'Total Tokens'
| where timestamp > ago(30m)
| extend parsedDim = parse_json(customDimensions)
| extend subscriptionId = tostring(parsedDim['Subscription ID'])
| extend userId = tostring(parsedDim['User ID'])
| extend costCenter = tostring(parsedDim['Cost Center'])
| summarize TotalTokens=sum(value), CallCount=count() by subscriptionId, userId, costCenter
| order by TotalTokens desc
""".strip(),

    "prompt_vs_completion": """
customMetrics
| where name in ('Prompt Tokens', 'Completion Tokens')
| where timestamp > ago(30m)
| extend parsedDim = parse_json(customDimensions)
| extend subscriptionId = tostring(parsedDim['Subscription ID'])
| summarize Tokens=sum(value) by name, subscriptionId
| order by subscriptionId, name
""".strip(),

    "tokens_over_time": """
customMetrics
| where name == 'Total Tokens'
| where timestamp > ago(1h)
| extend parsedDim = parse_json(customDimensions)
| extend subscriptionId = tostring(parsedDim['Subscription ID'])
| summarize TotalTokens=sum(value) by bin(timestamp, 5m), subscriptionId
| order by timestamp desc
""".strip(),

    "all_dimensions_check": """
customMetrics
| where name == 'Total Tokens'
| where timestamp > ago(30m)
| extend parsedDim = parse_json(customDimensions)
| extend clientIP = tostring(parsedDim['Client IP'])
| extend apiId = tostring(parsedDim['API ID'])
| extend subscriptionId = tostring(parsedDim['Subscription ID'])
| extend userId = tostring(parsedDim['User ID'])
| extend costCenter = tostring(parsedDim['Cost Center'])
| extend environment = tostring(parsedDim['Environment'])
| project timestamp, value, clientIP, apiId, subscriptionId, userId, costCenter, environment
| order by timestamp desc
| take 20
""".strip(),

    "streaming_vs_nonstreaming": """
customMetrics
| where name == 'Total Tokens'
| where timestamp > ago(1h)
| extend parsedDim = parse_json(customDimensions)
| extend operationId = tostring(parsedDim['Operation ID'])
| summarize TotalTokens=sum(value), CallCount=count() by operationId
| order by TotalTokens desc
""".strip(),
}


def run_kql_query(resource_group: str, app_insights_name: str, query: str) -> dict:
    """Execute a KQL query against Application Insights via Azure CLI."""
    cmd = [
        "az", "monitor", "app-insights", "query",
        "--resource-group", resource_group,
        "--app", app_insights_name,
        "--analytics-query", query,
        "--output", "json",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return {"error": result.stderr.strip()}
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Validate Token Metrics in App Insights")
    parser.add_argument("--resource-group", required=True, help="Azure resource group name")
    parser.add_argument("--app-insights-name", required=True, help="Application Insights resource name")
    parser.add_argument("--query", choices=list(QUERIES.keys()), default=None,
                        help="Run a specific query (default: run all)")
    parser.add_argument("--export", type=str, default=None, help="Export results to JSON file")
    args = parser.parse_args()

    print(f"=== Token Metrics Validation ===")
    print(f"Resource Group: {args.resource_group}")
    print(f"App Insights:   {args.app_insights_name}")
    print(f"Time:           {datetime.utcnow().isoformat()}Z")
    print()

    queries_to_run = {args.query: QUERIES[args.query]} if args.query else QUERIES
    all_results = {}

    for name, query in queries_to_run.items():
        print(f"--- {name} ---")
        result = run_kql_query(args.resource_group, args.app_insights_name, query)

        if "error" in result:
            print(f"  ERROR: {result['error'][:200]}")
            all_results[name] = result
            continue

        tables = result.get("tables", [])
        if tables:
            columns = [c["name"] for c in tables[0].get("columns", [])]
            rows = tables[0].get("rows", [])
            print(f"  Columns: {columns}")
            print(f"  Rows:    {len(rows)}")
            for row in rows[:10]:
                row_dict = dict(zip(columns, row))
                print(f"    {row_dict}")
            if len(rows) == 0:
                print("  (no data yet — metrics may take 3-5 minutes to appear)")
        else:
            print("  (no tables returned)")

        all_results[name] = result
        print()

    if args.export:
        with open(args.export, "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"Results exported to {args.export}")

    # Quick health check
    print("\n=== Health Check ===")
    summary = all_results.get("total_tokens_summary", {})
    tables = summary.get("tables", [])
    if tables and tables[0].get("rows"):
        print("PASS: Token metrics are being emitted to Application Insights!")
        print(f"  Found {len(tables[0]['rows'])} distinct subscription/user/costCenter combinations.")
    else:
        print("WARN: No token metrics found yet.")
        print("  - Metrics can take 3-5 minutes to appear after API calls.")
        print("  - Verify the llm-emit-token-metric policy is applied.")
        print("  - Check that App Insights has CustomMetricsOptedInType = 'WithDimensions'.")


if __name__ == "__main__":
    main()
