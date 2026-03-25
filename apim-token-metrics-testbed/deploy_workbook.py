"""Deploy the LLM Token Billing Dashboard workbook to Azure.

Usage:
    python deploy_workbook.py
    python deploy_workbook.py --resource-group <RG> --app-insights-name <NAME>
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import uuid


def main():
    parser = argparse.ArgumentParser(description="Deploy workbook to App Insights")
    parser.add_argument("--resource-group", default="rg-apim-token-metrics-testbed")
    parser.add_argument("--app-insights-name", default="appi-nmjucoy7g7q22")
    parser.add_argument("--subscription-id", default="7a28b21e-0d3e-4435-a686-d92889d4ee96")
    parser.add_argument("--location", default="eastus2")
    args = parser.parse_args()

    app_insights_id = (
        f"/subscriptions/{args.subscription_id}"
        f"/resourceGroups/{args.resource_group}"
        f"/providers/microsoft.insights/components/{args.app_insights_name}"
    )
    workbook_id = str(uuid.uuid4())

    # Load workbook template
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "workbook-template.json")
    with open(template_path) as f:
        template = json.load(f)
    template["fallbackResourceIds"] = [app_insights_id]

    body = {
        "location": args.location,
        "kind": "shared",
        "properties": {
            "displayName": "LLM Token Billing Dashboard",
            "serializedData": json.dumps(template),
            "category": "workbook",
            "sourceId": app_insights_id,
            "version": "Notebook/1.0",
        },
    }

    url = (
        f"https://management.azure.com/subscriptions/{args.subscription_id}"
        f"/resourceGroups/{args.resource_group}/providers/Microsoft.Insights"
        f"/workbooks/{workbook_id}?api-version=2023-06-01"
    )

    # Write body to temp file (avoids arg length limits)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(body, f)
        body_file = f.name

    try:
        result = subprocess.run(
            ["az", "rest", "--method", "PUT", "--url", url,
             "--body", f"@{body_file}", "--output", "json"],
            capture_output=True, text=True, timeout=30,
        )
    finally:
        os.unlink(body_file)

    if result.returncode != 0:
        print(f"ERROR: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    response = json.loads(result.stdout)
    wb_name = response["properties"]["displayName"]
    wb_id = response["id"]

    print(f"Workbook deployed: {wb_name}")
    print(f"Resource ID: {wb_id}")
    print(f"\nOpen in Azure Portal:")
    print(f"https://portal.azure.com/#@/resource{wb_id}/workbook")


if __name__ == "__main__":
    main()
