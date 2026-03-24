#!/bin/bash
# ============================================================================
# Cleanup: Delete all test bed resources
# ============================================================================
set -euo pipefail

RESOURCE_GROUP="${RESOURCE_GROUP:-rg-apim-token-metrics-testbed}"

echo "=== Cleanup: APIM Token Metrics Test Bed ==="
echo "This will DELETE resource group: $RESOURCE_GROUP"
echo ""
read -p "Are you sure? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Cancelled."
    exit 0
fi

echo "Deleting resource group $RESOURCE_GROUP..."
az group delete --name "$RESOURCE_GROUP" --yes --no-wait
echo "Deletion initiated (runs in background). Resources will be removed within ~5 minutes."
