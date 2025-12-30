# Tasks: Controle de Numeração de Documentos

**Input**: Design documents from `/specs/001-controle-numeracao/`  
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Tests**: Incluídos conforme boas práticas do projeto (pytest, Vitest, Playwright)

**Organization**: Tasks grouped by user story for independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1-US6) this task belongs to
- Exact file paths included in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project structure and initialize dependencies

- [X] T001 Create root folder structure: `backend/`, `frontend/`, `infra/`, `scripts/`
- [X] T002 [P] Initialize backend Python project with `backend/requirements.txt` (azure-functions, azure-data-tables, pyjwt, bcrypt, pydantic, python-dotenv)
- [X] T003 [P] Initialize frontend React project with Vite in `frontend/` (npm create vite@latest)
- [X] T004 [P] Create `backend/host.json` with Azure Functions v4 configuration
- [X] T005 [P] Create `backend/local.settings.json.template` with required environment variables
- [X] T006 [P] Create `frontend/components.json` for Shadcn/UI configuration
- [X] T007 Install Shadcn/UI base dependencies and configure Tailwind in `frontend/`
- [X] T008 [P] Create `infra/main.bicep` skeleton with parameter structure
- [X] T009 [P] Configure Ruff linter in `backend/pyproject.toml`
- [X] T010 [P] Configure ESLint + Prettier in `frontend/`

**Checkpoint**: Project skeleton ready, dependencies installed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Core

- [X] T011 Implement environment configuration in `backend/core/config.py` (Azure Tables connection, JWT secret, CORS origins)
- [X] T012 [P] Implement Azure Tables client factory in `backend/core/tables.py` with connection pooling
- [X] T013 [P] Implement custom exceptions in `backend/core/exceptions.py` (NotFoundError, UnauthorizedError, ConflictError)
- [X] T014 [P] Implement JWT utilities in `backend/core/auth.py` (create_token, verify_token, hash_password, verify_password)
- [X] T015 Implement auth middleware decorator in `backend/core/middleware.py` (@require_auth, @require_admin)
- [X] T016 Create Azure Functions entry point in `backend/function_app.py` with blueprint registration

### Backend Models (Pydantic)

- [X] T017 [P] Create User Pydantic models in `backend/models/user.py` (UserEntity, UserCreate, UserResponse, LoginRequest)
- [X] T018 [P] Create DocumentType Pydantic models in `backend/models/document_type.py` (DocumentTypeEntity, DocumentTypeCreate, DocumentTypeResponse)
- [X] T019 [P] Create Sequence Pydantic models in `backend/models/sequence.py` (SequenceEntity)
- [X] T020 [P] Create NumberLog Pydantic models in `backend/models/number_log.py` (NumberLogEntity, NumberLogResponse, HistoryFilter)

### Frontend Core

- [X] T021 Configure API client with cookie handling in `frontend/src/lib/api.ts` (including 401 interceptor for session expiry redirect)
- [X] T022 Create utility functions in `frontend/src/lib/utils.ts` (cn, formatNumber, formatDate)
- [X] T023 Install Shadcn UI components: button, card, dialog, form, input, table, select, toast, label, dropdown-menu
- [X] T024 Create auth context and provider in `frontend/src/lib/auth-context.tsx`
- [X] T025 Create TypeScript types from OpenAPI in `frontend/src/types/index.ts`

### Frontend Layout

- [X] T026 [P] Create Header component in `frontend/src/components/layout/header.tsx`
- [X] T027 [P] Create Sidebar component in `frontend/src/components/layout/sidebar.tsx`
- [X] T028 Create PageContainer layout in `frontend/src/components/layout/page-container.tsx`
- [X] T029 Setup React Router in `frontend/src/App.tsx` with protected routes

### Infrastructure (IaC)

- [X] T030 [P] Create Storage Account Bicep module in `infra/modules/storage.bicep` (Tables + Static Website + Backup Policy)
- [X] T031 [P] Create Function App Bicep module in `infra/modules/function-app.bicep` (Flex Consumption, Python 3.11)
- [X] T032 [P] Create Key Vault Bicep module in `infra/modules/keyvault.bicep`
- [X] T033 [P] Create Application Insights Bicep module in `infra/modules/monitoring.bicep`
- [X] T034 Complete `infra/main.bicep` with module composition and outputs
- [X] T035 [P] Create `infra/parameters/dev.bicepparam` with development values
- [X] T036 [P] Create `infra/parameters/prod.bicepparam` with production values

### Backend Tests Setup

- [X] T037 Create pytest configuration in `backend/tests/conftest.py` with Azurite fixtures
- [X] T038 [P] Create test utilities in `backend/tests/__init__.py`

### Frontend Tests Setup

- [X] T039 Create Vitest configuration in `frontend/vitest.config.ts`
- [X] T040 [P] Create test setup in `frontend/tests/setup.ts`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Login no Sistema (Priority: P1) 🎯 MVP

**Goal**: Servidor público acessa o sistema com e-mail e senha para obter acesso às funcionalidades

**Independent Test**: Acessar página de login, inserir credenciais válidas, verificar redirecionamento para dashboard

### Tests for US1

- [X] T041 [P] [US1] Unit test for auth utilities in `backend/tests/unit/test_auth.py` (JWT, password hashing)
- [ ] T042 [P] [US1] Integration test for login API in `backend/tests/integration/test_auth_api.py`
- [ ] T043 [P] [US1] Component test for LoginForm in `frontend/tests/login.test.tsx`

### Backend Implementation for US1

- [X] T044 [US1] Implement UserService in `backend/services/user_service.py` (get_by_email, verify_credentials, get_by_id)
- [X] T045 [US1] Implement login endpoint in `backend/functions/auth/login.py` (POST /api/auth/login)
- [X] T046 [P] [US1] Implement logout endpoint in `backend/functions/auth/logout.py` (POST /api/auth/logout)
- [X] T047 [P] [US1] Implement me endpoint in `backend/functions/auth/me.py` (GET /api/auth/me)
- [X] T048 [US1] Implement change-password endpoint in `backend/functions/auth/change_password.py` (POST /api/auth/change-password)
- [X] T049 [US1] Register auth blueprint in `backend/function_app.py`

### Frontend Implementation for US1

- [X] T050 [US1] Create LoginForm component in `frontend/src/components/features/login-form.tsx` (implementado em LoginPage.tsx)
- [X] T051 [US1] Create Login page in `frontend/src/pages/login.tsx` (implementado como LoginPage.tsx)
- [X] T052 [US1] Create Dashboard page skeleton in `frontend/src/pages/dashboard.tsx` (implementado como HomePage.tsx)
- [X] T053 [US1] Create ChangePassword page in `frontend/src/pages/change-password.tsx` (implementado como ChangePasswordDialog)
- [X] T054 [US1] Implement protected route wrapper with auth redirect (ProtectedRoute.tsx)
- [X] T055 [US1] Implement MustChangePassword redirect in `frontend/src/lib/auth-context.tsx` (force password change on first login)

### Seed Data for US1

- [X] T057 [US1] Create seed script in `scripts/seed.py` (admin user + initial document types)

**Checkpoint**: Login funcional - usuários podem autenticar e acessar dashboard ✅

---

## Phase 4: User Story 2 - Solicitar Número de Documento (Priority: P1) 🎯 MVP

**Goal**: Servidor solicita próximo número sequencial para um tipo de documento específico

**Independent Test**: Usuário logado seleciona tipo "Ofício", clica em "Solicitar Número", recebe número formatado

### Tests for US2

- [ ] T058 [P] [US2] Unit test for number generation in `backend/tests/unit/test_number_service.py` (atomicity, ETag retry)
- [ ] T059 [P] [US2] Integration test for numbers API in `backend/tests/integration/test_numbers_api.py`
- [ ] T060 [P] [US2] Component test for NumberGenerator in `frontend/tests/number-generator.test.tsx`

### Backend Implementation for US2

- [X] T061 [US2] Implement DocumentTypeService in `backend/services/document_type_service.py` (list_active, get_by_id)
- [X] T062 [US2] Implement NumberService in `backend/services/number_service.py` (generate_number with ETag concurrency)
- [X] T063 [US2] Implement generate number endpoint in `backend/functions/numbers/generate.py` (POST /api/numbers)
- [X] T064 [US2] Implement list document types endpoint in `backend/functions/document_types/list.py` (GET /api/document-types)
- [X] T065 [US2] Register numbers and document-types blueprints in `backend/function_app.py`

### Frontend Implementation for US2

- [X] T066 [US2] Create NumberGenerator component in `frontend/src/components/features/number-generator.tsx` (select, confirm modal, success modal, copy)
- [X] T067 [US2] Complete Dashboard page in `frontend/src/pages/dashboard.tsx` with NumberGenerator integration
- [X] T068 [US2] Add toast notifications for success/error states

**Checkpoint**: Geração de números funcional - MVP core completo (Login + Geração)

---

## Phase 5: User Story 3 - Visualizar Histórico de Números (Priority: P2)

**Goal**: Servidor visualiza números já emitidos com filtros por tipo, data e usuário

**Independent Test**: Usuário acessa tela de histórico, aplica filtro por tipo "Ofício", visualiza lista

### Tests for US3

- [ ] T069 [P] [US3] Integration test for history API in `backend/tests/integration/test_history_api.py`
- [ ] T070 [P] [US3] Component test for HistoryTable in `frontend/tests/history.test.tsx`

### Backend Implementation for US3

- [X] T071 [US3] Implement HistoryService in `backend/services/history_service.py` (list_paginated, export_csv)
- [X] T072 [US3] Implement list history endpoint in `backend/functions/history/list.py` (GET /api/history)
- [X] T073 [US3] Implement export history endpoint in `backend/functions/history/export.py` (GET /api/history/export)
- [X] T074 [US3] Register history blueprint in `backend/function_app.py`

### Frontend Implementation for US3

- [X] T075 [US3] Create HistoryTable component in `frontend/src/components/features/history-table.tsx` (filtros, paginação)
- [X] T076 [US3] Create History page in `frontend/src/pages/history.tsx`
- [X] T077 [US3] Add CSV export functionality with download handling
- [X] T078 [US3] Add history link to sidebar navigation

**Checkpoint**: Histórico funcional - usuários podem auditar números gerados ✅

---

## Phase 6: User Story 4 - Gerenciar Tipos de Documento (Priority: P2)

**Goal**: Administrador cadastra, edita ou desativa tipos de documentos

**Independent Test**: Admin acessa configurações, adiciona tipo "Parecer", verifica disponibilidade na solicitação

### Tests for US4

- [ ] T079 [P] [US4] Integration test for document-types CRUD in `backend/tests/integration/test_document_types_api.py`

### Backend Implementation for US4

- [X] T080 [US4] Extend DocumentTypeService in `backend/services/document_type_service.py` (create, update, delete/deactivate)
- [X] T081 [US4] Implement create document type endpoint in `backend/functions/document_types/create.py` (POST /api/document-types)
- [X] T082 [P] [US4] Implement get document type endpoint in `backend/functions/document_types/get.py` (GET /api/document-types/{id})
- [X] T083 [P] [US4] Implement update document type endpoint in `backend/functions/document_types/update.py` (PUT /api/document-types/{id})
- [X] T084 [P] [US4] Implement delete document type endpoint in `backend/functions/document_types/delete.py` (DELETE /api/document-types/{id})

### Frontend Implementation for US4

- [X] T085 [US4] Create DocumentTypesList component in `frontend/src/components/features/document-types-list.tsx` (table, add/edit/delete)
- [X] T086 [US4] Create DocumentTypes settings page in `frontend/src/pages/settings/document-types.tsx`
- [X] T087 [US4] Add settings link to sidebar navigation (admin only)

**Checkpoint**: CRUD de tipos funcional - admin pode gerenciar tipos de documentos ✅

---

## Phase 7: User Story 5 - Gerenciar Usuários (Priority: P2)

**Goal**: Administrador cadastra e gerencia servidores com acesso ao sistema

**Independent Test**: Admin cadastra novo usuário e verifica que consegue fazer login

### Tests for US5

- [ ] T088 [P] [US5] Integration test for users CRUD in `backend/tests/integration/test_users_api.py`

### Backend Implementation for US5

- [X] T089 [US5] Extend UserService in `backend/services/user_service.py` (create, update, list, deactivate, reset_password)
- [X] T090 [US5] Implement list users endpoint in `backend/functions/users/list.py` (GET /api/users)
- [X] T091 [US5] Implement create user endpoint in `backend/functions/users/create.py` (POST /api/users)
- [X] T092 [P] [US5] Implement get user endpoint in `backend/functions/users/get.py` (GET /api/users/{id})
- [X] T093 [P] [US5] Implement update user endpoint in `backend/functions/users/update.py` (PUT /api/users/{id})
- [X] T094 [P] [US5] Implement delete user endpoint in `backend/functions/users/delete.py` (DELETE /api/users/{id})
- [X] T095 [US5] Implement reset password endpoint in `backend/functions/users/reset_password.py` (POST /api/users/{id}/reset-password)

### Frontend Implementation for US5

- [X] T096 [US5] Create UsersList component in `frontend/src/components/features/users-list.tsx` (table, add/edit/deactivate/reset)
- [X] T097 [US5] Create Users settings page in `frontend/src/pages/settings/users.tsx`

**Checkpoint**: CRUD de usuários funcional - admin pode gerenciar acesso ✅

---

## Phase 8: User Story 6 - Reinício Anual Automático (Priority: P3)

**Goal**: Sistema reinicia sequências automaticamente no início de cada ano

**Independent Test**: Simular data 01/01/2026 e verificar que próximo número é 1/2026

### Tests for US6

- [ ] T098 [P] [US6] Unit test for year boundary handling in `backend/tests/unit/test_number_service.py`

### Backend Implementation for US6

- [X] T099 [US6] Add timezone handling (America/Sao_Paulo) in `backend/core/config.py`
- [X] T100 [US6] Update NumberService year detection logic in `backend/services/number_service.py`
- [X] T101 [US6] Add integration test for year rollover scenario

**Checkpoint**: Reinício anual funcional - sistema pronto para virada de ano ✅

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### CI/CD

- [X] T102 [P] Create backend CI workflow in `.github/workflows/backend.yml` (lint, test, deploy)
- [X] T103 [P] Create frontend CI workflow in `.github/workflows/frontend.yml` (lint, test, build, deploy)
- [X] T104 [P] Create infra deployment workflow in `.github/workflows/infra.yml` (Bicep deploy)

### Documentation

- [X] T105 [P] Update `README.md` at repository root with project overview and setup instructions
- [X] T106 [P] Create `infra/README.md` with infrastructure documentation
- [X] T107 [P] Create `backend/README.md` with API documentation
- [X] T108 [P] Create `frontend/README.md` with frontend documentation

### Security Hardening

- [X] T109 Configure CORS settings in Function App for production
- [X] T110 Add rate limiting middleware for number generation endpoint
- [X] T111 Configure CSP headers in static website

### Final Validation

- [X] T112 Run full test suite (backend + frontend)
- [X] T113 Execute quickstart.md validation steps
- [ ] T114 Deploy to staging environment and smoke test
- [ ] T115 Security review and penetration testing checklist

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKS all user stories
    ↓
    ├── Phase 3 (US1: Login) ← P1, MVP
    │       ↓
    │   Phase 4 (US2: Números) ← P1, MVP (depends on US1 for auth)
    │
    ├── Phase 5 (US3: Histórico) ← P2 (can start after US2)
    ├── Phase 6 (US4: Tipos) ← P2 (can start after US2)
    └── Phase 7 (US5: Usuários) ← P2 (can start after US1)
        
Phase 8 (US6: Reinício) ← P3 (can start after US2)
    ↓
Phase 9 (Polish) ← After desired stories complete
```

### User Story Dependencies

| Story | Depends On | Can Start After |
|-------|------------|-----------------|
| US1 (Login) | Phase 2 | Phase 2 complete |
| US2 (Números) | US1 | US1 complete |
| US3 (Histórico) | US2 | US2 complete |
| US4 (Tipos) | US2 | US2 complete |
| US5 (Usuários) | US1 | US1 complete |
| US6 (Reinício) | US2 | US2 complete |

### Parallel Opportunities per Phase

**Phase 1 (Setup)**:
```
T002, T003, T004, T005, T006, T008, T009, T010 → all [P]
```

**Phase 2 (Foundational)**:
```
T012, T013, T014 → parallel (core utilities)
T017, T018, T019, T020 → parallel (models)
T026, T027 → parallel (layout)
T030, T031, T032, T033 → parallel (Bicep modules)
```

**Phase 3 (US1)**:
```
T041, T042, T043 → parallel (tests)
T046, T047 → parallel (auth endpoints)
```

**Phase 4 (US2)**:
```
T056, T057, T058 → parallel (tests)
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 - Login
4. **VALIDATE**: Test login independently
5. Complete Phase 4: US2 - Números
6. **MVP READY**: Deploy/demo - sistema funcional para geração de números
7. Estimated: ~60% of tasks for 100% of core functionality

### Incremental Delivery

| Delivery | Stories | Value |
|----------|---------|-------|
| MVP | US1 + US2 | Core: Login + Gerar números |
| Release 2 | US3 | Auditoria com histórico |
| Release 3 | US4 + US5 | Admin: gerenciar tipos e usuários |
| Release 4 | US6 | Automação de virada de ano |

### Task Count Summary

| Phase | Tasks | Parallelizable |
|-------|-------|----------------|
| Phase 1: Setup | 10 | 8 |
| Phase 2: Foundational | 30 | 18 |
| Phase 3: US1 Login | 17 | 5 |
| Phase 4: US2 Números | 11 | 3 |
| Phase 5: US3 Histórico | 10 | 2 |
| Phase 6: US4 Tipos | 9 | 4 |
| Phase 7: US5 Usuários | 10 | 4 |
| Phase 8: US6 Reinício | 4 | 1 |
| Phase 9: Polish | 14 | 7 |
| **Total** | **115** | **52 (45%)** |

---

## Notes

- **[P]** = diferentes arquivos, sem dependências, pode rodar em paralelo
- **[Story]** = rastreabilidade para user story específica
- MVP viável com ~55 tasks (Phases 1-4)
- Cada user story é independentemente testável após conclusão
- Commitar após cada task ou grupo lógico
- Validar tests falham antes de implementar
- Azure Tables usa ETag para concorrência - critical para NumberService
