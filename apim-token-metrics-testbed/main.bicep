// ============================================================================
// APIM Token Metrics + Audit Logging Test Bed
// Approach 1: emit-metric (generic) → App Insights custom metrics (billing)
// Approach 2: log-to-eventhub → Event Hub (audit/evaluation logging)
// Based on: Azure-Samples/ai-gateway labs/token-metrics-emitting
// ============================================================================

@description('Resource group location')
param location string = resourceGroup().location

@description('Resource name suffix')
param resourceSuffix string = uniqueString(subscription().id, resourceGroup().id)

@description('APIM SKU - Basicv2 recommended for testing')
@allowed(['Consumption', 'Developer', 'Basicv2', 'Standardv2'])
param apimSku string = 'Basicv2'

@description('APIM publisher name')
param apimPublisherName string = 'Token Metrics TestBed'

@description('APIM publisher email')
param apimPublisherEmail string = 'testbed@contoso.com'

@description('AI Services configuration - name and location for multi-region')
param aiServicesConfig array = [
  {
    name: 'foundry1'
    location: 'eastus2'
  }
]

@description('Model deployments - uses GPT-5.4 mini (reasoning model, supports reasoning_effort)')
param modelsConfig array = [
  {
    name: 'gpt-5.4-mini'
    publisher: 'OpenAI'
    version: '2026-03-17'
    sku: 'GlobalStandard'
    capacity: 20
  }
]

@description('APIM subscription configuration for multi-tenant billing test')
param apimSubscriptionsConfig array = [
  {
    name: 'tenant-a'
    displayName: 'Tenant A'
  }
  {
    name: 'tenant-b'
    displayName: 'Tenant B'
  }
  {
    name: 'tenant-c'
    displayName: 'Tenant C'
  }
]

// ============================================================================
// Log Analytics Workspace
// ============================================================================
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'law-${resourceSuffix}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// ============================================================================
// Application Insights - WithDimensions for custom metrics (Approach 1)
// ============================================================================
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${resourceSuffix}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    #disable-next-line BCP037
    CustomMetricsOptedInType: 'WithDimensions'  // CRITICAL: enables dimensions on custom metrics
  }
}

// ============================================================================
// Event Hub Namespace + Hub (Approach 2: audit logging)
// ============================================================================
resource eventHubNamespace 'Microsoft.EventHub/namespaces@2024-01-01' = {
  name: 'evhns-${resourceSuffix}'
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
    capacity: 1
  }
}

resource eventHub 'Microsoft.EventHub/namespaces/eventhubs@2024-01-01' = {
  parent: eventHubNamespace
  name: 'audit-logs'
  properties: {
    messageRetentionInDays: 3
    partitionCount: 2
  }
}

// RBAC: APIM -> Azure Event Hubs Data Sender (managed identity, no SAS needed)
resource apimToEventHubRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(apim.id, eventHubNamespace.id, '2b629674-e913-4c01-ae53-ef4638d8f975')
  scope: eventHubNamespace
  properties: {
    principalId: apim.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '2b629674-e913-4c01-ae53-ef4638d8f975'  // Azure Event Hubs Data Sender
    )
  }
}

// ============================================================================
// API Management
// ============================================================================
resource apim 'Microsoft.ApiManagement/service@2024-05-01' = {
  name: 'apim-${resourceSuffix}'
  location: location
  sku: {
    name: apimSku
    capacity: (apimSku == 'Consumption') ? 0 : 1
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    publisherName: apimPublisherName
    publisherEmail: apimPublisherEmail
  }
}

// App Insights logger for APIM (Approach 1)
resource apimLogger 'Microsoft.ApiManagement/service/loggers@2024-05-01' = {
  parent: apim
  name: 'appinsights-logger'
  properties: {
    loggerType: 'applicationInsights'
    credentials: {
      instrumentationKey: appInsights.properties.InstrumentationKey
    }
    resourceId: appInsights.id
  }
}

// APIM diagnostic: Wire App Insights logger to API telemetry (required for emit-metric)
resource apimAppInsightsDiagnostic 'Microsoft.ApiManagement/service/diagnostics@2024-05-01' = {
  parent: apim
  name: 'applicationinsights'
  properties: {
    loggerId: apimLogger.id
    alwaysLog: 'allErrors'
    sampling: {
      samplingType: 'fixed'
      percentage: 100
    }
    metrics: true
  }
}

// Diagnostic setting: Send APIM Gateway Logs to Log Analytics
resource apimDiagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  scope: apim
  name: 'apim-to-law'
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        category: 'GatewayLogs'
        enabled: true
      }
      {
        category: 'GatewayLlmLogs'
        enabled: true
      }
    ]
  }
}

// Named value: Event Hub REST endpoint for send-request policy (Approach 2)
// Uses REST API instead of log-to-eventhub because MCAPS policy disables SAS/local auth
resource eventHubEndpointNamedValue 'Microsoft.ApiManagement/service/namedValues@2024-05-01' = {
  parent: apim
  name: 'eventhub-endpoint'
  properties: {
    displayName: 'eventhub-endpoint'
    value: 'https://${eventHubNamespace.name}.servicebus.windows.net/${eventHub.name}/messages'
    secret: false
  }
}

// ============================================================================
// AI Foundry / Cognitive Services accounts
// ============================================================================
resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = [
  for config in aiServicesConfig: {
    name: 'ai-${config.name}-${resourceSuffix}'
    location: config.location
    kind: 'AIServices'
    sku: {
      name: 'S0'
    }
    properties: {
      customSubDomainName: 'ai-${config.name}-${resourceSuffix}'
      publicNetworkAccess: 'Enabled'
    }
  }
]

// Model deployments
resource modelDeployments 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = [
  for (model, i) in modelsConfig: {
    parent: aiServices[0]
    name: model.name
    sku: {
      name: model.sku
      capacity: model.capacity
    }
    properties: {
      model: {
        format: 'OpenAI'
        name: model.name
        version: model.version
      }
    }
  }
]

// RBAC: APIM -> Cognitive Services User
resource apimToAiRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [
  for (config, i) in aiServicesConfig: {
    name: guid(apim.id, aiServices[i].id, '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
    scope: aiServices[i]
    properties: {
      principalId: apim.identity.principalId
      principalType: 'ServicePrincipal'
      roleDefinitionId: subscriptionResourceId(
        'Microsoft.Authorization/roleDefinitions',
        '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'  // Cognitive Services OpenAI User
      )
    }
  }
]

// ============================================================================
// APIM API - Azure OpenAI Responses API
// ============================================================================
resource api 'Microsoft.ApiManagement/service/apis@2024-05-01' = {
  parent: apim
  name: 'azure-openai-api'
  properties: {
    path: 'openai'
    displayName: 'Azure OpenAI Responses API'
    protocols: ['https']
    subscriptionRequired: true
    subscriptionKeyParameterNames: {
      header: 'api-key'
      query: 'api-key'
    }
  }
}

// Responses API operation: POST /v1/responses
resource apiOperationCreateResponse 'Microsoft.ApiManagement/service/apis/operations@2024-05-01' = {
  parent: api
  name: 'create-response'
  properties: {
    displayName: 'Create Response'
    method: 'POST'
    urlTemplate: '/v1/responses'
  }
}

// Responses API operation: GET /v1/responses/{response_id}
resource apiOperationGetResponse 'Microsoft.ApiManagement/service/apis/operations@2024-05-01' = {
  parent: api
  name: 'get-response'
  properties: {
    displayName: 'Get Response'
    method: 'GET'
    urlTemplate: '/v1/responses/{response_id}'
    templateParameters: [
      {
        name: 'response_id'
        required: true
        type: 'string'
      }
    ]
  }
}

// Backend pool pointing to AI Services endpoint(s)
resource backend 'Microsoft.ApiManagement/service/backends@2024-05-01' = [
  for (config, i) in aiServicesConfig: {
    parent: apim
    name: 'ai-backend-${config.name}'
    properties: {
      protocol: 'http'
      url: '${aiServices[i].properties.endpoint}openai'
      tls: {
        validateCertificateChain: true
        validateCertificateName: true
      }
    }
  }
]

// API Policy - token metrics emitting
resource apiPolicy 'Microsoft.ApiManagement/service/apis/policies@2024-05-01' = {
  parent: api
  name: 'policy'
  properties: {
    format: 'rawxml'
    value: loadTextContent('policy.xml')
  }
}

// ============================================================================
// APIM Subscriptions for multi-tenant billing test
// ============================================================================
resource apimSubscriptions 'Microsoft.ApiManagement/service/subscriptions@2024-05-01' = [
  for config in apimSubscriptionsConfig: {
    parent: apim
    name: config.name
    properties: {
      displayName: config.displayName
      scope: '/apis/${api.name}'
      state: 'active'
    }
  }
]

// ============================================================================
// Outputs
// ============================================================================
output apimName string = apim.name
output apimGatewayUrl string = apim.properties.gatewayUrl
output apimResourceId string = apim.id
output appInsightsName string = appInsights.name
output appInsightsId string = appInsights.id
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
output eventHubNamespaceName string = eventHubNamespace.name
output eventHubName string = eventHub.name
output aiServicesEndpoints array = [
  for (config, i) in aiServicesConfig: {
    name: config.name
    endpoint: aiServices[i].properties.endpoint
  }
]
output subscriptionNames array = [for config in apimSubscriptionsConfig: config.name]
