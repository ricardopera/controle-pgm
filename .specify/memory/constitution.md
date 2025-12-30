<!--
SYNC IMPACT REPORT
==================
Version change: N/A → 1.0.0 (initial ratification)
Modified principles: N/A (new document)
Added sections:
  - Core Principles (4 principles)
  - Azure Infrastructure Standards
  - Quality Gates
  - Governance
Removed sections: N/A
Templates requiring updates:
  ✅ plan-template.md - Constitution Check section compatible
  ✅ spec-template.md - User Scenarios align with UX principle
  ✅ tasks-template.md - Test phases align with Testing Standards principle
Follow-up TODOs: None
-->

# Controle PGM Constitution

## Core Principles

### I. Qualidade de Código (NON-NEGOTIABLE)

O código DEVE ser limpo, legível e manutenível. Padrões rígidos garantem longevidade do projeto.

- **Legibilidade**: Nomes descritivos para variáveis, funções e classes. Código auto-documentado é preferível a comentários extensivos
- **Simplicidade**: YAGNI (You Aren't Gonna Need It) - implementar apenas o necessário. Evitar over-engineering
- **DRY (Don't Repeat Yourself)**: Código duplicado DEVE ser extraído para funções/módulos reutilizáveis
- **SOLID**: Princípios SOLID DEVEM guiar o design de classes e módulos
- **Linting obrigatório**: Código DEVE passar em todas as verificações de linting antes de merge
- **Type hints**: Tipagem estática DEVE ser usada (TypeScript, Python type hints, etc.)

**Rationale**: Código de baixa qualidade gera débito técnico exponencial. Manutenção consome 80% do tempo de desenvolvimento; código limpo reduz esse custo.

### II. Padrões de Teste (NON-NEGOTIABLE)

Testes são a documentação viva do sistema e garantem confiança nas alterações.

- **Cobertura mínima**: 80% de cobertura de código para features novas
- **Pirâmide de testes**: Mais testes unitários, menos testes de integração, poucos testes E2E
- **Testes unitários**: DEVEM ser rápidos (<100ms cada), isolados e determinísticos
- **Testes de integração**: DEVEM cobrir contratos de API e comunicação entre serviços
- **Nomenclatura**: Padrão `test_[método]_[cenário]_[resultado_esperado]`
- **Assertions claras**: Uma assertion principal por teste, mensagens de erro descritivas
- **CI obrigatório**: Nenhum merge sem todos os testes passando

**Rationale**: Testes permitem refatoração com confiança e documentam comportamento esperado. Investimento inicial economiza tempo em debugging e regressões.

### III. Experiência do Usuário (UX-First)

O usuário final é a razão de existir do sistema. Decisões técnicas DEVEM considerar impacto na UX.

- **Feedback imediato**: Operações DEVEM fornecer feedback visual em <100ms (loading states, skeleton screens)
- **Mensagens de erro claras**: Erros DEVEM ser em linguagem humana com ações sugeridas, nunca stack traces
- **Acessibilidade**: WCAG 2.1 AA compliance é obrigatório para interfaces web
- **Performance percebida**: Otimizar para tempo de interação, não apenas tempo de carregamento
- **Consistência**: Padrões de UI/UX DEVEM ser uniformes em toda a aplicação
- **Mobile-first**: Design responsivo é obrigatório; interfaces DEVEM funcionar em dispositivos móveis

**Rationale**: Software com UX ruim não é usado, independente da qualidade técnica. Usuário satisfeito = projeto bem-sucedido.

### IV. Infraestrutura Azure Cost-Efficient

Maximizar valor entregue por real gasto. Azure é a plataforma cloud padrão.

- **Serverless-first**: Preferir Azure Functions, Static Web Apps, e serviços consumption-based
- **Tier gratuito**: Utilizar tiers gratuitos quando viável (Azure Functions Consumption, Cosmos DB free tier, etc.)
- **Auto-scaling**: Configurar scale-to-zero para ambientes não-produtivos
- **Storage otimizado**: Usar Azure Blob Storage com tiers adequados (Hot/Cool/Archive)
- **Database**: Preferir Azure SQL Serverless ou Cosmos DB Serverless para cargas variáveis
- **Monitoramento de custos**: Budget alerts DEVEM ser configurados; revisão mensal obrigatória
- **IaC obrigatório**: Toda infraestrutura DEVE ser definida em Bicep ou Terraform

**Rationale**: Cloud sem controle de custos pode inviabilizar projetos. Arquitetura cost-aware desde o início evita surpresas e permite escalar de forma sustentável.

## Azure Infrastructure Standards

Diretrizes específicas para implementações Azure no projeto.

- **Naming convention**: `{project}-{env}-{resource}-{region}` (ex: `pgm-prod-func-brazilsouth`)
- **Resource Groups**: Um RG por ambiente (dev, staging, prod)
- **Região padrão**: Brazil South para compliance de dados e latência
- **Tags obrigatórias**: `environment`, `project`, `owner`, `cost-center`
- **Secrets**: Azure Key Vault obrigatório; nunca hardcoded ou em repositório
- **CI/CD**: GitHub Actions com Azure Login via OIDC (sem secrets expostos)
- **Backup**: Políticas de backup configuradas para dados críticos
- **Logs**: Application Insights para telemetria; Log Analytics para agregação

## Quality Gates

Checkpoints obrigatórios antes de merge para main/production.

1. **Lint & Format**: Zero warnings de linting, formatação automática aplicada
2. **Testes**: Todos os testes passando, cobertura ≥80% para código novo
3. **Build**: Build de produção bem-sucedido sem warnings
4. **Security Scan**: Nenhuma vulnerabilidade crítica ou alta
5. **Performance**: Nenhuma regressão em métricas de performance
6. **Documentation**: README atualizado para features públicas, CHANGELOG mantido
7. **Review**: Aprovação de pelo menos 1 reviewer

## Governance

Esta constituição é o documento supremo para decisões técnicas no projeto.

- **Precedência**: Em caso de conflito, esta constituição prevalece sobre práticas externas
- **Emendas**: Alterações requerem documentação do motivo, aprovação do tech lead, e plano de migração se necessário
- **Versionamento**: Semantic versioning (MAJOR.MINOR.PATCH) para a constituição
- **Compliance**: Todo PR DEVE verificar aderência aos princípios; violações requerem justificativa documentada
- **Exceções**: Desvios temporários permitidos apenas com issue tracking e prazo de correção

**Version**: 1.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2025-12-29
