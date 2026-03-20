# Azure Infrastructure Deployment Script (PowerShell)
# This script deploys the Bicep template to create Azure OpenAI, AI Search, Storage, and App Service resources

param(
    [string]$ResourceGroupName = "rg-hypervelocity-engineering-dev",
    [string]$Location = "eastus2",
    [string]$BicepFile = "main.bicep",
    [string]$ParametersFile = "main.parameters.json"
)

# Configuration
$DeploymentName = "hve-infrastructure-$(Get-Date -Format 'yyyyMMdd-HHmmss')"

Write-Host "🚀 Azure Infrastructure Deployment" -ForegroundColor Blue
Write-Host "==================================" -ForegroundColor Blue
Write-Host "Resource Group: $ResourceGroupName" -ForegroundColor White
Write-Host "Location: $Location" -ForegroundColor White
Write-Host "Deployment Name: $DeploymentName" -ForegroundColor White
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "✅ Azure CLI version: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first." -ForegroundColor Red
    Write-Host "Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in
try {
    $account = az account show --output json | ConvertFrom-Json
    Write-Host "📋 Current subscription: $($account.name)" -ForegroundColor Blue
} catch {
    Write-Host "⚠️  You are not logged in to Azure. Please login first." -ForegroundColor Yellow
    Write-Host "Run: az login" -ForegroundColor White
    exit 1
}

Write-Host ""

# Create resource group if it doesn't exist
Write-Host "🏗️  Creating resource group..." -ForegroundColor Yellow
try {
    az group create --name $ResourceGroupName --location $Location --output table
    Write-Host "✅ Resource group created/verified" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create resource group" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Validate the Bicep template
Write-Host "✅ Validating Bicep template..." -ForegroundColor Yellow
try {
    az deployment group validate `
        --resource-group $ResourceGroupName `
        --template-file $BicepFile `
        --parameters "@$ParametersFile"
    
    Write-Host "✅ Template validation successful" -ForegroundColor Green
} catch {
    Write-Host "❌ Template validation failed" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Deploy the infrastructure
Write-Host "🚀 Deploying infrastructure..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor White
Write-Host ""

try {
    az deployment group create `
        --resource-group $ResourceGroupName `
        --name $DeploymentName `
        --template-file $BicepFile `
        --parameters "@$ParametersFile" `
        --output table
    
    Write-Host ""
    Write-Host "✅ Deployment completed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Get deployment outputs
    Write-Host "📋 Deployment Outputs:" -ForegroundColor Blue
    az deployment group show `
        --resource-group $ResourceGroupName `
        --name $DeploymentName `
        --query properties.outputs `
        --output table
    
    Write-Host ""
    Write-Host "🎉 Your Azure infrastructure is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Blue
    Write-Host "1. Get the API keys from Azure Portal for OpenAI and Search services" -ForegroundColor White
    Write-Host "2. Configure your application with the service endpoints" -ForegroundColor White
    Write-Host "3. Deploy your application to the Web App" -ForegroundColor White
    
} catch {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}