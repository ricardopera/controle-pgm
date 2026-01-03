# Feature Specification: Correções de Exclusão e Validação

**Feature Branch**: `002-fix-delete-validation`  
**Created**: 2026-01-03  
**Status**: Draft  
**Input**: User description: "Correções para exclusão de usuários e tipos de documentos, e validação de documentos desabilitados na geração de números"

## Resumo do Problema

O sistema atual apresenta três bugs relacionados:

1. **Exclusão de Usuários**: Não é possível excluir/desativar usuários através da interface
2. **Exclusão de Tipos de Documento**: Não é possível excluir/desativar tipos de documento através da interface  
3. **Validação de Documentos Desabilitados**: O sistema permite solicitar números de tipos de documentos que estão desabilitados

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Desativar Usuário (Priority: P1)

Um administrador precisa desativar um usuário que não deve mais ter acesso ao sistema. Ele acessa a lista de usuários, localiza o usuário desejado e clica no botão de desativar. O sistema solicita confirmação e, após confirmado, o usuário é desativado com sucesso.

**Why this priority**: Gerenciar o acesso de usuários é crítico para segurança do sistema. Sem a possibilidade de desativar usuários, ex-funcionários ou usuários problemáticos podem continuar acessando o sistema.

**Independent Test**: Pode ser testado criando um usuário de teste, tentando desativá-lo pela interface, e verificando que o status muda para inativo.

**Acceptance Scenarios**:

1. **Given** um usuário ativo existe no sistema, **When** o administrador clica em desativar e confirma, **Then** o usuário é desativado e não pode mais fazer login
2. **Given** o administrador está na lista de usuários, **When** ele tenta desativar o último administrador ativo, **Then** o sistema exibe mensagem de erro informando que não é possível desativar o último admin
3. **Given** um administrador está logado, **When** ele tenta desativar a si mesmo, **Then** o sistema exibe mensagem de erro informando que não é possível se auto-desativar

---

### User Story 2 - Desativar Tipo de Documento (Priority: P1)

Um administrador precisa desativar um tipo de documento que não está mais em uso. Ele acessa a lista de tipos de documento, localiza o tipo desejado e clica no botão de desativar. O sistema solicita confirmação e, após confirmado, o tipo é desativado.

**Why this priority**: Tipos de documento desativados não devem estar disponíveis para geração de novos números, mantendo a integridade do sistema de numeração.

**Independent Test**: Pode ser testado criando um tipo de documento de teste, desativando-o pela interface, e verificando que o status muda para inativo.

**Acceptance Scenarios**:

1. **Given** um tipo de documento ativo existe, **When** o administrador clica em desativar e confirma, **Then** o tipo é desativado com sucesso
2. **Given** um tipo de documento foi desativado, **When** um usuário tenta selecionar esse tipo para gerar número, **Then** o tipo não aparece na lista de opções disponíveis

---

### User Story 3 - Bloqueio de Geração para Documentos Inativos (Priority: P2)

Quando um usuário tenta gerar um número para um tipo de documento que foi desativado (por exemplo, através de chamada direta à API), o sistema deve recusar a operação e informar que o tipo de documento está inativo.

**Why this priority**: Esta é uma validação de segurança que impede bypass do sistema de controle de tipos de documentos.

**Independent Test**: Pode ser testado via API enviando requisição de geração de número para um tipo de documento inativo e verificando que retorna erro apropriado.

**Acceptance Scenarios**:

1. **Given** um tipo de documento está inativo, **When** uma requisição de geração de número é feita para esse tipo via API, **Then** o sistema retorna erro 404 com mensagem "Tipo de documento está inativo"
2. **Given** um tipo de documento está ativo, **When** é desativado enquanto um usuário está com a tela de geração aberta, **Then** ao tentar gerar, o usuário recebe mensagem de erro apropriada

---

### Edge Cases

- O que acontece quando o único administrador tenta se desativar?
  - Sistema deve impedir a operação
- O que acontece quando há requisições simultâneas de desativação para o mesmo registro?
  - Sistema deve processar apenas uma e retornar resultado para ambas chamadas
- O que acontece se a lista de tipos de documentos for recarregada após uma desativação?
  - Tipos inativos não devem aparecer na lista de geração de números, mas devem aparecer na lista de administração

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE permitir que administradores desativem usuários através da interface
- **FR-002**: Sistema DEVE impedir a desativação do último administrador ativo
- **FR-003**: Sistema DEVE impedir que administradores desativem a si mesmos
- **FR-004**: Sistema DEVE permitir que administradores desativem tipos de documento através da interface
- **FR-005**: Sistema DEVE retornar erro 404 ao tentar gerar número para tipo de documento inativo
- **FR-006**: Sistema DEVE exibir apenas tipos de documento ativos no formulário de geração de números
- **FR-007**: Sistema DEVE permitir reativar usuários inativos
- **FR-008**: Sistema DEVE permitir reativar tipos de documento inativos
- **FR-009**: Sistema DEVE exibir mensagens de erro claras quando operações falharem
- **FR-010**: Sistema DEVE registrar no log de auditoria todas as operações de desativação/ativação

### Key Entities

- **User**: Representa um usuário do sistema. Atributos relevantes: ID, nome, email, role (admin/user), status (ativo/inativo)
- **DocumentType**: Representa um tipo de documento. Atributos relevantes: ID, código, nome, status (ativo/inativo)
- **NumberLog**: Registro de auditoria de operações de numeração. Inclui referência ao tipo de documento e usuário

## Suposições

- O backend já possui a lógica de desativação implementada corretamente (soft delete)
- O frontend já possui os componentes de UI necessários (dialogs, botões, etc.)
- O problema pode estar na comunicação entre frontend e backend ou na lógica de exibição dos controles
- A validação de documento inativo já existe no backend (\`NumberService.generate_number\`)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Administradores conseguem desativar usuários em menos de 30 segundos via interface
- **SC-002**: Administradores conseguem desativar tipos de documento em menos de 30 segundos via interface
- **SC-003**: 100% das tentativas de gerar número para documento inativo retornam erro apropriado
- **SC-004**: Zero ocorrências de tipos de documento inativos aparecendo no formulário de geração
- **SC-005**: Mensagens de erro são exibidas ao usuário em 100% dos casos de falha
- **SC-006**: Operações de ativação/desativação são registradas no log de auditoria
