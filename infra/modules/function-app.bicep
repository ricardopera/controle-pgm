// Azure Function App module for Controle PGM
// Python 3.11 on Consumption (Linux) plan

@description('Azure region for resource deployment')
param location string

@description('Resource name prefix')
param baseName string

@description('Environment name')
@allowed(['dev', 'prod'])
param environment string

@description('Tags to apply to resources')
param tags object = {}

@description('Storage account connection string for function app')
@secure()
param storageConnectionString string

@description('Azure Tables connection string')
@secure()
param tablesConnectionString string

@description('JWT secret for authentication')
@secure()
param jwtSecret string

@description('Allowed CORS origins')
param corsOrigins array = ['*']

@description('Application Insights connection string')
param appInsightsConnectionString string = ''

// Resource names
var functionAppName = '${baseName}-api-${environment}'
var hostingPlanName = '${baseName}-plan-${environment}'

// Consumption Plan (Linux)
resource hostingPlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: hostingPlanName
  location: location
  tags: tags
  sku: {
    name: 'Y1'
    tier: 'Dynamic'
  }
  kind: 'functionapp'
  properties: {
    reserved: true // Required for Linux
  }
}

// Function App
resource functionApp 'Microsoft.Web/sites@2023-12-01' = {
  name: functionAppName
  location: location
  tags: tags
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: hostingPlan.id
    httpsOnly: true
    publicNetworkAccess: 'Enabled'
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      cors: {
        allowedOrigins: corsOrigins
      }
      appSettings: [
        {
          name: 'AzureWebJobsStorage'
          value: storageConnectionString
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~4'
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
        {
          name: 'AZURE_TABLES_CONNECTION_STRING'
          value: tablesConnectionString
        }
        {
          name: 'JWT_SECRET'
          value: jwtSecret
        }
        {
          name: 'JWT_EXPIRATION_HOURS'
          value: '8'
        }
        {
          name: 'CORS_ORIGINS'
          value: join(corsOrigins, ',')
        }
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: appInsightsConnectionString
        }
      ]
    }
  }
}

// Outputs
@description('Function App name')
output functionAppName string = functionApp.name

@description('Function App ID')
output functionAppId string = functionApp.id

@description('Function App default hostname')
output functionAppHostname string = functionApp.properties.defaultHostName

@description('Function App URL')
output functionAppUrl string = 'https://${functionApp.properties.defaultHostName}'

@description('Function App managed identity principal ID')
output managedIdentityPrincipalId string = functionApp.identity.principalId

@description('Hosting plan name')
output hostingPlanName string = hostingPlan.name
