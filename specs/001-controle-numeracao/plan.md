# Implementation Plan: Controle de Numeração de Documentos

**Branch**: `001-controle-numeracao` | **Date**: 2025-12-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification + Stack requirements: Python Function App + Azure Tables + Static Website + Shadcn UI

## Summary

Sistema web para controle de numeração sequencial de documentos da Procuradoria-Geral do Município de Itajaí. Backend Python serverless com Azure Functions (Flex Consumption), banco de dados NoSQL com Azure Tables, e frontend React SPA hospedado em Storage Account Static Website. Arquitetura cost-efficient projetada para <R$20/mês.

## Technical Context

**Backend Language**: Python 3.11  
**Backend Framework**: Azure Functions v4 (Flex Consumption)  
**Frontend Framework**: React 18 + Vite + TypeScript  
**UI Components**: Shadcn/UI (Radix + Tailwind)  
**Database**: Azure Tables (Storage Account)  
**Authentication**: JWT em Cookie HttpOnly  
**Testing**: pytest (backend), Vitest + Testing Library (frontend)  
**IaC**: Bicep  
**Target Platform**: Azure (Brazil South)  
**Resource Group**: controle-pgm  
**Cost Target**: < R$ 50/mês  
**Performance Goals**: < 500ms p95 para geração de número  
**Scale/Scope**: ~20 usuários, ~1000 números/mês

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Qualidade de Código | ✅ | Python type hints + TypeScript strict, Ruff + ESLint |
| II. Padrões de Teste | ✅ | pytest unitário + integração, Vitest + Playwright E2E, target 80% |
| III. Experiência do Usuário | ✅ | Shadcn/UI acessível, loading states, mobile-first |
| IV. Azure Cost-Efficient | ✅ | Storage Account (~R$5) + Function Flex (~R$5) + KeyVault (~R$1) ≈ R$15 |

**Post-Design Re-Check**: ✅ Arquitetura validada, custo estimado ~R$15/mês (30% do target)

## Architecture Decision

### Por que Python Azure Functions?

1. **Especificação do usuário**: Requisito explícito de backend Python
2. **Flex Consumption**: Cold start ~0, scale-to-zero, custo por execução
3. **SDK nativo**: `azure-data-tables` oficial e bem mantido
4. **Simplicidade**: Funções HTTP simples, sem framework pesado

### Por que Azure Tables em vez de SQL/Cosmos?

1. **Custo**: ~R$1/mês para transações vs ~R$30-40/mês SQL Serverless
2. **Simplicidade**: Key-value é suficiente para o modelo de dados
3. **Concorrência**: ETag-based optimistic locking funciona para o volume
4. **Integração**: Mesmo Storage Account do static website

### Por que Static Website em Storage Account?

1. **Custo**: ~R$5/mês (incluindo storage do frontend e tables)
2. **Simplicidade**: Deploy direto, sem configuração de servidor
3. **CDN opcional**: Pode adicionar depois se necessário
4. **HTTPS**: Suporte nativo com certificado gerenciado

### Alternativas Consideradas

| Opção | Prós | Contras | Decisão |
|-------|------|---------|---------|
| Azure SQL Serverless | ACID nativo | Custo ~R$35/mês, cold start | ❌ |
| Cosmos DB | Serverless, global | Custo por RU, complexidade | ❌ |
| Azure Static Web Apps | CI/CD integrado | Menos controle, funções limitadas | ❌ |
| Next.js | Full-stack TypeScript | Requisito era Python backend | ❌ |

## Project Structure

### Documentation (this feature)

```text
specs/001-controle-numeracao/
├── spec.md              # Especificação funcional
├── plan.md              # Este arquivo
├── research.md          # Decisões técnicas e pesquisa
├── data-model.md        # Modelo Azure Tables
├── quickstart.md        # Setup local
├── contracts/
│   └── openapi.yaml     # API specification
├── checklists/
│   └── requirements.md  # Checklist de requisitos
└── tasks.md             # Lista de tarefas (gerado na fase 2)
```

### Source Code (repository root)

```text
backend/                          # Azure Functions Python
├── function_app.py               # Entry point Azure Functions v4
├── requirements.txt              # Dependências Python
├── host.json                     # Configuração do host
├── local.settings.json.template  # Template para settings locais
├── functions/
│   ├── __init__.py
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── login.py              # POST /api/auth/login
│   │   ├── logout.py             # POST /api/auth/logout
│   │   ├── me.py                 # GET /api/auth/me
│   │   └── change_password.py    # POST /api/auth/change-password
│   ├── numbers/
│   │   ├── __init__.py
│   │   └── generate.py           # POST /api/numbers
│   ├── history/
│   │   ├── __init__.py
│   │   ├── list.py               # GET /api/history
│   │   └── export.py             # GET /api/history/export
│   ├── document_types/
│   │   ├── __init__.py
│   │   ├── list.py               # GET /api/document-types
│   │   ├── create.py             # POST /api/document-types
│   │   ├── get.py                # GET /api/document-types/{id}
│   │   ├── update.py             # PUT /api/document-types/{id}
│   │   └── delete.py             # DELETE /api/document-types/{id}
│   └── users/
│       ├── __init__.py
│       ├── list.py               # GET /api/users
│       ├── create.py             # POST /api/users
│       ├── get.py                # GET /api/users/{id}
│       ├── update.py             # PUT /api/users/{id}
│       ├── delete.py             # DELETE /api/users/{id}
│       └── reset_password.py     # POST /api/users/{id}/reset-password
├── core/
│   ├── __init__.py
│   ├── auth.py                   # JWT utilities
│   ├── middleware.py             # Auth middleware decorator
│   ├── tables.py                 # Azure Tables client factory
│   ├── config.py                 # Environment configuration
│   └── exceptions.py             # Custom exceptions
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   ├── document_type_service.py
│   ├── number_service.py         # Lógica de geração atômica
│   └── history_service.py
├── models/
│   ├── __init__.py
│   ├── user.py                   # Pydantic models
│   ├── document_type.py
│   ├── number_log.py
│   └── sequence.py
└── tests/
    ├── __init__.py
    ├── conftest.py               # Fixtures pytest
    ├── unit/
    │   ├── test_number_service.py
    │   └── test_auth.py
    └── integration/
        ├── test_numbers_api.py
        └── test_auth_api.py

frontend/                         # React SPA
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── components.json               # Shadcn config
├── index.html
├── public/
│   └── favicon.ico
├── src/
│   ├── main.tsx                  # Entry point
│   ├── App.tsx                   # Router setup
│   ├── index.css                 # Tailwind imports
│   ├── lib/
│   │   ├── api.ts                # API client
│   │   ├── utils.ts              # cn() e helpers
│   │   └── auth-context.tsx      # React context para auth
│   ├── components/
│   │   ├── ui/                   # Shadcn components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── form.tsx
│   │   │   ├── input.tsx
│   │   │   ├── table.tsx
│   │   │   ├── select.tsx
│   │   │   ├── toast.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── header.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── page-container.tsx
│   │   └── features/
│   │       ├── login-form.tsx
│   │       ├── number-generator.tsx
│   │       ├── history-table.tsx
│   │       ├── document-types-list.tsx
│   │       └── users-list.tsx
│   ├── pages/
│   │   ├── login.tsx
│   │   ├── dashboard.tsx
│   │   ├── history.tsx
│   │   ├── settings/
│   │   │   ├── document-types.tsx
│   │   │   └── users.tsx
│   │   └── change-password.tsx
│   └── types/
│       └── index.ts              # Types da API
└── tests/
    ├── setup.ts
    ├── login.test.tsx
    └── number-generator.test.tsx

infra/                            # Infrastructure as Code
├── main.bicep                    # Módulo principal
├── modules/
│   ├── storage.bicep             # Storage Account + Tables + Static Website
│   ├── function-app.bicep        # Function App Flex Consumption
│   ├── keyvault.bicep            # Key Vault para secrets
│   └── monitoring.bicep          # Application Insights
├── parameters/
│   ├── dev.bicepparam
│   └── prod.bicepparam
└── README.md

.github/
└── workflows/
    ├── backend.yml               # CI/CD backend
    ├── frontend.yml              # CI/CD frontend
    └── infra.yml                 # Deploy infra

scripts/
├── seed.py                       # Seed inicial (tipos + admin)
└── local-setup.sh                # Setup ambiente local
```

**Structure Decision**: Separação clara entre backend (Python/Azure Functions) e frontend (React SPA). Monorepo com dois projetos independentes para facilitar deploys separados.

## Technology Stack

| Camada | Tecnologia | Versão | Justificativa |
|--------|------------|--------|---------------|
| Backend Runtime | Python | 3.11 | LTS, performance, type hints |
| Backend Framework | Azure Functions v4 | 4.x | Flex Consumption, HTTP triggers |
| Database | Azure Tables | - | Cost-efficient NoSQL |
| ORM/SDK | azure-data-tables | 12.5+ | SDK oficial Microsoft |
| Auth | PyJWT | 2.8+ | JWT padrão |
| Password Hash | bcrypt | 4.1+ | Seguro, cost 12 |
| Validation | Pydantic | 2.5+ | Type-safe request/response |
| Frontend Framework | React | 18.x | Ecosystem, hooks |
| Build Tool | Vite | 5.x | Fast dev, optimized build |
| Language | TypeScript | 5.x | Type safety |
| Styling | Tailwind CSS | 3.x | Utility-first |
| Components | Shadcn/UI | latest | Accessible, customizable |
| HTTP Client | fetch | native | Simples, sem dependência |
| Testing (BE) | pytest | 8.x | Python standard |
| Testing (FE) | Vitest | 1.x | Vite-native |
| E2E | Playwright | 1.x | Cross-browser |
| IaC | Bicep | latest | Azure native |
| CI/CD | GitHub Actions | - | Integração nativa |

## Azure Resources

| Recurso | Nome | SKU/Config | Custo Est./mês |
|---------|------|------------|----------------|
| Resource Group | controle-pgm | - | R$ 0 |
| Storage Account | stcontrolepgm | Standard_LRS | ~R$ 5 |
| ↳ Static Website | $web container | - | (incluído) |
| ↳ Table Storage | Users, DocumentTypes, Sequences, NumberLogs | - | (incluído) |
| Function App | func-controlepgm | Flex Consumption, Python 3.11 | ~R$ 5 |
| Key Vault | kv-controlepgm | Standard | ~R$ 1 |
| Application Insights | appi-controlepgm | Basic (5GB free) | R$ 0 |
| **Total Estimado** | | | **~R$ 11-15** |

## Security Considerations

1. **Autenticação**: JWT com expiração 8h, armazenado em Cookie HttpOnly + Secure + SameSite=Strict
2. **Senhas**: bcrypt com cost factor 12, política mínimo 8 chars + 1 letra + 1 número
3. **Autorização**: Decorator `@require_auth(role=["admin"])` nas funções
4. **Secrets**: Connection strings e JWT secret no Key Vault
5. **CORS**: Restrito ao domínio do static website
6. **HTTPS**: Obrigatório via Azure (Storage Account e Function App)
7. **Rate Limiting**: 100 req/min por IP na função de geração de número
8. **SQL Injection**: N/A (NoSQL sem queries SQL)
9. **XSS**: React escapa por default, CSP headers configurados

## Performance Considerations

1. **Cold Start**: Flex Consumption tem cold start ~50-100ms vs ~5s do Consumption tradicional
2. **Concurrency**: ETag-based optimistic locking com retry automático (max 5 tentativas)
3. **Database**: Azure Tables tem latência ~10ms para operações pontuais
4. **Frontend**: Vite bundle otimizado, lazy loading de rotas
5. **Caching**: Cache de document types no frontend (TTL 5min)

## Risks & Mitigations

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Concorrência na sequência | Baixa | Alto | ETag retry, max 5 tentativas, log de falhas |
| Cold start em pico | Baixa | Médio | Flex Consumption + always ready (se necessário) |
| Custo acima do esperado | Baixa | Médio | Budget alerts em R$ 30 e R$ 50 |
| Migração de dados futura | Média | Baixo | Schema versionado, compatibilidade backward |

## Complexity Tracking

| Área | Complexidade | Justificativa |
|------|--------------|---------------|
| Geração de número | Média | ETag concurrency requer retry logic |
| Autenticação JWT | Baixa | Padrão bem estabelecido |
| Azure Tables | Baixa | SDK oficial, operações simples |
| Frontend React | Baixa | Componentes Shadcn prontos |
| Deploy Bicep | Média | Primeira vez com IaC |

Nenhuma violação de constituição identificada.

## Dependencies (External)

| Dependência | Motivo | Fallback |
|-------------|--------|----------|
| Azure Brasil South | Requisito compliance | N/A (requisito) |
| PyPI | Dependências Python | Cache local |
| npm Registry | Dependências JS | Cache local |
| Shadcn Registry | Componentes UI | Fork local se necessário |

## Phase Summary

### Phase 0: Research ✅
- [research.md](research.md) - Decisões técnicas documentadas

### Phase 1: Design ✅
- [data-model.md](data-model.md) - Schema Azure Tables
- [contracts/openapi.yaml](contracts/openapi.yaml) - API specification
- [quickstart.md](quickstart.md) - Setup local

### Phase 2: Tasks (Próximo)
- Gerar tasks.md com breakdown de implementação
- Estimar story points
- Definir ordem de execução

## Related Documents

- [Constitution](../../.specify/memory/constitution.md) - Princípios do projeto
- [Spec](spec.md) - Especificação funcional
- [Research](research.md) - Decisões técnicas
- [Data Model](data-model.md) - Schema do banco
- [API Contract](contracts/openapi.yaml) - OpenAPI 3.0
- [Quickstart](quickstart.md) - Setup local
