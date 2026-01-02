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
    tablesConnectionString: storage.outputs.connectionString
    jwtSecret: jwtSecret
    corsOrigins: [storage.outputs.staticWebsiteEndpoint]
    appInsightsConnectionString: monitoring.outputs.appInsightsConnectionString
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
