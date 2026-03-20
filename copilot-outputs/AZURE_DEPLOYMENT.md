# Azure Infrastructure with Bicep

This directory contains Bicep templates and deployment scripts to provision Azure resources for the Hypervelocity Engineering project.

## Resources Provisioned

The Bicep template creates the following Azure resources in the **East US 2** region:

1. **Azure OpenAI Account** with GPT-4o deployment
2. **Azure AI Search Service** (Basic tier)
3. **Azure Blob Storage Account** (Standard LRS)
4. **App Service Plan** (Linux)
5. **Linux Web App** (Python 3.11 runtime)

All resources are grouped in a single resource group with consistent naming conventions and tags.

## Files

- `main.bicep` - Main Bicep template with all resource definitions
- `main.parameters.json` - Parameters file with default values
- `deploy.sh` - Automated deployment script
- `AZURE_DEPLOYMENT.md` - This documentation file

## Prerequisites

1. **Azure CLI** - Install from [here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
2. **Azure Subscription** - You need an active Azure subscription
3. **Permissions** - Contributor or Owner role on the subscription/resource group

## Quick Deployment

### Option 1: Using the Deployment Script (Recommended)

```bash
cd copilot-outputs
./deploy.sh
```

The script will:
- Validate your Azure CLI login
- Create the resource group if it doesn't exist
- Validate the Bicep template
- Deploy all resources
- Display deployment outputs

### Option 2: Manual Azure CLI Commands

```bash
# Login to Azure
az login

# Create resource group
az group create \
    --name rg-hypervelocity-engineering-dev \
    --location eastus2

# Deploy the template
az deployment group create \
    --resource-group rg-hypervelocity-engineering-dev \
    --template-file main.bicep \
    --parameters @main.parameters.json
```

## Configuration

You can customize the deployment by modifying the `main.parameters.json` file:

```json
{
  "location": "eastus2",           // Azure region
  "resourcePrefix": "hve",         // Prefix for resource names
  "environment": "dev",            // Environment suffix
  "openAiDeploymentName": "gpt-4o", // OpenAI model deployment name
  "openAiDeploymentCapacity": 30,  // OpenAI deployment capacity (TPM thousands)
  "appServicePlanSku": "B1"        // App Service plan SKU (B1, B2, B3, S1, S2, S3, P1v2, P2v2, P3v2)
}
```

## Resource Naming Convention

Resources follow this naming pattern:
- **OpenAI Account**: `{prefix}-openai-{environment}-{uniqueId}`
- **Search Service**: `{prefix}-search-{environment}-{uniqueId}`
- **Storage Account**: `{prefix}storage{environment}{uniqueId}`
- **App Service Plan**: `{prefix}-asp-{environment}-{uniqueId}`
- **Web App**: `{prefix}-webapp-{environment}-{uniqueId}`

Where:
- `{prefix}` = resourcePrefix parameter (default: "hve")
- `{environment}` = environment parameter (default: "dev")
- `{uniqueId}` = 6-character unique string based on resource group ID

## Post-Deployment Steps

After successful deployment:

1. **Get API Keys**:
   ```bash
   # OpenAI API Key
   az cognitiveservices account keys list \
       --name {openai-account-name} \
       --resource-group rg-hypervelocity-engineering-dev

   # Search Service API Key
   az search admin-key show \
       --resource-group rg-hypervelocity-engineering-dev \
       --service-name {search-service-name}

   # Storage Account Key
   az storage account keys list \
       --account-name {storage-account-name} \
       --resource-group rg-hypervelocity-engineering-dev
   ```

2. **Configure Application Settings**:
   The web app is pre-configured with these environment variables:
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_DEPLOYMENT_NAME`
   - `AZURE_SEARCH_ENDPOINT`
   - `AZURE_STORAGE_ACCOUNT_NAME`
   - `AZURE_STORAGE_BLOB_ENDPOINT`

3. **Deploy Your Application**:
   Use Azure DevOps, GitHub Actions, or manual deployment to deploy your application code to the web app.

## Estimated Costs

Approximate monthly costs for the default configuration (East US 2):
- **OpenAI GPT-4o**: ~$15-30 (depends on usage, 30K TPM capacity)
- **AI Search Basic**: ~$250/month
- **Storage Account**: ~$5-10 (depends on usage)
- **App Service Plan B1**: ~$13/month
- **Total**: ~$283-303/month

> **Note**: Costs may vary based on actual usage and current Azure pricing.

## Security Considerations

The template includes basic security configurations:
- HTTPS only for web app
- TLS 1.2 minimum for storage
- Public network access enabled (can be restricted post-deployment)
- Managed identity support for web app

For production deployments, consider:
- Implementing network restrictions
- Using Azure Key Vault for secrets
- Enabling diagnostic logging
- Setting up monitoring and alerts

## Troubleshooting

### Common Issues

1. **OpenAI Account Creation Failed**:
   - Ensure you have OpenAI service enabled in your subscription
   - Check regional availability for Azure OpenAI

2. **Search Service Name Conflicts**:
   - Search service names must be globally unique
   - The template includes a unique suffix to avoid conflicts

3. **Insufficient Permissions**:
   - Ensure you have Contributor or Owner role
   - Some services might require additional permissions

### Getting Help

1. Check Azure Activity Log for detailed error messages
2. Validate the template: `az deployment group validate`
3. Use `--debug` flag with Azure CLI for verbose output

## Clean Up

To delete all resources:

```bash
az group delete --name rg-hypervelocity-engineering-dev --yes --no-wait
```

> **Warning**: This will permanently delete all resources in the resource group.