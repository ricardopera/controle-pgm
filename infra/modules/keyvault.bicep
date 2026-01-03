// Azure Key Vault module for Controle PGM
// Stores secrets like JWT key and connection strings

@description('Azure region for resource deployment')
param location string

@description('Resource name prefix')
param baseName string

@description('Tags to apply to resources')
param tags object = {}

@description('Principal IDs that should have access to secrets')
param accessPrincipalIds array = []

@description('Tenant ID for Key Vault')
param tenantId string = subscription().tenantId

// Resource name
var keyVaultName = 'kv-${baseName}'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: take(keyVaultName, 24)
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: tenantId
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
    enableRbacAuthorization: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// Role assignment for secret access (Key Vault Secrets User)
resource secretsUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for principalId in accessPrincipalIds: {
  name: guid(keyVault.id, principalId, '4633458b-17de-408a-b874-0445c86b69e6')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}]

// Outputs
@description('Key Vault name')
output keyVaultName string = keyVault.name

@description('Key Vault ID')
output keyVaultId string = keyVault.id

@description('Key Vault URI')
output keyVaultUri string = keyVault.properties.vaultUri
