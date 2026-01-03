# Backend API - Controle PGM

API REST em Python para o sistema de controle de numeração de documentos.

## 🛠️ Stack

- **Runtime**: Python 3.11
- **Framework**: Azure Functions v4 (Blueprint pattern)
- **Validação**: Pydantic v2
- **Sanitização**: Bleach (HTML Sanitization)
- **Autenticação**: PyJWT + bcrypt
- **Banco de Dados**: Azure Tables (azure-data-tables)
- **Cache**: Redis (Upstash/Azure Redis) para Rate Limiting

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
| `REDIS_CONNECTION_STRING` | Connection string Redis (rate limiting) | `` (usa memória) |
| `JWT_SECRET` | Chave secreta JWT | Deve ter 32+ caracteres |
| `JWT_EXPIRATION_HOURS` | Expiração do token | `8` |
| `CORS_ORIGINS` | Origens permitidas | `http://localhost:5173` |
| `ENVIRONMENT` | Ambiente | `development` |
| `TIMEZONE` | Timezone | `America/Sao_Paulo` |
| `PASSWORD_MIN_LENGTH` | Tamanho mínimo senha | `8` |
| `BCRYPT_COST_FACTOR` | Custo bcrypt | `12` |

## 🔒 Segurança

### Medidas Implementadas

| Proteção | Descrição |
|----------|-----------|
| **Sanitização OData** | Todas as queries ao Azure Tables são sanitizadas para prevenir injeção |
| **Sanitização de Input** | Remoção de tags HTML (XSS) via Bleach em todos os campos de texto |
| **Rate Limiting** | Limite de requisições por IP/usuário (Redis em produção) |
| **Timing Attack Prevention** | Delay aleatório no login para evitar enumeração de usuários |
| **UUID Validation** | Validação de formato UUID em todos os parâmetros de rota |
| **Error Hiding** | Detalhes de erro interno são ocultos em produção |
| **Auditoria** | Log de todas as ações administrativas |
| **HttpOnly Cookies** | Tokens JWT armazenados em cookies não acessíveis por JS |
| **Security Headers** | CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc. |

### Auditoria

Todas as ações administrativas são registradas na tabela `AuditLogs`:

- Login/logout (sucesso e falha)
- Criação/atualização/desativação de usuários
- Reset de senha
- Criação/atualização de tipos de documento
- Geração e correção de números

### Configuração para Produção

#### 1. JWT Secret

**CRÍTICO**: Configure um JWT_SECRET forte (mínimo 64 caracteres aleatórios).

```bash
# Gerar secret seguro
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Recomendado: Armazene no **Azure Key Vault** e referencie via Application Settings.

#### 2. Rate Limiting com Redis

Para ambientes de produção com múltiplas instâncias, configure o Redis:

```bash
REDIS_CONNECTION_STRING=rediss://:password@your-redis.redis.cache.windows.net:6380/0
```

Isso garante que o rate limiting seja persistente entre cold starts e compartilhado entre instâncias.

#### 3. Headers de Segurança

Os seguintes headers são injetados automaticamente via Middleware (`core/middleware.py`) em todas as respostas:

- `Content-Security-Policy`: Restringe fontes de scripts, estilos e imagens
- `Strict-Transport-Security`: Força HTTPS (HSTS)
- `X-Content-Type-Options: nosniff`: Previne MIME sniffing
- `X-Frame-Options: DENY`: Previne Clickjacking
- `X-XSS-Protection: 1; mode=block`: Proteção XSS legada
- `Referrer-Policy: strict-origin-when-cross-origin`: Privacidade de referrer
- `Server`: Removido (ou vazio) para ocultar tecnologia do servidor

#### 4. CORS

Configure `CORS_ORIGINS` apenas com as origens necessárias:

```bash
CORS_ORIGINS=https://seu-dominio.com,https://www.seu-dominio.com
```

### Checklist de Segurança para Deploy

- [ ] `JWT_SECRET` configurado com valor forte (64+ caracteres)
- [ ] `JWT_SECRET` armazenado no Azure Key Vault
- [ ] `ENVIRONMENT` configurado como `production`
- [ ] `CORS_ORIGINS` restrito aos domínios permitidos
- [ ] `REDIS_CONNECTION_STRING` configurado (se múltiplas instâncias)
- [ ] Azure Tables com autenticação via Managed Identity
- [ ] HTTPS forçado via Azure App Service
- [ ] Logs de auditoria sendo coletados

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
