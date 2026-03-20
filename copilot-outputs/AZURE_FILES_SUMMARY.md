# Azure Infrastructure Files Summary

This directory contains all the files needed to deploy Azure infrastructure using Bicep for the Hypervelocity Engineering project.

## Generated Files for Azure Infrastructure

### Core Infrastructure Files
- **`main.bicep`** (7,479 bytes) - Main Bicep template that provisions:
  - Azure OpenAI Account with GPT-4o deployment (30K TPM capacity)
  - Azure AI Search Service (Basic tier)  
  - Azure Blob Storage Account (Standard LRS)
  - App Service Plan (Linux, configurable SKU)
  - Linux Web App (Python 3.11 runtime)
  
- **`main.parameters.json`** (478 bytes) - Parameters file with default values:
  - Location: East US 2
  - Resource prefix: "hve"
  - Environment: "dev"
  - OpenAI deployment: "gpt-4o" with 30K TPM capacity
  - App Service SKU: B1 (Basic)

### Deployment Scripts
- **`deploy.sh`** (2,969 bytes) - Bash deployment script for Linux/Mac with:
  - Azure CLI validation
  - Resource group creation
  - Template validation
  - Automated deployment
  - Output display
  
- **`deploy.ps1`** (3,805 bytes) - PowerShell deployment script for Windows with:
  - Same functionality as bash script
  - Windows-friendly syntax and error handling

### Documentation
- **`AZURE_DEPLOYMENT.md`** (5,566 bytes) - Comprehensive documentation including:
  - Prerequisites and setup instructions
  - Configuration options
  - Post-deployment steps
  - Cost estimates (~$283-303/month)
  - Security considerations
  - Troubleshooting guide

## Quick Start

1. **Linux/Mac**: `./deploy.sh`
2. **Windows**: `.\deploy.ps1`
3. **Manual**: `az deployment group create --resource-group rg-hypervelocity-engineering-dev --template-file main.bicep --parameters @main.parameters.json`

## Resource Naming Convention

All resources follow the pattern: `{prefix}-{service}-{environment}-{uniqueId}`

Example resource names:
- OpenAI: `hve-openai-dev-abc123`
- Search: `hve-search-dev-abc123`
- Storage: `hvestoragedevabc123`
- App Plan: `hve-asp-dev-abc123`
- Web App: `hve-webapp-dev-abc123`

## Template Validation

✅ **Bicep syntax validation passed** - Template is ready for deployment

## Next Steps

1. Run `az login` to authenticate with Azure
2. Execute the deployment script: `./deploy.sh`
3. Retrieve API keys for the services
4. Deploy your application to the web app

All resources will be deployed to **East US 2** region with consistent tagging and naming conventions.