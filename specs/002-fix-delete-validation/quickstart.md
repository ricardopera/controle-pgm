# Quickstart: Correções de Exclusão e Validação

**Feature**: 002-fix-delete-validation
**Date**: 2026-01-03

## Pré-requisitos

Este é um bug fix para o sistema existente. Siga o [quickstart do feature 001](../001-controle-numeracao/quickstart.md) se o ambiente não estiver configurado.

## Setup Rápido

```bash
# 1. Certifique-se de estar no branch correto
git checkout 002-fix-delete-validation

# 2. Backend - verificar dependências
cd backend
source .venv/bin/activate
pip install -r requirements.txt

# 3. Frontend - verificar dependências
cd ../frontend
npm install

# 4. Iniciar serviços locais
# Terminal 1 - Backend
cd backend && func start

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## Reproduzindo os Bugs

### Bug 1: Desativação de Usuário

1. Acesse `http://localhost:5173/settings/users`
2. Clique no ícone de desativar (olho) em um usuário
3. **Comportamento Atual**: Nada acontece ou erro genérico
4. **Comportamento Esperado**: Usuário desativado com mensagem de sucesso

### Bug 2: Desativação de Tipo de Documento

1. Acesse `http://localhost:5173/settings/document-types`
2. Clique em "Desativar" em um tipo de documento
3. **Comportamento Atual**: Nada acontece ou erro genérico
4. **Comportamento Esperado**: Tipo desativado com mensagem de sucesso

### Bug 3: Tipos Inativos na Geração

1. Desative um tipo de documento (se o Bug 2 estiver corrigido, ou via API direta)
2. Acesse `http://localhost:5173` (Dashboard)
3. Verifique se o tipo desativado aparece no select
4. **Comportamento Atual**: Tipo inativo ainda aparece
5. **Comportamento Esperado**: Tipo inativo não aparece

## Verificando via API

```bash
# Desativar tipo de documento diretamente
curl -X DELETE http://localhost:7071/api/document-types/{id} \
  -H "Cookie: auth_token=<seu_token>"

# Listar tipos (deve mostrar apenas ativos)
curl http://localhost:7071/api/document-types \
  -H "Cookie: auth_token=<seu_token>"

# Listar todos os tipos (admin)
curl "http://localhost:7071/api/document-types?all=true" \
  -H "Cookie: auth_token=<seu_token>"
```

## Executando Testes

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm run test
```

## Validação das Correções

Após implementar as correções, verifique:

- [ ] Desativar usuário funciona e exibe mensagem de sucesso
- [ ] Erro ao desativar último admin exibe mensagem clara
- [ ] Erro ao auto-desativar exibe mensagem clara
- [ ] Desativar tipo de documento funciona
- [ ] Tipos inativos não aparecem no gerador de números
- [ ] Tentar gerar número para tipo inativo via API retorna 404
- [ ] Mensagens de erro da API são exibidas corretamente
