# Feature Specification: Controle de Numeração de Documentos

**Feature Branch**: `001-controle-numeracao`  
**Created**: 2025-12-29  
**Status**: Draft  
**Input**: Sistema de controle de numeração sequencial de documentos para PGM Itajaí

## Clarifications

### Session 2025-12-29

- Q: Qual formato de exibição do número deve ser usado? → A: Formato "N/AAAA" sem zeros à esquerda (ex: 1/2025, 25/2026, 2150/2026)
- Q: Sistema deve confirmar antes de gerar número? → A: Sim, exibir modal de confirmação antes de gerar (evita cliques acidentais)
- Q: Visibilidade do histórico entre usuários? → A: Todos da unidade - qualquer usuário vê todas as numerações da PGM
- Q: Comportamento após gerar número? → A: Modal com número gerado + botões "Copiar" e "Fechar", permanece na mesma tela
- Q: Política de senhas? → A: Moderada - mínimo 8 caracteres, pelo menos 1 letra e 1 número

## Visão Geral

Sistema web para controle de numeração sequencial de documentos da Procuradoria-Geral do Município de Itajaí. Cada tipo de documento (Comunicações Internas, Ofícios, Despachos, etc.) possui sequência própria que reinicia a cada ano.

## User Scenarios & Testing

### User Story 1 - Login no Sistema (Priority: P1)

Servidor público acessa o sistema com e-mail e senha para obter acesso às funcionalidades.

**Why this priority**: Sem autenticação, nenhuma outra funcionalidade pode ser acessada. É o ponto de entrada obrigatório.

**Independent Test**: Pode ser testado acessando a página de login, inserindo credenciais válidas e verificando redirecionamento para dashboard.

**Acceptance Scenarios**:

1. **Given** usuário não autenticado na página de login, **When** insere e-mail e senha válidos, **Then** é redirecionado ao dashboard com sessão ativa
2. **Given** usuário não autenticado na página de login, **When** insere credenciais inválidas, **Then** exibe mensagem "E-mail ou senha incorretos" sem revelar qual está errado
3. **Given** usuário autenticado, **When** clica em "Sair", **Then** sessão é encerrada e redirecionado para login
4. **Given** usuário não autenticado, **When** tenta acessar qualquer rota protegida, **Then** é redirecionado para login

---

### User Story 2 - Solicitar Número de Documento (Priority: P1)

Servidor solicita próximo número sequencial para um tipo de documento específico.

**Why this priority**: É a funcionalidade core do sistema - razão principal de sua existência.

**Independent Test**: Usuário logado seleciona tipo "Ofício", clica em "Solicitar Número" e recebe número formatado.

**Acceptance Scenarios**:

1. **Given** usuário autenticado no dashboard, **When** seleciona tipo "Ofício" e clica "Solicitar Número", **Then** sistema exibe modal "Confirmar geração de Ofício?" com botões "Confirmar" e "Cancelar"
2. **Given** modal de confirmação exibido, **When** usuário clica "Confirmar", **Then** sistema gera número e exibe modal de sucesso com número "1/2025", botões "Copiar" e "Fechar"
3. **Given** modal de sucesso exibido, **When** usuário clica "Copiar", **Then** número é copiado para área de transferência e feedback visual é exibido
4. **Given** modal de sucesso exibido, **When** usuário clica "Fechar", **Then** modal fecha e usuário permanece no dashboard
5. **Given** modal de confirmação exibido, **When** usuário clica "Cancelar", **Then** modal fecha e nenhum número é gerado
6. **Given** usuário solicita número de "Ofício" (atual 1/2025), **When** outro usuário solicita "Ofício", **Then** recebe "2/2025" (sequencial incrementado)
7. **Given** dois usuários solicitam número simultaneamente, **When** ambas requisições processadas, **Then** cada um recebe número único sem duplicação
8. **Given** usuário autenticado, **When** solicita número de "Comunicação Interna", **Then** recebe número da sequência correta (independente de Ofício)

---

### User Story 3 - Visualizar Histórico de Números (Priority: P2)

Servidor visualiza números já emitidos com filtros por tipo, data e usuário. Todos os usuários têm acesso ao histórico completo da PGM para fins de auditoria e conferência.

**Why this priority**: Importante para auditoria e conferência, mas não bloqueia operação principal.

**Independent Test**: Usuário acessa tela de histórico, aplica filtro por tipo "Ofício" e visualiza lista.

**Acceptance Scenarios**:

1. **Given** usuário autenticado, **When** acessa histórico sem filtros, **Then** exibe últimos 50 números emitidos por qualquer usuário, ordenados por data decrescente
2. **Given** usuário no histórico, **When** filtra por tipo "Despacho", **Then** exibe apenas números de Despachos (de todos os usuários)
3. **Given** usuário no histórico, **When** filtra por período "01/12/2025 a 31/12/2025", **Then** exibe apenas números desse período
4. **Given** usuário no histórico, **When** clica em exportar CSV, **Then** baixa arquivo com dados filtrados

---

### User Story 4 - Gerenciar Tipos de Documento (Priority: P2)

Administrador cadastra, edita ou desativa tipos de documentos.

**Why this priority**: Sistema precisa de tipos pré-cadastrados, mas pode iniciar com seed. Gerenciamento é secundário.

**Independent Test**: Admin acessa configurações, adiciona tipo "Parecer" e verifica disponibilidade na solicitação.

**Acceptance Scenarios**:

1. **Given** admin autenticado em configurações, **When** adiciona tipo "Parecer" com prefixo "PAR", **Then** tipo disponível para solicitação
2. **Given** admin em configurações, **When** desativa tipo "Comunicação Interna", **Then** tipo não aparece mais para solicitação mas histórico preservado
3. **Given** admin edita tipo existente, **When** altera nome de "Ofício" para "Ofício Externo", **Then** novo nome refletido em todo sistema
4. **Given** tipo com números já emitidos, **When** admin tenta excluir, **Then** sistema permite apenas desativar (soft delete)

---

### User Story 5 - Gerenciar Usuários (Priority: P2)

Administrador cadastra e gerencia servidores com acesso ao sistema.

**Why this priority**: Necessário para onboarding de novos servidores, mas pode iniciar com usuário seed.

**Independent Test**: Admin cadastra novo usuário e verifica que consegue fazer login.

**Acceptance Scenarios**:

1. **Given** admin em gerenciamento de usuários, **When** cadastra servidor com e-mail, nome e senha temporária, **Then** servidor consegue fazer login
2. **Given** admin visualiza lista de usuários, **When** desativa usuário, **Then** usuário não consegue mais logar
3. **Given** usuário logado pela primeira vez com senha temporária, **When** acessa sistema, **Then** é forçado a alterar senha
4. **Given** admin em gerenciamento, **When** define usuário como admin, **Then** usuário ganha acesso às configurações
5. **Given** admin em gerenciamento, **When** remove role admin de outro usuário, **Then** usuário perde acesso às configurações (mas mantém acesso básico)

---

### User Story 6 - Reinício Anual Automático (Priority: P3)

Sistema reinicia sequências automaticamente no início de cada ano.

**Why this priority**: Crítico para operação correta, mas acontece apenas 1x por ano. Pode ser validado em staging.

**Independent Test**: Simular data 01/01/2026 e verificar que próximo número é 1/2026.

**Acceptance Scenarios**:

1. **Given** último número de "Ofício" em 2025 é 150/2025, **When** primeiro usuário solicita "Ofício" em 01/01/2026, **Then** recebe "1/2026"
2. **Given** virada de ano, **When** sistema processa, **Then** todas as sequências de todos os tipos reiniciam independentemente
3. **Given** números de 2025 existentes, **When** ano muda para 2026, **Then** histórico de 2025 permanece acessível e inalterado

---

### Edge Cases

- **Concorrência**: Dois usuários solicitando número do mesmo tipo simultaneamente DEVEM receber números diferentes
- **Timezone**: Sistema DEVE usar horário de Brasília (America/Sao_Paulo) para determinar o ano
- **Sessão expirada**: Após 8 horas de inatividade, usuário DEVE ser redirecionado para login
- **Tipo inexistente**: Requisição para tipo não cadastrado DEVE retornar erro 404
- **Usuário desativado**: Tentativa de login DEVE falhar com mensagem genérica

## Requirements

### Functional Requirements

- **FR-001**: Sistema DEVE autenticar usuários via e-mail e senha
- **FR-002**: Sistema DEVE gerar números sequenciais únicos por tipo de documento e ano
- **FR-003**: Sistema DEVE garantir atomicidade na geração de números (sem duplicatas)
- **FR-004**: Sistema DEVE formatar números como "N/AAAA" sem zeros à esquerda (ex: 1/2025, 25/2026, 2150/2026)
- **FR-005**: Sistema DEVE registrar log de cada número gerado (data/hora, usuário, tipo, número)
- **FR-006**: Sistema DEVE reiniciar sequências automaticamente a cada ano
- **FR-007**: Sistema DEVE permitir CRUD de tipos de documentos (admin)
- **FR-008**: Sistema DEVE permitir CRUD de usuários (admin)
- **FR-009**: Sistema DEVE permitir consulta e exportação do histórico
- **FR-010**: Sistema DEVE usar horário de Brasília para todas as operações

### Non-Functional Requirements

- **NFR-001**: Tempo de resposta para geração de número < 500ms (p95)
- **NFR-002**: Disponibilidade 99% em horário comercial (8h-18h, seg-sex)
- **NFR-003**: Senhas armazenadas com hash bcrypt (cost factor ≥ 12)
- **NFR-003a**: Política de senha: mínimo 8 caracteres, pelo menos 1 letra e 1 número
- **NFR-004**: HTTPS obrigatório em produção
- **NFR-005**: Backup diário do banco de dados
- **NFR-006**: Interface responsiva (funcional em mobile)
- **NFR-007**: Custo mensal Azure < R$ 50 para ambiente produção

### Key Entities

- **User**: Servidor público com acesso ao sistema (email, nome, senha, role, ativo)
- **DocumentType**: Tipo de documento (nome, prefixo, ativo, criado_em)
- **Sequence**: Controle de sequência (tipo_id, ano, ultimo_numero)
- **NumberLog**: Registro de números emitidos (tipo_id, numero, ano, usuario_id, emitido_em)

## Assumptions

- **E-mail institucional**: Usuários utilizam e-mail da prefeitura (domínio @itajai.sc.gov.br ou similar)
- **Fuso horário**: Sistema opera em horário de Brasília (America/Sao_Paulo) para determinação do ano
- **Tipos iniciais**: Sistema inicia com tipos pré-cadastrados: Comunicação Interna, Ofício, Despacho
- **Volume estimado**: Menos de 1000 numerações/ano, menos de 50 usuários ativos
- **Retenção**: Histórico mantido indefinidamente (sem política de expurgo)
- **Primeiro usuário admin**: Criado via seed no deploy inicial

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuários conseguem solicitar e obter um número em menos de 3 segundos
- **SC-002**: 100% das numerações são únicas por tipo/ano (zero duplicatas)
- **SC-003**: Sistema suporta 20 usuários simultâneos sem degradação perceptível
- **SC-004**: 95% dos usuários completam solicitação de número na primeira tentativa
- **SC-005**: Consulta de histórico retorna em menos de 5 segundos (até 10.000 registros)
- **SC-006**: Disponibilidade de 99% em horário comercial (8h-18h, dias úteis)
- **SC-007**: Custo mensal da infraestrutura Azure inferior a R$ 50

## Out of Scope (v1)

- Integração com outros sistemas da Prefeitura
- Assinatura digital de documentos
- Armazenamento de documentos (apenas números)
- Recuperação de senha por e-mail (admin reseta manualmente)
- Múltiplas procuradorias (apenas PGM Itajaí)
- API pública para terceiros
