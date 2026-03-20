#!/bin/bash

# PROFISEE Multi-Agent MDM System - Deployment Script
# Partner: PROFISEE
# Use Case: Multi-Agent Master Data Management System
# Technologies: Microsoft Agent Framework (MAF), Azure AI Services
# Author: Arturo Quiroga, Partner Solutions Architect
# Date: March 2026

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP_NAME="rg-profisee-mdm-dev"
LOCATION="East US 2"
DEPLOYMENT_NAME="profisee-mdm-deployment-$(date +%Y%m%d-%H%M%S)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}PROFISEE Multi-Agent MDM System Deployment${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo -e "${RED}Error: Azure CLI is not installed. Please install it first.${NC}"
    echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged into Azure
if ! az account show &> /dev/null; then
    echo -e "${RED}Error: Not logged into Azure. Please run 'az login' first.${NC}"
    exit 1
fi

# Get current subscription info
SUBSCRIPTION_ID=$(az account show --query id --output tsv)
SUBSCRIPTION_NAME=$(az account show --query name --output tsv)
echo -e "${GREEN}✓ Logged into Azure${NC}"
echo -e "  Subscription: ${SUBSCRIPTION_NAME} (${SUBSCRIPTION_ID})"

# Check if Docker is installed (for containerization)
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Docker is available${NC}"
else
    echo -e "${YELLOW}⚠ Docker not found - containerization features will be limited${NC}"
fi

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python is available (${PYTHON_VERSION})${NC}"
else
    echo -e "${YELLOW}⚠ Python not found - local development features will be limited${NC}"
fi

echo ""

# Prompt for confirmation
echo -e "${YELLOW}Deployment Configuration:${NC}"
echo "  Resource Group: ${RESOURCE_GROUP_NAME}"
echo "  Location: ${LOCATION}"
echo "  Deployment Name: ${DEPLOYMENT_NAME}"
echo ""

read -p "Do you want to continue with the deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Deployment cancelled.${NC}"
    exit 0
fi

echo ""

# Create resource group
echo -e "${YELLOW}Creating resource group...${NC}"
if az group show --name $RESOURCE_GROUP_NAME &> /dev/null; then
    echo -e "${GREEN}✓ Resource group ${RESOURCE_GROUP_NAME} already exists${NC}"
else
    az group create --name $RESOURCE_GROUP_NAME --location "$LOCATION"
    echo -e "${GREEN}✓ Created resource group ${RESOURCE_GROUP_NAME}${NC}"
fi

echo ""

# Deploy Bicep template
echo -e "${YELLOW}Deploying Azure infrastructure...${NC}"
echo "This may take 10-15 minutes..."

# Get SQL password from user (secure input)
echo -n "Enter SQL Administrator Password: "
read -s SQL_PASSWORD
echo

az deployment group create \
    --resource-group $RESOURCE_GROUP_NAME \
    --template-file profisee-azure-infrastructure.bicep \
    --parameters profisee-deployment-parameters.json \
    --parameters sqlAdministratorPassword="$SQL_PASSWORD" \
    --name $DEPLOYMENT_NAME \
    --verbose

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Azure infrastructure deployed successfully${NC}"
else
    echo -e "${RED}✗ Infrastructure deployment failed${NC}"
    exit 1
fi

echo ""

# Get deployment outputs
echo -e "${YELLOW}Retrieving deployment outputs...${NC}"

OUTPUTS=$(az deployment group show \
    --resource-group $RESOURCE_GROUP_NAME \
    --name $DEPLOYMENT_NAME \
    --query properties.outputs \
    --output json)

# Parse key outputs
OPENAI_ENDPOINT=$(echo $OUTPUTS | jq -r '.openAiEndpoint.value')
SEARCH_SERVICE_NAME=$(echo $OUTPUTS | jq -r '.searchServiceName.value')
COSMOS_DB_ENDPOINT=$(echo $OUTPUTS | jq -r '.cosmosDbEndpoint.value')
KEY_VAULT_URI=$(echo $OUTPUTS | jq -r '.keyVaultUri.value')
CONTAINER_REGISTRY_LOGIN_SERVER=$(echo $OUTPUTS | jq -r '.containerRegistryLoginServer.value')

echo -e "${GREEN}✓ Deployment outputs retrieved${NC}"
echo "  OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "  Search Service: $SEARCH_SERVICE_NAME"
echo "  Key Vault: $KEY_VAULT_URI"
echo "  Container Registry: $CONTAINER_REGISTRY_LOGIN_SERVER"

echo ""

# Create .env file for local development
echo -e "${YELLOW}Creating environment configuration...${NC}"

ENV_CONFIG=$(echo $OUTPUTS | jq -r '.environmentConfiguration.value')

cat > .env << EOF
# PROFISEE Multi-Agent MDM System - Environment Configuration
# Generated on: $(date)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT_NAME=$(echo $OUTPUTS | jq -r '.gpt4oDeploymentName.value')
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=$(echo $OUTPUTS | jq -r '.embeddingDeploymentName.value')

# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_NAME=$SEARCH_SERVICE_NAME
AZURE_SEARCH_ENDPOINT=$(echo $OUTPUTS | jq -r '.searchServiceEndpoint.value')

# Azure Text Analytics Configuration  
TEXT_ANALYTICS_ENDPOINT=$(echo $OUTPUTS | jq -r '.textAnalyticsEndpoint.value')

# Azure Document Intelligence Configuration
DOCUMENT_INTELLIGENCE_ENDPOINT=$(echo $OUTPUTS | jq -r '.documentIntelligenceEndpoint.value')

# Azure Cosmos DB Configuration
COSMOS_DB_ENDPOINT=$COSMOS_DB_ENDPOINT
COSMOS_DB_DATABASE_NAME=$(echo $OUTPUTS | jq -r '.cosmosDbDatabaseName.value')

# Azure SQL Database Configuration
SQL_SERVER_FQDN=$(echo $OUTPUTS | jq -r '.sqlServerFqdn.value')
SQL_DATABASE_NAME=$(echo $OUTPUTS | jq -r '.sqlDatabaseName.value')

# Azure Storage Configuration
STORAGE_ACCOUNT_NAME=$(echo $OUTPUTS | jq -r '.storageAccountName.value')
BLOB_STORAGE_ENDPOINT=$(echo $OUTPUTS | jq -r '.blobStorageEndpoint.value')

# Azure Key Vault Configuration
AZURE_KEY_VAULT_URL=$KEY_VAULT_URI

# Monitoring Configuration
APPLICATION_INSIGHTS_CONNECTION_STRING="$(echo $OUTPUTS | jq -r '.applicationInsightsConnectionString.value')"
LOG_ANALYTICS_WORKSPACE_ID=$(echo $OUTPUTS | jq -r '.logAnalyticsWorkspaceId.value')

# Container Registry Configuration
CONTAINER_REGISTRY_LOGIN_SERVER=$CONTAINER_REGISTRY_LOGIN_SERVER

EOF

echo -e "${GREEN}✓ Environment file created (.env)${NC}"

echo ""

# Set up Python virtual environment (if Python is available)
if command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Setting up Python development environment...${NC}"
    
    # Create virtual environment
    python3 -m venv profisee-mdm-env
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    
    # Activate and install dependencies
    source profisee-mdm-env/bin/activate
    
    if [ -f "profisee-requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r profisee-requirements.txt
        echo -e "${GREEN}✓ Python dependencies installed${NC}"
    else
        echo -e "${YELLOW}⚠ Requirements file not found, skipping pip install${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}To activate the Python environment, run:${NC}"
    echo -e "${BLUE}source profisee-mdm-env/bin/activate${NC}"
fi

echo ""

# Initialize Azure AI Search index (if search service is ready)
echo -e "${YELLOW}Initializing Azure AI Search index...${NC}"

# This would typically involve creating the search index schema
# For now, we'll just note that it needs to be done
echo -e "${YELLOW}⚠ Search index initialization requires manual setup${NC}"
echo "  1. Create master-data-entities index in $SEARCH_SERVICE_NAME"
echo "  2. Configure semantic search and vector fields"
echo "  3. Set up indexers for data ingestion"

echo ""

# Container registry setup (if Docker is available)
if command -v docker &> /dev/null; then
    echo -e "${YELLOW}Setting up container registry authentication...${NC}"
    
    # Login to Azure Container Registry
    az acr login --name $(echo $OUTPUTS | jq -r '.containerRegistryName.value')
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Authenticated with Azure Container Registry${NC}"
    else
        echo -e "${YELLOW}⚠ Container registry authentication failed${NC}"
    fi
fi

echo ""

# Generate post-deployment checklist
echo -e "${YELLOW}Post-deployment checklist:${NC}"
echo ""
echo -e "${BLUE}1. Verify Azure Resources:${NC}"
echo "   - Check all Azure resources are deployed and running"
echo "   - Verify Azure OpenAI deployments are ready"
echo "   - Test connectivity to all services"
echo ""
echo -e "${BLUE}2. Configure Authentication:${NC}"
echo "   - Set up Managed Identity or Service Principal"
echo "   - Configure Key Vault access policies"
echo "   - Test secret retrieval from Key Vault"
echo ""
echo -e "${BLUE}3. Initialize Data Stores:${NC}"
echo "   - Create Azure AI Search index schema"
echo "   - Set up Cosmos DB containers and partitioning"
echo "   - Initialize SQL Database schema"
echo ""
echo -e "${BLUE}4. Deploy Application Code:${NC}"
echo "   - Build and push MAF agent container images"
echo "   - Deploy to Container Apps or AKS"
echo "   - Configure auto-scaling and health checks"
echo ""
echo -e "${BLUE}5. Test the System:${NC}"
echo "   - Run end-to-end tests with sample data"
echo "   - Verify multi-agent workflows"
echo "   - Test monitoring and alerting"
echo ""

# Save deployment summary
cat > deployment-summary.md << EOF
# PROFISEE MDM System Deployment Summary

**Deployment Date:** $(date)  
**Deployment Name:** $DEPLOYMENT_NAME  
**Resource Group:** $RESOURCE_GROUP_NAME  
**Location:** $LOCATION  

## Deployed Resources

- **Azure OpenAI:** $OPENAI_ENDPOINT
- **Azure AI Search:** $SEARCH_SERVICE_NAME  
- **Azure Cosmos DB:** $COSMOS_DB_ENDPOINT
- **Azure Key Vault:** $KEY_VAULT_URI
- **Container Registry:** $CONTAINER_REGISTRY_LOGIN_SERVER

## Next Steps

1. Configure authentication and access policies
2. Initialize data stores and search indexes
3. Deploy and test MAF agent applications
4. Set up monitoring and alerting
5. Configure CI/CD pipelines

## Environment File

Local development environment configuration has been saved to \`.env\`

## Support Resources

- [Microsoft Agent Framework Documentation](https://microsoft.github.io/autogen/)
- [Azure AI Services Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/)
- [PROFISEE Technical Architecture](./profisee-mdm-multi-agent-architecture.md)

EOF

echo -e "${GREEN}✓ Deployment summary saved to deployment-summary.md${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETED SUCCESSFULLY! 🎉${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}The PROFISEE Multi-Agent MDM system infrastructure has been deployed.${NC}"
echo -e "${BLUE}Check deployment-summary.md for next steps and configuration details.${NC}"
echo ""