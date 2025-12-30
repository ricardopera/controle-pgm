// Monitoring module for Controle PGM
// Application Insights and Log Analytics workspace

@description('Azure region for resource deployment')
param location string

@description('Resource name prefix')
param baseName string

@description('Environment name')
@allowed(['dev', 'prod'])
param environment string

@description('Tags to apply to resources')
param tags object = {}

@description('Log Analytics retention in days')
@minValue(30)
@maxValue(730)
param retentionInDays int = 30

// Resource names
var logAnalyticsName = '${baseName}-log-${environment}'
var appInsightsName = '${baseName}-ai-${environment}'

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionInDays
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: {
      dailyQuotaGb: environment == 'dev' ? 1 : 5
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    Flow_Type: 'Redfield'
    Request_Source: 'IbizaAIExtension'
    WorkspaceResourceId: logAnalyticsWorkspace.id
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
    RetentionInDays: retentionInDays
    DisableLocalAuth: false
  }
}

// Outputs
@description('Log Analytics workspace name')
output logAnalyticsName string = logAnalyticsWorkspace.name

@description('Log Analytics workspace ID')
output logAnalyticsId string = logAnalyticsWorkspace.id

@description('Log Analytics workspace customer ID')
output logAnalyticsCustomerId string = logAnalyticsWorkspace.properties.customerId

@description('Application Insights name')
output appInsightsName string = appInsights.name

@description('Application Insights ID')
output appInsightsId string = appInsights.id

@description('Application Insights instrumentation key')
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey

@description('Application Insights connection string')
output appInsightsConnectionString string = appInsights.properties.ConnectionString
