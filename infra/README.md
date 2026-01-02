# Infraestrutura - Controle PGM

Configuração de infraestrutura como código (IaC) usando Azure Bicep.

## 📁 Estrutura

```
infra/
├── main.bicep           # Template principal
├── parameters.json      # Parâmetros de configuração
├── modules/            # Módulos Bicep reutilizáveis
│   ├── storage.bicep
│   ├── function-app.bicep
│   └── tables.bicep
└── README.md           # Esta documentação
```

## 🏗️ Recursos Provisionados

| Recurso | Nome | Descrição |
|---------|------|-----------|
| Storage Account | controlepgmdev | Armazena site estático e tabelas |
| Function App | controlepgm-api-dev | API backend (Flex Consumption) |
| Azure Tables | Users, DocumentTypes, Sequences, NumberLogs | Dados do sistema |
| Key Vault | kv-controle-pgm | Armazenamento de segredos |

## 🌍 Região

Todos os recursos são provisionados em **Brazil South** (`brazilsouth`).

## 🚀 Deploy Manual

### Pré-requisitos

- Azure CLI instalado e autenticado
- Resource Group criado: `controle-pgm`

### Comandos

```bash
# Validar template
az bicep build --file main.bicep --stdout > /dev/null

# Preview das mudanças
az deployment group what-if \
  --resource-group controle-pgm \
  --template-file main.bicep \
  --parameters parameters.json

# Deploy
az deployment group create \
  --resource-group controle-pgm \
  --template-file main.bicep \
  --parameters parameters.json
```

## 📊 Outputs

Após o deploy, os seguintes outputs são disponibilizados:

- `storageAccountName`: Nome do Storage Account
- `functionAppName`: Nome do Function App
- `staticWebsiteUrl`: URL do site estático
- `functionAppUrl`: URL da API

## 🔐 Configuração

### Variáveis de Ambiente do Function App

| Variável | Descrição |
|----------|-----------|
| `AZURE_TABLES_CONNECTION_STRING` | Connection string do Azure Tables |
| `JWT_SECRET` | Chave secreta para assinatura de tokens JWT |
| `CORS_ORIGINS` | Origens permitidas para CORS |
| `ENVIRONMENT` | Ambiente (development, staging, production) |

### Parâmetros do Template

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `environment` | string | Ambiente de deploy |
| `jwtSecret` | secureString | Chave JWT (mínimo 32 caracteres) |
| `corsOrigins` | string | Origens CORS separadas por vírgula |

## 🔄 CI/CD

O deploy é automatizado via GitHub Actions em `.github/workflows/infra.yml`:

1. Push para `main` em `infra/**` dispara o workflow
2. Validação do template Bicep
3. What-if para preview
4. Deploy para produção (apenas em push para main)

## 📝 Notas

- O Storage Account usa replicação LRS (locally redundant)
- O Function App usa o plano Flex Consumption (serverless)
- As tabelas são criadas automaticamente pelo código no primeiro uso
