#!/bin/bash

# Azure Infrastructure Deployment Script
# This script deploys the Bicep template to create Azure OpenAI, AI Search, Storage, and App Service resources

set -e

# Configuration
RESOURCE_GROUP_NAME="rg-hypervelocity-engineering-dev"
LOCATION="eastus2"
DEPLOYMENT_NAME="hve-infrastructure-$(date +%Y%m%d-%H%M%S)"
BICEP_FILE="main.bicep"
PARAMETERS_FILE="main.parameters.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Azure Infrastructure Deployment${NC}"
echo "=================================="
echo "Resource Group: $RESOURCE_GROUP_NAME"
echo "Location: $LOCATION"
echo "Deployment Name: $DEPLOYMENT_NAME"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  You are not logged in to Azure. Please login first.${NC}"
    echo "Run: az login"
    exit 1
fi

# Display current subscription
SUBSCRIPTION=$(az account show --query name -o tsv)
echo -e "${BLUE}📋 Current subscription: ${SUBSCRIPTION}${NC}"
echo ""

# Create resource group if it doesn't exist
echo -e "${YELLOW}🏗️  Creating resource group...${NC}"
az group create \
    --name $RESOURCE_GROUP_NAME \
    --location $LOCATION \
    --output table

echo ""

# Validate the Bicep template
echo -e "${YELLOW}✅ Validating Bicep template...${NC}"
az deployment group validate \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file $BICEP_FILE \
    --parameters @$PARAMETERS_FILE

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Template validation successful${NC}"
else
    echo -e "${RED}❌ Template validation failed${NC}"
    exit 1
fi

echo ""

# Deploy the infrastructure
echo -e "${YELLOW}🚀 Deploying infrastructure...${NC}"
echo "This may take several minutes..."
echo ""

az deployment group create \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $DEPLOYMENT_NAME \
    --template-file $BICEP_FILE \
    --parameters @$PARAMETERS_FILE \
    --output table

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    
    # Get deployment outputs
    echo -e "${BLUE}📋 Deployment Outputs:${NC}"
    az deployment group show \
        --resource-group $RESOURCE_GROUP_NAME \
        --name $DEPLOYMENT_NAME \
        --query properties.outputs \
        --output table
    
    echo ""
    echo -e "${GREEN}🎉 Your Azure infrastructure is ready!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Get the API keys from Azure Portal for OpenAI and Search services"
    echo "2. Configure your application with the service endpoints"
    echo "3. Deploy your application to the Web App"
    
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi