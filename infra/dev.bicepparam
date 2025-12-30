// =============================================================================
// Development Environment Parameters
// =============================================================================
using 'main.bicep'

param environment = 'dev'
param location = 'brazilsouth'
param baseName = 'controlepgm'

// IMPORTANT: Replace with a secure secret before deployment
// Use: az keyvault secret show or generate a new one
param jwtSecret = 'REPLACE_WITH_SECURE_SECRET_MIN_32_CHARS'
