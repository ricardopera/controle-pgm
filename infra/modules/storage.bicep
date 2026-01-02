// Storage Account module for Controle PGM
// Includes Azure Tables and Static Website hosting

@description('Azure region for resource deployment')
param location string

@description('Resource name prefix')
param baseName string

@description('Environment name')
@allowed(['dev', 'prod'])
param environment string

@description('Tags to apply to resources')
param tags object = {}

// Storage account name must be lowercase, alphanumeric, 3-24 chars
var storageAccountName = toLower(replace('${baseName}${environment}', '-', ''))

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: length(storageAccountName) > 24 ? substring(storageAccountName, 0, 24) : storageAccountName
  location: location
  tags: tags
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    allowSharedKeyAccess: true
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
    // Enable static website
    // Note: Static website must be enabled via a separate call or Azure CLI
  }
}

// Table service for Azure Tables
resource tableService 'Microsoft.Storage/storageAccounts/tableServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {}
}

// Create required tables
resource usersTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: 'Users'
}

resource documentTypesTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: 'DocumentTypes'
}

resource sequencesTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: 'Sequences'
}

resource numberLogsTable 'Microsoft.Storage/storageAccounts/tableServices/tables@2023-05-01' = {
  parent: tableService
  name: 'NumberLogs'
}

// Blob service for static website
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
  properties: {
    cors: {
      corsRules: [
        {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'HEAD', 'OPTIONS']
          allowedHeaders: ['*']
          exposedHeaders: ['*']
          maxAgeInSeconds: 3600
        }
      ]
    }
  }
}

// Container for static website content (created by enabling static website)
resource webContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: '$web'
  properties: {
    publicAccess: 'None'
  }
}

// Container for Flex Consumption deployment packages
resource deploymentContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: 'deploymentpackage'
  properties: {
    publicAccess: 'None'
  }
}

// Outputs
@description('Storage account name')
output storageAccountName string = storageAccount.name

@description('Storage account ID')
output storageAccountId string = storageAccount.id

@description('Storage account primary endpoints')
output primaryEndpoints object = storageAccount.properties.primaryEndpoints

@description('Table service endpoint')
output tableEndpoint string = storageAccount.properties.primaryEndpoints.table

@description('Static website endpoint')
output staticWebsiteEndpoint string = storageAccount.properties.primaryEndpoints.web

// Note: Connection string is output for convenience but should be stored in Key Vault for production
@description('Connection string for Azure Tables (use Key Vault in production)')
#disable-next-line outputs-should-not-contain-secrets
output connectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${az.environment().suffixes.storage}'
