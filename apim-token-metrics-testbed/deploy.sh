#!/bin/bash
# ============================================================================
# Deploy APIM Token Metrics Test Bed
# ============================================================================
set -euo pipefail

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-rg-apim-token-metrics-testbed}"
LOCATION="${LOCATION:-eastus2}"
DEPLOYMENT_NAME="apim-token-metrics-$(date +%Y%m%d%H%M%S)"

echo "=== APIM Token Metrics Test Bed - Deployment ==="
echo "Resource Group: $RESOURCE_GROUP"
echo "Location:       $LOCATION"
echo ""

# Verify Azure CLI login
echo "Verifying Azure CLI session..."
az account show --query "[name, id]" -o tsv || { echo "ERROR: Not logged in. Run 'az login' first."; exit 1; }
echo ""

# Create resource group
echo "Creating resource group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" -o none
echo "Resource group created."

# Deploy Bicep
echo ""
echo "Deploying Bicep template (this takes ~10-15 minutes for APIM provisioning)..."
az deployment group create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DEPLOYMENT_NAME" \
  --template-file main.bicep \
  --parameters main.parameters.json \
  --query "properties.outputs" \
  -o json | tee deployment-outputs.json

echo ""
echo "=== Deployment Complete ==="
echo "Outputs saved to deployment-outputs.json"

# Extract key values for test scripts
APIM_GATEWAY_URL=$(jq -r '.apimGatewayUrl.value' deployment-outputs.json)
APIM_NAME=$(jq -r '.apimName.value' deployment-outputs.json)
APP_INSIGHTS_NAME=$(jq -r '.appInsightsName.value' deployment-outputs.json)

echo ""
echo "APIM Gateway URL: $APIM_GATEWAY_URL"
echo "APIM Name:        $APIM_NAME"
echo "App Insights:     $APP_INSIGHTS_NAME"

# Fetch subscription keys
echo ""
echo "Fetching APIM subscription keys..."
for sub in tenant-a tenant-b tenant-c; do
  KEY=$(az rest --method post \
    --uri "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.ApiManagement/service/$APIM_NAME/subscriptions/$sub/listSecrets?api-version=2024-05-01" \
    --query "primaryKey" -o tsv 2>/dev/null || echo "PENDING")
  echo "  $sub: $KEY"
done

echo ""
echo "Next steps:"
echo "  1. Wait ~5 minutes for RBAC propagation"
echo "  2. Copy a subscription key above"
echo "  3. Run: python test_token_metrics.py --gateway-url $APIM_GATEWAY_URL --api-key <KEY>"
