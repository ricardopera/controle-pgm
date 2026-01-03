# Validation Checklist - Hard Delete

## User Story 4: Excluir Usuário Permanentemente

- [ ] Botão "Lixeira" aparece na lista de usuários
- [ ] Clicar na "Lixeira" abre diálogo de confirmação específico ("Excluir Permanentemente")
- [ ] Confirmar exclusão chama `DELETE /api/users/{id}`
- [ ] Backend remove o registro da tabela `Users`
- [ ] Tentar excluir o último admin retorna erro 403
- [ ] Tentar excluir a si mesmo retorna erro 403

## User Story 5: Excluir Tipo de Documento Permanentemente

- [ ] Botão "Lixeira" aparece na lista de tipos de documento
- [ ] Clicar na "Lixeira" abre diálogo de confirmação específico
- [ ] Confirmar exclusão chama `DELETE /api/document-types/{id}`
- [ ] Backend remove o registro da tabela `DocumentTypes`
- [ ] Tentar excluir tipo com números gerados retorna erro 409 (Conflict)

## Regression Testing (Soft Delete)

- [ ] Botão "Desativar" (Olho Riscado) continua funcionando
- [ ] Confirmar desativação chama `PUT /api/users/{id}` com `is_active: false`
- [ ] Usuário desativado aparece como "Inativo" na lista
- [ ] Botão "Ativar" (Olho) funciona e chama `PUT` com `is_active: true`
