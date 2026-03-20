// PROFISEE Multi-Agent MDM System - Azure Infrastructure as Code
// Partner: PROFISEE
// Use Case: Multi-Agent Master Data Management System  
// Technologies: Microsoft Agent Framework (MAF), Azure AI Services
// Author: Arturo Quiroga, Partner Solutions Architect
// Date: March 2026

@description('The name prefix for all resources')
param resourcePrefix string = 'profisee-mdm'

@description('The location for all resources')
param location string = resourceGroup().location

@description('The environment name (dev, test, prod)')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string = 'dev'

@description('The SKU for Azure OpenAI')
@allowed([
  'S0'
])
param openAiSku string = 'S0'

@description('The SKU for Azure AI Search')
@allowed([
  'free'
  'basic'
  'standard'
  'standard2'
  'standard3'
  'storage_optimized_l1'
  'storage_optimized_l2'
])
param searchSku string = 'basic'

@description('The SKU for Cosmos DB')
@allowed([
  'Free'
  'Standard'
])
param cosmosDbSku string = 'Standard'

@description('The administrator login for Azure SQL Database')
param sqlAdministratorLogin string

@description('The administrator password for Azure SQL Database')
@secure()
param sqlAdministratorPassword string

// Variables
var uniqueSuffix = substring(uniqueString(resourceGroup().id), 0, 6)
var resourceName = '${resourcePrefix}-${environment}-${uniqueSuffix}'

// ============================================================================
// Azure OpenAI Service
// ============================================================================

resource openAiAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${resourceName}-openai'
  location: location
  sku: {
    name: openAiSku
  }
  kind: 'OpenAI'
  properties: {
    apiProperties: {
      statisticsEnabled: false
    }
    customSubDomainName: '${resourceName}-openai'
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// GPT-4o deployment for agent conversations
resource gpt4oDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiAccount
  name: 'gpt-4o-profisee'
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-05-13'
    }
    raiPolicyName: 'Microsoft.Default'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
  sku: {
    name: 'Standard'
    capacity: 30
  }
}

// Text Embedding deployment for vector search
resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  parent: openAiAccount
  name: 'text-embedding-ada-002'
  dependsOn: [
    gpt4oDeployment
  ]
  properties: {
    model: {
      format: 'OpenAI'
      name: 'text-embedding-ada-002'
      version: '2'
    }
    raiPolicyName: 'Microsoft.Default'
    versionUpgradeOption: 'OnceCurrentVersionExpired'
  }
  sku: {
    name: 'Standard'
    capacity: 30
  }
}

// ============================================================================
// Azure AI Search Service  
// ============================================================================

resource searchService 'Microsoft.Search/searchServices@2023-11-01' = {
  name: '${resourceName}-search'
  location: location
  sku: {
    name: searchSku
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    publicNetworkAccess: 'enabled'
    networkRuleSet: {
      ipRules: []
    }
    disableLocalAuth: false
    authOptions: {
      apiKeyOnly: {}
    }
    semanticSearch: 'free'
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// ============================================================================
// Azure Text Analytics (Language Service)
// ============================================================================

resource textAnalyticsService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${resourceName}-textanalytics'
  location: location
  sku: {
    name: 'S'
  }
  kind: 'TextAnalytics'
  properties: {
    apiProperties: {
      statisticsEnabled: false
    }
    customSubDomainName: '${resourceName}-textanalytics'
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// ============================================================================
// Azure Document Intelligence
// ============================================================================

resource documentIntelligenceService 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: '${resourceName}-docintel'
  location: location
  sku: {
    name: 'S0'
  }
  kind: 'FormRecognizer'
  properties: {
    apiProperties: {
      statisticsEnabled: false
    }
    customSubDomainName: '${resourceName}-docintel'
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: false
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// ============================================================================
// Azure Cosmos DB (Multi-Model Database)
// ============================================================================

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-09-15' = {
  name: '${resourceName}-cosmos'
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    isVirtualNetworkFilterEnabled: false
    virtualNetworkRules: []
    disableKeyBasedMetadataWriteAccess: false
    enableFreeTier: environment == 'dev' ? true : false
    enableAnalyticalStorage: true
    analyticalStorageConfiguration: {
      schemaType: 'WellDefined'
    }
    databaseAccountOfferType: 'Standard'
    defaultIdentity: 'FirstPartyIdentity'
    networkAclBypass: 'None'
    disableLocalAuth: false
    enablePartitionMerge: false
    enableBurstCapacity: false
    minimalTlsVersion: 'Tls12'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
      maxIntervalInSeconds: 86400
      maxStalenessPrefix: 1000000
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableServerless'
      }
    ]
    ipRules: []
    backupPolicy: {
      type: 'Periodic'
      periodicModeProperties: {
        backupIntervalInMinutes: 1440
        backupRetentionIntervalInHours: 48
        backupStorageRedundancy: 'Local'
      }
    }
    networkAclBypassResourceIds: []
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// Cosmos DB Database for MDM
resource cosmosDatabase 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2023-09-15' = {
  parent: cosmosAccount
  name: 'ProfiseeMDM'
  properties: {
    resource: {
      id: 'ProfiseeMDM'
    }
  }
}

// Container for Master Entities
resource masterEntitiesContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-09-15' = {
  parent: cosmosDatabase
  name: 'MasterEntities'
  properties: {
    resource: {
      id: 'MasterEntities'
      partitionKey: {
        paths: [
          '/entity_type'
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
      }
      defaultTtl: -1
      uniqueKeyPolicy: {
        uniqueKeys: []
      }
      conflictResolutionPolicy: {
        mode: 'LastWriterWins'
        conflictResolutionPath: '/_ts'
      }
      analyticalStorageTtl: 7776000
    }
  }
}

// Container for Entity Relationships  
resource entityRelationshipsContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-09-15' = {
  parent: cosmosDatabase
  name: 'EntityRelationships'
  properties: {
    resource: {
      id: 'EntityRelationships'
      partitionKey: {
        paths: [
          '/source_entity_id'
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
      }
      defaultTtl: -1
      uniqueKeyPolicy: {
        uniqueKeys: []
      }
      conflictResolutionPolicy: {
        mode: 'LastWriterWins'
        conflictResolutionPath: '/_ts'
      }
      analyticalStorageTtl: 7776000
    }
  }
}

// Container for Audit Trail
resource auditTrailContainer 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2023-09-15' = {
  parent: cosmosDatabase
  name: 'AuditTrail'
  properties: {
    resource: {
      id: 'AuditTrail'
      partitionKey: {
        paths: [
          '/record_id'
        ]
        kind: 'Hash'
      }
      indexingPolicy: {
        indexingMode: 'consistent'
        automatic: true
        includedPaths: [
          {
            path: '/*'
          }
        ]
        excludedPaths: [
          {
            path: '/"_etag"/?'
          }
        ]
      }
      defaultTtl: 2592000  // 30 days retention
      uniqueKeyPolicy: {
        uniqueKeys: []
      }
      conflictResolutionPolicy: {
        mode: 'LastWriterWins'
        conflictResolutionPath: '/_ts'
      }
      analyticalStorageTtl: 7776000
    }
  }
}

// ============================================================================
// Azure SQL Database (Metadata Store)
// ============================================================================

resource sqlServer 'Microsoft.Sql/servers@2023-05-01-preview' = {
  name: '${resourceName}-sql'
  location: location
  properties: {
    administratorLogin: sqlAdministratorLogin
    administratorLoginPassword: sqlAdministratorPassword
    version: '12.0'
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    restrictOutboundNetworkAccess: 'Disabled'
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-05-01-preview' = {
  parent: sqlServer
  name: 'ProfiseeMDMMetadata'
  location: location
  sku: {
    name: environment == 'prod' ? 'S2' : 'S0'
    tier: 'Standard'
  }
  properties: {
    collation: 'SQL_Latin1_General_CP1_CI_AS'
    maxSizeBytes: environment == 'prod' ? 268435456000 : 2147483648 // 250GB for prod, 2GB for dev/test
    catalogCollation: 'SQL_Latin1_General_CP1_CI_AS'
    zoneRedundant: false
    readScale: 'Disabled'
    requestedBackupStorageRedundancy: 'Local'
    isLedgerOn: false
    availabilityZone: 'NoPreference'
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// Allow Azure services access to SQL Server
resource sqlFirewallRule 'Microsoft.Sql/servers/firewallRules@2023-05-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

// ============================================================================
// Azure Blob Storage (Document Store)
// ============================================================================

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: '${replace(resourceName, '-', '')}storage'
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    dnsEndpointType: 'Standard'
    defaultToOAuthAuthentication: false
    publicNetworkAccess: 'Enabled'
    allowCrossTenantReplication: false
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      requireInfrastructureEncryption: false
      services: {
        file: {
          keyType: 'Account'
          enabled: true
        }
        blob: {
          keyType: 'Account'
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Hot'
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// Blob container for documents
resource documentsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/documents'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
}

// Blob container for processed files
resource processedContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  name: '${storageAccount.name}/default/processed'
  properties: {
    immutableStorageWithVersioning: {
      enabled: false
    }
    defaultEncryptionScope: '$account-encryption-key'
    denyEncryptionScopeOverride: false
    publicAccess: 'None'
  }
}

// ============================================================================
// Azure Key Vault (Secrets Management)
// ============================================================================

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: '${resourceName}-kv'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenant().tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enableRbacAuthorization: true
    vaultUri: 'https://${resourceName}-kv.vault.azure.net/'
    provisioningState: 'Succeeded'
    publicNetworkAccess: 'Enabled'
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// Store OpenAI API key in Key Vault
resource openAiKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'azure-openai-api-key'
  properties: {
    value: openAiAccount.listKeys().key1
    contentType: 'text/plain'
  }
}

// Store Search service key in Key Vault
resource searchKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'azure-search-api-key'
  properties: {
    value: searchService.listAdminKeys().primaryKey
    contentType: 'text/plain'
  }
}

// Store Cosmos DB key in Key Vault  
resource cosmosKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'cosmos-db-key'
  properties: {
    value: cosmosAccount.listKeys().primaryMasterKey
    contentType: 'text/plain'
  }
}

// Store Text Analytics key in Key Vault
resource textAnalyticsKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'text-analytics-api-key'
  properties: {
    value: textAnalyticsService.listKeys().key1
    contentType: 'text/plain'
  }
}

// Store Storage account key in Key Vault
resource storageKeySecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'storage-account-key'
  properties: {
    value: storageAccount.listKeys().keys[0].value
    contentType: 'text/plain'
  }
}

// ============================================================================
// Azure Container Registry (for MAF Agent Images)
// ============================================================================

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: '${replace(resourceName, '-', '')}acr'
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
    policies: {
      quarantinePolicy: {
        status: 'disabled'
      }
      trustPolicy: {
        type: 'Notary'
        status: 'disabled'
      }
      retentionPolicy: {
        days: 7
        status: 'disabled'
      }
      exportPolicy: {
        status: 'enabled'
      }
      azureADAuthenticationAsArmPolicy: {
        status: 'enabled'
      }
      softDeletePolicy: {
        retentionDays: 7
        status: 'disabled'
      }
    }
    encryption: {
      status: 'disabled'
    }
    dataEndpointEnabled: false
    publicNetworkAccess: 'Enabled'
    networkRuleBypassOptions: 'AzureServices'
    zoneRedundancy: 'Disabled'
    anonymousPullEnabled: false
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// ============================================================================
// Azure Container Apps Environment (for MAF Agent Hosting)
// ============================================================================

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: '${resourceName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: {
      dailyQuotaGb: -1
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: '${resourceName}-containerenv'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// ============================================================================
// Azure Application Insights (Monitoring)
// ============================================================================

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${resourceName}-insights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
  tags: {
    Environment: environment
    Project: 'PROFISEE-MDM'
    Owner: 'Partner-Solutions-Architecture'
  }
}

// ============================================================================
// Outputs
// ============================================================================

@description('The resource group name where all resources are deployed')
output resourceGroupName string = resourceGroup().name

@description('The Azure OpenAI service endpoint')
output openAiEndpoint string = openAiAccount.properties.endpoint

@description('The Azure OpenAI service name')
output openAiAccountName string = openAiAccount.name

@description('The GPT-4o deployment name')
output gpt4oDeploymentName string = gpt4oDeployment.name

@description('The text embedding deployment name')
output embeddingDeploymentName string = embeddingDeployment.name

@description('The Azure AI Search service name')
output searchServiceName string = searchService.name

@description('The Azure AI Search service endpoint')
output searchServiceEndpoint string = 'https://${searchService.name}.search.windows.net'

@description('The Text Analytics service endpoint')
output textAnalyticsEndpoint string = textAnalyticsService.properties.endpoint

@description('The Document Intelligence service endpoint')
output documentIntelligenceEndpoint string = documentIntelligenceService.properties.endpoint

@description('The Cosmos DB account endpoint')
output cosmosDbEndpoint string = cosmosAccount.properties.documentEndpoint

@description('The Cosmos DB database name')
output cosmosDbDatabaseName string = cosmosDatabase.name

@description('The SQL Server name')
output sqlServerName string = sqlServer.name

@description('The SQL Database name')
output sqlDatabaseName string = sqlDatabase.name

@description('The SQL Server FQDN')
output sqlServerFqdn string = sqlServer.properties.fullyQualifiedDomainName

@description('The Storage Account name')
output storageAccountName string = storageAccount.name

@description('The Blob Storage endpoint')
output blobStorageEndpoint string = storageAccount.properties.primaryEndpoints.blob

@description('The Key Vault name')
output keyVaultName string = keyVault.name

@description('The Key Vault URI')
output keyVaultUri string = keyVault.properties.vaultUri

@description('The Container Registry name')
output containerRegistryName string = containerRegistry.name

@description('The Container Registry login server')
output containerRegistryLoginServer string = containerRegistry.properties.loginServer

@description('The Container Apps Environment name')
output containerAppsEnvironmentName string = containerAppsEnvironment.name

@description('The Application Insights connection string')
output applicationInsightsConnectionString string = applicationInsights.properties.ConnectionString

@description('The Log Analytics Workspace ID')
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.properties.customerId

// Resource configuration summary for deployment scripts
@description('Complete configuration for environment variables')
output environmentConfiguration object = {
  AZURE_OPENAI_ENDPOINT: openAiAccount.properties.endpoint
  AZURE_OPENAI_DEPLOYMENT_NAME: gpt4oDeployment.name
  AZURE_OPENAI_EMBEDDING_DEPLOYMENT: embeddingDeployment.name
  AZURE_SEARCH_SERVICE_NAME: searchService.name
  AZURE_SEARCH_ENDPOINT: 'https://${searchService.name}.search.windows.net'
  TEXT_ANALYTICS_ENDPOINT: textAnalyticsService.properties.endpoint
  DOCUMENT_INTELLIGENCE_ENDPOINT: documentIntelligenceService.properties.endpoint
  COSMOS_DB_ENDPOINT: cosmosAccount.properties.documentEndpoint
  COSMOS_DB_DATABASE_NAME: cosmosDatabase.name
  SQL_SERVER_FQDN: sqlServer.properties.fullyQualifiedDomainName
  SQL_DATABASE_NAME: sqlDatabase.name
  STORAGE_ACCOUNT_NAME: storageAccount.name
  BLOB_STORAGE_ENDPOINT: storageAccount.properties.primaryEndpoints.blob
  KEY_VAULT_URI: keyVault.properties.vaultUri
  CONTAINER_REGISTRY_LOGIN_SERVER: containerRegistry.properties.loginServer
  APPLICATION_INSIGHTS_CONNECTION_STRING: applicationInsights.properties.ConnectionString
  LOG_ANALYTICS_WORKSPACE_ID: logAnalyticsWorkspace.properties.customerId
}