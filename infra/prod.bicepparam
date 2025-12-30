// =============================================================================
// Production Environment Parameters
// =============================================================================
using 'main.bicep'

param environment = 'prod'
param location = 'brazilsouth'
param baseName = 'controlepgm'

// IMPORTANT: Replace with a secure secret before deployment
// Use: az keyvault secret show or generate a new one
// Production secrets should be stored in Azure Key Vault and referenced
param jwtSecret = 'REPLACE_WITH_SECURE_SECRET_MIN_32_CHARS'
