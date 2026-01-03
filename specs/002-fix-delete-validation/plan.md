# Implementation Plan: Correções de Exclusão e Validação

**Branch**: `002-fix-delete-validation` | **Date**: 2026-01-03 | **Spec**: [spec.md](spec.md)
**Input**: Bug fixes para funcionalidades existentes do feature 001-controle-numeracao

## Summary

Correções de bugs identificados no sistema de controle de numeração. Três problemas principais foram identificados:
1. Desativação de usuários não funciona através da interface
2. Desativação de tipos de documento não funciona através da interface
3. Tipos de documento desabilitados ainda aparecem disponíveis para geração de números

A análise do código existente mostra que:
- Backend: Lógica de desativação implementada corretamente
- Frontend: Componentes existentes, porém podem ter bugs na comunicação com API
- API: Filtro `?all=true` implementado para listagem

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: Azure Functions v4, React 18, Shadcn/UI
**Storage**: Azure Tables (já implementado)
**Testing**: pytest (backend), Vitest (frontend)
**Target Platform**: Azure (Brazil South)
**Project Type**: Web (monorepo com backend e frontend separados)
**Performance Goals**: < 500ms p95 para operações
**Constraints**: Nenhum (bug fixes)
**Scale/Scope**: Correção pontual em 3-5 arquivos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Qualidade de Código | ✅ | Correções seguem padrões existentes |
| II. Padrões de Teste | ✅ | Adicionar testes para os cenários corrigidos |
| III. Experiência do Usuário | ✅ | Mensagens de erro claras, feedback imediato |
| IV. Azure Cost-Efficient | ✅ | Sem impacto em custos (bug fix) |

**Post-Design Re-Check**: N/A - não há mudanças de arquitetura

## Root Cause Analysis

### Bug 1: Desativação de Usuários

**Análise do Código**:
- `backend/functions/users/delete.py`: Endpoint DELETE funciona corretamente
- `backend/services/user_service.py`: `deactivate()` implementado com proteções
- `frontend/src/components/features/UsersList.tsx`: 
  - `handleToggleActive()` (linha 107-120) chama `api.delete()` e `api.put()`
  - Botão de toggle existe (linha 380-415)

**Possível Causa**: O botão de desativar existe e chama a função correta. Precisa investigar se há erro de comunicação com a API ou se o estado não está sendo atualizado.

### Bug 2: Desativação de Tipos de Documento

**Análise do Código**:
- `backend/functions/document_types/delete.py`: Endpoint DELETE funciona
- `backend/services/document_type_service.py`: `deactivate()` implementado
- `frontend/src/components/features/DocumentTypesList.tsx`:
  - `handleToggleActive()` (linha 79-91) chama `api.delete()` e `api.put()`
  - Botão existe (linha 280-283)

**Possível Causa**: Similar ao bug 1. Verificar comunicação e atualização de estado.

### Bug 3: Documentos Inativos na Geração

**Análise do Código**:
- `backend/services/number_service.py`: Já valida `if not doc_type.IsActive` (linha 102)
- `backend/functions/document_types/list.py`: Filtra por `?all=true`
- `frontend/src/components/features/NumberGenerator.tsx`:
  - Chama `/document-types` sem `?all=true` (linha 51)

**Possível Causa**: O frontend chama API corretamente. O backend filtra corretamente. Pode ser que o bug seja na camada de cache ou que tipos inativos estejam sendo exibidos após recarga.

## Investigation Tasks

Para confirmar as causas raiz, é necessário:

1. **Testar localmente** as operações de desativação e verificar logs de console
2. **Verificar** se os endpoints DELETE retornam status 200 corretamente
3. **Confirmar** que a lista de document types no NumberGenerator não inclui inativos
4. **Validar** comportamento do `handleToggleActive` com diferentes cenários

## Project Structure

### Documentation (this feature)

```text
specs/002-fix-delete-validation/
├── spec.md              # Especificação do bug fix
├── plan.md              # Este arquivo
├── research.md          # Investigação dos bugs (Phase 0)
├── checklists/
│   └── requirements.md  # Checklist de requisitos
└── tasks.md             # Lista de tarefas (Phase 2)
```

### Source Code (arquivos potencialmente afetados)

```text
backend/
├── functions/
│   ├── users/
│   │   └── delete.py           # [VERIFICAR] Endpoint DELETE usuário
│   ├── document_types/
│   │   ├── delete.py           # [VERIFICAR] Endpoint DELETE tipo
│   │   └── list.py             # [OK] Já implementa filtro
│   └── numbers/
│       └── generate.py         # [VERIFICAR] Validação de tipo inativo
├── services/
│   ├── user_service.py         # [OK] Lógica implementada
│   ├── document_type_service.py # [OK] Lógica implementada
│   └── number_service.py       # [OK] Validação existe (linha 100-103)
└── tests/
    ├── unit/
    │   └── test_deactivation.py  # [NOVO] Testes de desativação
    └── integration/
        └── test_deactivation_api.py # [NOVO] Testes E2E

frontend/
├── src/
│   ├── components/
│   │   └── features/
│   │       ├── UsersList.tsx          # [VERIFICAR] handleToggleActive
│   │       ├── DocumentTypesList.tsx  # [VERIFICAR] handleToggleActive
│   │       └── NumberGenerator.tsx    # [VERIFICAR] filtro de tipos
│   └── lib/
│       └── api.ts                     # [OK] métodos implementados
└── tests/
    └── deactivation.test.tsx          # [NOVO] Testes de UI
```

**Structure Decision**: Nenhuma mudança estrutural. Correções pontuais nos arquivos existentes.

## Fixes Identificadas

### Fix 1: Garantir Atualização de Estado Após Desativação

**Arquivos**: `UsersList.tsx`, `DocumentTypesList.tsx`
**Problema Provável**: Estado não está sendo atualizado após operação bem-sucedida
**Solução**: Verificar se `loadUsers()` e `loadDocumentTypes()` são chamados após sucesso

### Fix 2: Filtrar Tipos Inativos no NumberGenerator

**Arquivos**: `NumberGenerator.tsx`
**Problema Provável**: Componente pode estar cacheando tipos ou não filtrando corretamente
**Solução**: Garantir que apenas tipos com `is_active: true` sejam exibidos

### Fix 3: Melhorar Mensagens de Erro

**Arquivos**: Todos os componentes afetados
**Problema Provável**: Erros da API não estão sendo exibidos ao usuário
**Solução**: Capturar e exibir mensagens de erro da API corretamente

## Complexity Tracking

| Área | Complexidade | Justificativa |
|------|--------------|---------------|
| Investigação | Baixa | Código já existe, precisa debug |
| Frontend Fixes | Baixa | Ajustes pontuais em handlers |
| Backend Fixes | Muito Baixa | Se necessário, ajustes mínimos |
| Testes | Baixa | Cenários específicos |

Nenhuma violação de constituição identificada.

## Phase Summary

### Phase 0: Research ✅ (a executar)
- Investigar causas raiz com debug local
- Documentar comportamento atual vs esperado

### Phase 1: Design ✅ (a executar)
- Definir correções específicas
- Sem mudanças em data-model ou contracts (bug fix)

### Phase 2: Tasks (próximo)
- Gerar tasks.md com fixes específicos
- Estimar 2-4 horas de trabalho

## Related Documents

- [Constitution](../../.specify/memory/constitution.md) - Princípios do projeto
- [Spec](spec.md) - Especificação dos bugs
- [Feature 001 Plan](../001-controle-numeracao/plan.md) - Contexto original
- [Feature 001 Data Model](../001-controle-numeracao/data-model.md) - Schema existente
