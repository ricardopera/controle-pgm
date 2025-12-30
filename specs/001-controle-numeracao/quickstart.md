# Quickstart: Controle de Numeração PGM

Guia rápido para configurar o ambiente de desenvolvimento local.

## Pré-requisitos

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 20+** - [Download](https://nodejs.org/)
- **Azure CLI** - [Instalação](https://learn.microsoft.com/pt-br/cli/azure/install-azure-cli)
- **Azure Functions Core Tools v4** - [Instalação](https://learn.microsoft.com/pt-br/azure/azure-functions/functions-run-local)
- **Azurite** (emulador local) - `npm install -g azurite`

## 1. Clone e Estrutura

```bash
cd /home/ricardo/projetos/controle-pgm
```

O projeto segue esta estrutura:
```
controle-pgm/
├── backend/     # Azure Functions Python
├── frontend/    # React SPA
├── infra/       # Bicep IaC
└── specs/       # Documentação
```

## 2. Backend Setup

### 2.1 Ambiente Virtual Python

```bash
cd backend

# Criar ambiente virtual
python -m venv .venv

# Ativar (Linux/Mac)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2.2 Configurar Local Settings

```bash
# Copiar template
cp local.settings.json.template local.settings.json
```

Editar `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_TABLES_CONNECTION_STRING": "UseDevelopmentStorage=true",
    "JWT_SECRET": "dev-secret-change-in-production-min-32-chars",
    "CORS_ORIGINS": "http://localhost:5173"
  }
}
```

### 2.3 Iniciar Azurite (Emulador Storage)

Em um terminal separado:
```bash
azurite --silent --location ~/.azurite --debug ~/.azurite/debug.log
```

### 2.4 Iniciar Backend

```bash
# No diretório backend/
func start
```

Backend disponível em: `http://localhost:7071`

### 2.5 Seed de Dados Iniciais

```bash
# Com backend rodando
python scripts/seed.py
```

Isso cria:
- Tipos de documento: Comunicação Interna, Ofício, Despacho
- Usuário admin: `admin@pgm.local` / `Admin123!`

## 3. Frontend Setup

### 3.1 Instalar Dependências

```bash
cd frontend
npm install
```

### 3.2 Configurar Ambiente

Criar arquivo `.env.local`:
```env
VITE_API_URL=http://localhost:7071/api
```

### 3.3 Iniciar Frontend

```bash
npm run dev
```

Frontend disponível em: `http://localhost:5173`

## 4. Testes

### Backend (pytest)

```bash
cd backend
source .venv/bin/activate

# Todos os testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html

# Apenas unitários
pytest tests/unit/

# Apenas integração (requer Azurite)
pytest tests/integration/
```

### Frontend (Vitest)

```bash
cd frontend

# Modo watch
npm run test

# CI mode
npm run test:ci

# Com cobertura
npm run test:coverage
```

### E2E (Playwright)

```bash
cd frontend

# Instalar browsers
npx playwright install

# Rodar (backend e frontend devem estar up)
npm run test:e2e
```

## 5. Lint e Format

### Backend

```bash
cd backend
source .venv/bin/activate

# Lint
ruff check .

# Fix automático
ruff check --fix .

# Format
ruff format .
```

### Frontend

```bash
cd frontend

# Lint
npm run lint

# Fix
npm run lint:fix

# Format
npm run format
```

## 6. Deploy Local da Infra (Opcional)

Para testar Bicep localmente:

```bash
# Login Azure
az login

# Selecionar subscription
az account set --subscription "SUA_SUBSCRIPTION_ID"

# Deploy para resource group existente
cd infra
az deployment group create \
  --resource-group controle-pgm \
  --template-file main.bicep \
  --parameters parameters/dev.bicepparam
```

## URLs Locais

| Serviço | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:7071/api |
| Azurite Blob | http://127.0.0.1:10000 |
| Azurite Queue | http://127.0.0.1:10001 |
| Azurite Table | http://127.0.0.1:10002 |

## Credenciais de Desenvolvimento

| Usuário | Email | Senha | Role |
|---------|-------|-------|------|
| Admin | admin@pgm.local | Admin123! | admin |

## Troubleshooting

### Azurite não conecta

```bash
# Verificar se está rodando
lsof -i :10002

# Reiniciar
pkill azurite
azurite --silent
```

### Function App não inicia

```bash
# Verificar versão
func --version  # Deve ser 4.x

# Limpar cache
rm -rf .python_packages
pip install -r requirements.txt
```

### Frontend não conecta no backend

1. Verificar se backend está rodando na porta 7071
2. Verificar CORS_ORIGINS no `local.settings.json`
3. Verificar VITE_API_URL no `.env.local`

### Erro de tipo no Azure Tables

Se receber erro de serialização, verificar se datetime está em UTC:
```python
from datetime import datetime, timezone
created_at = datetime.now(timezone.utc)
```

## Próximos Passos

1. Explore a API em `http://localhost:7071/api/health`
2. Faça login no frontend com as credenciais acima
3. Teste a geração de número
4. Veja o histórico

Para dúvidas, consulte [spec.md](spec.md) e [plan.md](plan.md).
