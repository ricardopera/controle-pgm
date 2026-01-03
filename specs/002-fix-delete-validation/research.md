# Research: Correções de Exclusão e Validação

**Feature**: 002-fix-delete-validation
**Date**: 2026-01-03
**Status**: Completo

## Investigation Summary

### Bug 1: Desativação de Usuários

#### Análise do Backend

**Arquivo**: `backend/functions/users/delete.py`
```python
@bp.route(route="users/{user_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS)
@handle_errors
@require_admin
def delete_user(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
```

**Status**: ✅ Implementado corretamente
- Endpoint existe e está registrado
- Decorator `@require_admin` aplicado
- Chama `UserService.deactivate()` corretamente
- Registra ação de auditoria

**Arquivo**: `backend/services/user_service.py`
```python
@staticmethod
def deactivate(user_id: str, current_admin_id: str) -> UserEntity:
    if user_id == current_admin_id:
        raise ForbiddenError("Não é possível desativar a si mesmo")
    # ... validações de último admin
    return UserService.update(user_id, {"IsActive": False})
```

**Status**: ✅ Implementado corretamente
- Proteção contra auto-desativação
- Proteção contra desativar último admin
- Atualiza campo `IsActive` para `False`

#### Análise do Frontend

**Arquivo**: `frontend/src/components/features/UsersList.tsx`

**Função `handleToggleActive`** (linhas 107-120):
```typescript
async function handleToggleActive(user: User) {
  try {
    if (user.is_active) {
      await api.delete(`/users/${user.id}`);
      toast.success(`Usuário "${user.name}" desativado!`);
    } else {
      await api.put(`/users/${user.id}`, { is_active: true });
      toast.success(`Usuário "${user.name}" ativado!`);
    }
    await loadUsers();
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Erro ao alterar status';
    toast.error(message);
  }
}
```

**Status**: ⚠️ Possível problema
- A função está implementada corretamente
- O catch captura apenas `Error` genérico, não `ApiError`
- Mensagem de erro da API pode não ser exibida corretamente

**Botão de Toggle** (linhas 380-415):
```typescript
<Button
  variant="ghost"
  size="sm"
  onClick={() => handleToggleActive(user)}
  title={user.is_active ? 'Desativar' : 'Ativar'}
>
```

**Status**: ✅ Implementado corretamente

#### Causa Raiz Identificada

**Problema**: O handler `handleToggleActive` não trata corretamente erros do tipo `ApiError`:
```typescript
const message = err instanceof Error ? err.message : 'Erro ao alterar status';
```

Deveria ser:
```typescript
const message = err instanceof ApiError 
  ? (err.data?.error as string) || 'Erro ao alterar status'
  : 'Erro ao alterar status';
```

---

### Bug 2: Desativação de Tipos de Documento

#### Análise do Backend

**Arquivo**: `backend/functions/document_types/delete.py`
```python
@bp.route(
    route="document-types/{doc_type_id}", methods=["DELETE"], auth_level=func.AuthLevel.ANONYMOUS
)
@handle_errors
@require_admin
def delete_document_type(req: func.HttpRequest, current_user: CurrentUser) -> func.HttpResponse:
```

**Status**: ✅ Implementado corretamente

**Arquivo**: `backend/services/document_type_service.py`
```python
@staticmethod
def deactivate(doc_type_id: str) -> DocumentTypeEntity:
    return DocumentTypeService.update(doc_type_id, DocumentTypeUpdate(is_active=False))
```

**Status**: ✅ Implementado corretamente

#### Análise do Frontend

**Arquivo**: `frontend/src/components/features/DocumentTypesList.tsx`

**Função `handleToggleActive`** (linhas 79-91):
```typescript
async function handleToggleActive(type: DocumentType) {
  try {
    if (type.is_active) {
      await api.delete(`/document-types/${type.id}`);
      toast.success(`Tipo "${type.name}" desativado!`);
    } else {
      await api.put(`/document-types/${type.id}`, { is_active: true });
      toast.success(`Tipo "${type.name}" ativado!`);
    }
    await loadDocumentTypes();
  } catch (err) {
    const message = err instanceof Error ? err.message : 'Erro ao alterar status';
    toast.error(message);
  }
}
```

**Status**: ⚠️ Mesmo problema do Bug 1

#### Causa Raiz Identificada

**Problema**: Idêntico ao Bug 1 - tratamento incorreto de `ApiError`.

---

### Bug 3: Documentos Inativos na Geração

#### Análise do Backend

**Arquivo**: `backend/services/number_service.py` (linhas 100-103):
```python
# Verify document type exists and is active
doc_type = DocumentTypeService.get_by_code(document_type_code)
if not doc_type:
    raise NotFoundError(f"Tipo de documento '{document_type_code}' não encontrado")
if not doc_type.IsActive:
    raise NotFoundError(f"Tipo de documento '{document_type_code}' está inativo")
```

**Status**: ✅ Validação implementada corretamente

**Arquivo**: `backend/functions/document_types/list.py`:
```python
# Check if admin wants all document types
include_all = req.params.get("all", "").lower() == "true"

if include_all and current_user["role"] == "admin":
    doc_types = DocumentTypeService.list_all()
else:
    doc_types = DocumentTypeService.list_active()
```

**Status**: ✅ Filtro implementado corretamente

#### Análise do Frontend

**Arquivo**: `frontend/src/components/features/NumberGenerator.tsx` (linha 51):
```typescript
const response = await api.get<DocumentTypesListResponse>('/document-types');
```

**Status**: ✅ Chama endpoint sem `?all=true`, portanto só recebe tipos ativos

#### Possível Causa Raiz

Se tipos inativos ainda aparecem, pode ser por:
1. **Cache do navegador** - dados antigos em localStorage ou sessionStorage
2. **Estado React desatualizado** - componente não re-renderiza após mudança
3. **API retornando dados incorretos** - bug no filtro de backend (pouco provável)

**Investigação adicional necessária**: Verificar se o frontend implementa algum tipo de cache local.

---

## Resumo das Correções Necessárias

### Correção 1: Tratamento de Erros (P1)

**Arquivos afetados**:
- `frontend/src/components/features/UsersList.tsx`
- `frontend/src/components/features/DocumentTypesList.tsx`

**Mudança**:
```typescript
// De:
const message = err instanceof Error ? err.message : 'Erro ao alterar status';

// Para:
const message = err instanceof ApiError 
  ? (err.data?.error as string) || 'Erro ao alterar status'
  : err instanceof Error 
    ? err.message 
    : 'Erro ao alterar status';
```

### Correção 2: Filtro Adicional no NumberGenerator (P2)

**Arquivo**: `frontend/src/components/features/NumberGenerator.tsx`

**Mudança**: Adicionar filtro explícito como segurança adicional:
```typescript
// Após receber response da API:
const activeTypes = response.items.filter(type => type.is_active);
setDocumentTypes(activeTypes);
```

### Correção 3: Forçar Reload Após Toggle (P2)

Garantir que `loadUsers()` e `loadDocumentTypes()` são chamados e que o estado é atualizado corretamente.

---

## Decisões Técnicas

| Decisão | Escolha | Alternativas Consideradas | Justificativa |
|---------|---------|---------------------------|---------------|
| Tratamento de erros | Verificar `ApiError` primeiro | Criar wrapper genérico | Mais simples, seguir padrão existente |
| Filtro de tipos inativos | Dupla verificação (backend + frontend) | Apenas backend | Defesa em profundidade |
| Testes | Adicionar testes unitários + E2E | Apenas testes manuais | Conformidade com Constitution |

## Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| Bug não é o tratamento de erro | Baixa | Médio | Testar localmente antes de implementar |
| Regressão em outras funcionalidades | Muito Baixa | Baixo | Rodar todos os testes existentes |
| Cache do navegador causando problemas | Média | Baixo | Adicionar versão na URL ou header no-cache |
