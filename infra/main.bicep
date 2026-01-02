// =============================================================================
// Controle PGM - Main Bicep Template
// =============================================================================
// Description: Infrastructure as Code for Controle de Numeração de Documentos
// Target: Azure Brazil South
// Resource Group: controle-pgm
// =============================================================================

targetScope = 'resourceGroup'

// =============================================================================
// Parameters
// =============================================================================

@description('Environment name (dev, prod)')
@allowed(['dev', 'prod'])
param environment string

@description('Azure region for deployment')
param location string = 'brazilsouth'

@description('Base name for resources')
param baseName string = 'controlepgm'

@description('JWT secret for authentication')
@secure()
param jwtSecret string

@description('Tags to apply to all resources')
param tags object = {
  project: 'controle-pgm'
  environment: environment
  managedBy: 'bicep'
}

// =============================================================================
// Modules
// =============================================================================

// Monitoring (Log Analytics + Application Insights)
module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring-deployment'
  params: {
    baseName: baseName
    environment: environment
    location: location
    tags: tags
    retentionInDays: environment == 'prod' ? 90 : 30
  }
}

// Storage Account (Tables + Static Website)
module storage 'modules/storage.bicep' = {
  name: 'storage-deployment'
  params: {
    baseName: baseName
    environment: environment
    location: location
    tags: tags
  }
}

// Key Vault
module keyvault 'modules/keyvault.bicep' = {
  name: 'keyvault-deployment'
  params: {
    baseName: baseName
    location: location
    tags: tags
    accessPrincipalIds: [functionApp.outputs.managedIdentityPrincipalId]
  }
}

// Function App
module functionApp 'modules/function-app.bicep' = {
  name: 'functionapp-deployment'
  params: {
    baseName: baseName
    environment: environment
    location: location
    tags: tags
    storageConnectionString: storage.outputs.connectionString
    storageBlobEndpoint: storage.outputs.primaryEndpoints.blob
    tablesConnectionString: storage.outputs.connectionString
    jwtSecret: jwtSecret
    corsOrigins: [storage.outputs.staticWebsiteEndpoint]
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
  }
}

// Reference existing storage account for role assignment
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: storage.outputs.storageAccountName
}

// Role Assignment: Function App to Storage Account (Storage Blob Data Contributor)
// Required for Flex Consumption deployment
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, functionApp.outputs.managedIdentityPrincipalId, 'ba92f572-3b2b-4ada-a4c0-d617f42b06b1')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f572-3b2b-4ada-a4c0-d617f42b06b1')
    principalId: functionApp.outputs.managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
  }
}

// =============================================================================
// Outputs
// =============================================================================

@description('Storage account name')
output storageAccountName string = storage.outputs.storageAccountName

@description('Function App URL')
output functionAppUrl string = functionApp.outputs.functionAppUrl

@description('Static website URL')
output staticWebsiteUrl string = storage.outputs.staticWebsiteEndpoint

@description('Application Insights name')
output appInsightsName string = monitoring.outputs.appInsightsName

@description('Key Vault name')
output keyVaultName string = keyvault.outputs.keyVaultName

@description('Key Vault URI')
output keyVaultUri string = keyvault.outputs.keyVaultUri
