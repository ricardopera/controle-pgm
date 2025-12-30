# Backend API - Controle PGM

API REST em Python para o sistema de controle de numeração de documentos.

## 🛠️ Stack

- **Runtime**: Python 3.11
- **Framework**: Azure Functions v4 (Blueprint pattern)
- **Validação**: Pydantic v2
- **Autenticação**: PyJWT + bcrypt
- **Banco de Dados**: Azure Tables (azure-data-tables)

## 📁 Estrutura

```
backend/
├── core/                    # Núcleo da aplicação
│   ├── config.py           # Configurações e variáveis de ambiente
│   ├── exceptions.py       # Exceções customizadas
│   ├── middleware.py       # Decoradores de autenticação e erros
│   └── tables.py           # Conexões com Azure Tables
├── functions/              # Endpoints da API
│   ├── auth/              # Autenticação
│   ├── document_types/    # CRUD tipos de documento
│   ├── history/           # Histórico e exportação
│   ├── numbers/           # Geração de números
│   └── users/             # CRUD usuários
├── models/                 # Modelos Pydantic
│   ├── user.py
│   ├── document_type.py
│   ├── sequence.py
│   └── number_log.py
├── services/              # Lógica de negócio
│   ├── auth_service.py
│   ├── document_type_service.py
│   ├── history_service.py
│   ├── number_service.py
│   └── user_service.py
├── scripts/               # Scripts utilitários
│   └── seed_data.py      # Popular dados iniciais
├── tests/                 # Testes
│   ├── unit/
│   └── integration/
├── function_app.py        # Entry point da Function App
├── host.json              # Configuração do host
├── local.settings.json    # Configurações locais (gitignored)
└── requirements.txt       # Dependências Python
```

## 🔌 Endpoints

### Autenticação

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| POST | `/api/auth/login` | Login com email/senha | Nenhuma |
| POST | `/api/auth/logout` | Logout (limpa cookie) | Nenhuma |
| GET | `/api/auth/me` | Dados do usuário logado | JWT |
| POST | `/api/auth/change-password` | Alterar senha | JWT |

### Números

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| POST | `/api/numbers/generate` | Gerar próximo número | JWT |

### Tipos de Documento

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| GET | `/api/document-types` | Listar tipos | JWT |
| POST | `/api/document-types` | Criar tipo | Admin |
| GET | `/api/document-types/{id}` | Obter tipo | Admin |
| PUT | `/api/document-types/{id}` | Atualizar tipo | Admin |
| DELETE | `/api/document-types/{id}` | Desativar tipo | Admin |

### Histórico

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| GET | `/api/history` | Listar histórico | JWT |
| GET | `/api/history/export` | Exportar CSV | JWT |

### Usuários

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| GET | `/api/users` | Listar usuários | Admin |
| POST | `/api/users` | Criar usuário | Admin |
| GET | `/api/users/{id}` | Obter usuário | Admin |
| PUT | `/api/users/{id}` | Atualizar usuário | Admin |
| DELETE | `/api/users/{id}` | Desativar usuário | Admin |
| POST | `/api/users/{id}/reset-password` | Resetar senha | Admin |

### Health Check

| Método | Rota | Descrição | Autenticação |
|--------|------|-----------|--------------|
| GET | `/api/health` | Status da API | Nenhuma |

## 🚀 Desenvolvimento Local

### Pré-requisitos

- Python 3.11+
- Azure Functions Core Tools v4
- Azurite (emulador de Azure Storage)

### Setup

```bash
# Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Copiar configurações locais
cp local.settings.json.example local.settings.json
```

### Iniciar Azurite

```bash
npm install -g azurite
azurite --silent &
```

### Popular dados iniciais

```bash
python scripts/seed_data.py
```

### Iniciar servidor

```bash
func start
```

A API estará disponível em `http://localhost:7071/api`.

## 🔐 Autenticação

A API usa JWT (JSON Web Tokens) armazenados em cookies HttpOnly:

1. Cliente faz POST em `/api/auth/login` com email/senha
2. Servidor valida credenciais e retorna JWT em cookie `auth_token`
3. Browser envia cookie automaticamente nas requisições seguintes
4. Servidor valida JWT via decorator `@require_auth` ou `@require_admin`

### Configuração JWT

| Variável | Descrição | Default |
|----------|-----------|---------|
| `JWT_SECRET` | Chave de assinatura | Deve ser alterada em produção |
| `JWT_EXPIRATION_HOURS` | Tempo de expiração | 8 horas |
| `JWT_ALGORITHM` | Algoritmo de assinatura | HS256 |

## 🗄️ Banco de Dados

### Tabelas Azure

| Tabela | PartitionKey | RowKey | Descrição |
|--------|-------------|--------|-----------|
| Users | `USER` | `{uuid}` | Usuários do sistema |
| DocumentTypes | `DOCTYPE` | `{uuid}` | Tipos de documento |
| Sequences | `{code}_{year}` | `SEQUENCE` | Sequências numéricas |
| NumberLogs | `{code}_{year}` | `{inverse_ts}_{uuid}` | Log de gerações |

### Concorrência

A geração de números usa **ETag-based optimistic locking**:

1. Ler sequência atual com ETag
2. Incrementar número
3. Atualizar com condição `If-Match: {etag}`
4. Se conflito (412), retry até MAX_RETRIES

## 🧪 Testes

```bash
# Todos os testes
python -m pytest tests/ -v

# Com cobertura
python -m pytest tests/ -v --cov=backend --cov-report=html

# Apenas unit tests
python -m pytest tests/unit/ -v

# Apenas integration tests
python -m pytest tests/integration/ -v
```

## 📝 Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `AZURE_TABLES_CONNECTION_STRING` | Connection string Azure Tables | `UseDevelopmentStorage=true` |
| `JWT_SECRET` | Chave secreta JWT | Deve ter 32+ caracteres |
| `JWT_EXPIRATION_HOURS` | Expiração do token | `8` |
| `CORS_ORIGINS` | Origens permitidas | `http://localhost:5173` |
| `ENVIRONMENT` | Ambiente | `development` |
| `TIMEZONE` | Timezone | `America/Sao_Paulo` |
| `PASSWORD_MIN_LENGTH` | Tamanho mínimo senha | `8` |
| `BCRYPT_COST_FACTOR` | Custo bcrypt | `12` |

## 🔍 Troubleshooting

### Erro de conexão com Azure Tables

```
AzureException: Connection refused
```

Verifique se o Azurite está rodando:
```bash
azurite --silent &
```

### Erro de autenticação

```
401 Unauthorized
```

Verifique:
1. Cookie `auth_token` está sendo enviado
2. Token não expirou
3. `JWT_SECRET` é o mesmo usado para criar o token

### Erro de concorrência

```
500 - Não foi possível gerar número após N tentativas
```

Isso indica alta concorrência. Aumente `MAX_RETRIES` se necessário, mas o valor default (5) deve ser suficiente para uso normal.
