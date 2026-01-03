# Tasks: Correções de Exclusão e Validação

**Input**: Design documents from `/specs/002-fix-delete-validation/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| 1 | 2 | 0 | Setup - Verificação e preparação |
| 2 | 0 | 0 | Foundational - N/A (bug fix) |
| 3 | 3 | 2 | US1 - Desativar Usuário |
| 4 | 3 | 2 | US2 - Desativar Tipo de Documento |
| 5 | 3 | 2 | US3 - Bloqueio de Geração |
| 6 | 3 | 2 | Polish - Testes e validação final |
| **Total** | **14** | **8** | |

---

## Phase 1: Setup

**Purpose**: Verificar ambiente e preparar para correções

- [X] T001 Verificar que backend inicia sem erros em `backend/` com `func start`
- [X] T002 Verificar que frontend inicia sem erros em `frontend/` com `npm run dev`

---

## Phase 2: Foundational

**Purpose**: N/A - Este é um bug fix, não há infraestrutura nova necessária

**⚠️ Skip**: Infraestrutura já existe no feature 001-controle-numeracao

---

## Phase 3: User Story 1 - Desativar Usuário (Priority: P1) 🎯 MVP

**Goal**: Permitir que administradores desativem usuários através da interface

**Independent Test**: Acessar `/settings/users`, clicar no botão de desativar em um usuário ativo, confirmar que o status muda para inativo

### Implementation for User Story 1

- [X] T003 [P] [US1] Importar `ApiError` no topo de `frontend/src/components/features/UsersList.tsx`
- [X] T004 [US1] Corrigir tratamento de erro em `handleToggleActive()` de `frontend/src/components/features/UsersList.tsx` para verificar `ApiError` antes de `Error` genérico
- [X] T005 [US1] Testar manualmente desativação de usuário e verificar mensagem de erro ao tentar desativar último admin

**Checkpoint**: Desativação de usuários funciona e exibe mensagens de erro corretas

---

## Phase 4: User Story 2 - Desativar Tipo de Documento (Priority: P1)

**Goal**: Permitir que administradores desativem tipos de documento através da interface

**Independent Test**: Acessar `/settings/document-types`, clicar em "Desativar" em um tipo ativo, confirmar que o status muda para inativo

### Implementation for User Story 2

- [X] T006 [P] [US2] Importar `ApiError` no topo de `frontend/src/components/features/DocumentTypesList.tsx`
- [X] T007 [US2] Corrigir tratamento de erro em `handleToggleActive()` de `frontend/src/components/features/DocumentTypesList.tsx` para verificar `ApiError` antes de `Error` genérico
- [X] T008 [US2] Testar manualmente desativação de tipo de documento e verificar que lista atualiza corretamente

**Checkpoint**: Desativação de tipos de documento funciona e exibe mensagens de erro corretas

---

## Phase 5: User Story 3 - Bloqueio de Geração para Documentos Inativos (Priority: P2)

**Goal**: Garantir que tipos de documento inativos não apareçam no gerador de números e que a API rejeite requisições para tipos inativos

**Independent Test**: Desativar um tipo de documento, verificar que não aparece no select do gerador, tentar gerar via API e confirmar erro 404

### Implementation for User Story 3

- [X] T009 [P] [US3] Adicionar filtro defensivo `is_active: true` em `frontend/src/components/features/NumberGenerator.tsx` após receber resposta da API
- [X] T010 [P] [US3] Verificar que `backend/services/number_service.py` já valida `IsActive` (confirmação - não precisa mudança)
- [X] T011 [US3] Testar via API POST `/api/numbers/generate` com tipo inativo e verificar resposta 404

**Checkpoint**: Tipos inativos não aparecem no gerador e API rejeita corretamente

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Testes finais, validação e documentação

- [X] T012 [P] Executar `npm run lint` em `frontend/` e corrigir eventuais warnings
- [X] T013 [P] Executar `ruff check backend/` e corrigir eventuais warnings
- [X] T014 Validar todos os cenários da spec.md manualmente e documentar resultados em `specs/002-fix-delete-validation/checklists/validation.md`

---

## Dependencies

```
T001 ─┬─> T003 ─> T004 ─> T005 (US1 completo)
      │
T002 ─┼─> T006 ─> T007 ─> T008 (US2 completo)
      │
      └─> T009 ─┬─> T011 (US3 completo)
          T010 ─┘
      
T005, T008, T011 ──> T012, T013 ──> T014
```

## Parallel Execution Examples

### Batch 1: Setup (sequential)
```
T001 → T002
```

### Batch 2: US1 + US2 + US3 Import/Prep (parallel)
```
T003 | T006 | T009 | T010
```

### Batch 3: US1 + US2 + US3 Fixes (sequential per story, parallel across stories)
```
T004 → T005  |  T007 → T008  |  T011
```

### Batch 4: Polish (parallel)
```
T012 | T013 → T014
```

## Implementation Strategy

### MVP Scope
**User Story 1 (Desativar Usuário)** é o MVP mínimo - entrega valor imediato de segurança.

### Incremental Delivery
1. **Increment 1**: T001-T005 (Desativar usuários funciona) ✓ MVP
2. **Increment 2**: T006-T008 (Desativar tipos de documento funciona)
3. **Increment 3**: T009-T011 (Bloqueio de geração para inativos)
4. **Increment 4**: T012-T014 (Polish e validação)

### Estimated Time
- **Total**: 2-3 horas
- **Per task average**: ~10-15 minutos

## Validation Checklist

Ao final de todas as tasks, verificar:

- [ ] Desativar usuário funciona via interface
- [ ] Erro ao desativar último admin exibe mensagem clara
- [ ] Erro ao auto-desativar exibe mensagem clara
- [ ] Desativar tipo de documento funciona via interface
- [ ] Tipos inativos NÃO aparecem no gerador de números
- [ ] API rejeita geração para tipo inativo com erro 404
- [ ] Mensagens de erro da API são exibidas corretamente ao usuário
- [ ] Lint passa sem warnings (frontend e backend)
