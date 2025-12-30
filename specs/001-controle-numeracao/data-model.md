# Data Model: Controle de Numeração de Documentos

**Date**: 2025-12-29  
**Database**: Azure Tables (NoSQL)  
**Spec**: [spec.md](spec.md)

---

## Overview

Azure Tables é um banco de dados NoSQL key-value que usa **PartitionKey + RowKey** como chave composta. O design de partições é crítico para performance e concorrência.

---

## Tabelas

### 1. Users

Armazena servidores públicos com acesso ao sistema.

| Property | Type | Description |
|----------|------|-------------|
| **PartitionKey** | string | Fixo: `"USER"` |
| **RowKey** | string | UUID do usuário |
| Email | string | E-mail único (índice lógico) |
| Name | string | Nome completo |
| PasswordHash | string | Hash bcrypt da senha |
| Role | string | `"admin"` ou `"user"` |
| IsActive | boolean | Se o usuário pode logar |
| MustChangePassword | boolean | Força troca no próximo login |
| CreatedAt | datetime | UTC timestamp criação |
| UpdatedAt | datetime | UTC timestamp última alteração |

**Exemplo de Entidade**:
```json
{
  "PartitionKey": "USER",
  "RowKey": "550e8400-e29b-41d4-a716-446655440000",
  "Email": "maria.silva@itajai.sc.gov.br",
  "Name": "Maria Silva",
  "PasswordHash": "$2b$12$...",
  "Role": "user",
  "IsActive": true,
  "MustChangePassword": false,
  "CreatedAt": "2025-01-15T10:30:00Z",
  "UpdatedAt": "2025-01-15T10:30:00Z"
}
```

**Queries Comuns**:
- Por ID: `PartitionKey == "USER" && RowKey == {id}`
- Por Email: Scan com filtro `Email == {email}` (criar índice secundário se performance degradar)
- Listar ativos: `PartitionKey == "USER" && IsActive == true`

---

### 2. DocumentTypes

Tipos de documentos que podem ser numerados.

| Property | Type | Description |
|----------|------|-------------|
| **PartitionKey** | string | Fixo: `"DOCTYPE"` |
| **RowKey** | string | UUID do tipo |
| Name | string | Nome do tipo (ex: "Ofício") |
| Prefix | string | Prefixo opcional (ex: "OF") |
| IsActive | boolean | Se aparece para seleção |
| SortOrder | int | Ordem de exibição |
| CreatedAt | datetime | UTC timestamp criação |
| UpdatedAt | datetime | UTC timestamp última alteração |

**Exemplo de Entidade**:
```json
{
  "PartitionKey": "DOCTYPE",
  "RowKey": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "Name": "Ofício",
  "Prefix": "OF",
  "IsActive": true,
  "SortOrder": 1,
  "CreatedAt": "2025-01-01T00:00:00Z",
  "UpdatedAt": "2025-01-01T00:00:00Z"
}
```

**Seed Data**:
```json
[
  { "Name": "Comunicação Interna", "Prefix": "CI", "SortOrder": 1 },
  { "Name": "Ofício", "Prefix": "OF", "SortOrder": 2 },
  { "Name": "Despacho", "Prefix": "DESP", "SortOrder": 3 }
]
```

---

### 3. Sequences

Controle de sequência numérica por tipo e ano. **Partição crítica para concorrência**.

| Property | Type | Description |
|----------|------|-------------|
| **PartitionKey** | string | `"SEQ_{type_id}"` |
| **RowKey** | string | Ano como string (ex: `"2025"`) |
| LastNumber | int | Último número gerado |
| UpdatedAt | datetime | UTC timestamp última geração |

**Exemplo de Entidade**:
```json
{
  "PartitionKey": "SEQ_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "RowKey": "2025",
  "LastNumber": 42,
  "UpdatedAt": "2025-06-15T14:30:00Z"
}
```

**Estratégia de Partição**:
- Cada tipo de documento em partição separada
- Permite operações concorrentes em tipos diferentes
- ETag usado para concorrência otimista dentro do mesmo tipo

**Algoritmo de Geração**:
```
1. GET entidade com PartitionKey="SEQ_{type_id}", RowKey="{year}"
2. SE não existe: CREATE com LastNumber=1
3. SE existe: 
   a. Incrementar LastNumber
   b. UPDATE com If-Match: ETag
   c. SE conflito (412): RETRY do passo 1
4. RETURN novo número
```

---

### 4. NumberLogs

Registro histórico de todos os números gerados. Partição temporal.

| Property | Type | Description |
|----------|------|-------------|
| **PartitionKey** | string | `"LOG_{year}_{month}"` (ex: `"LOG_2025_06"`) |
| **RowKey** | string | `"{timestamp}_{uuid}"` para ordenação |
| DocumentTypeId | string | FK para DocumentTypes |
| DocumentTypeName | string | Nome desnormalizado para display |
| Number | int | Número gerado |
| Year | int | Ano da numeração |
| FormattedNumber | string | Número formatado (ex: "42/2025") |
| UserId | string | FK para Users |
| UserName | string | Nome desnormalizado para display |
| UserEmail | string | Email desnormalizado para auditoria |
| GeneratedAt | datetime | UTC timestamp exato da geração |
| GeneratedAtLocal | string | Timestamp em Brasília (ISO string) |

**Exemplo de Entidade**:
```json
{
  "PartitionKey": "LOG_2025_06",
  "RowKey": "2025-06-15T14:30:00.123Z_550e8400-e29b-41d4-a716-446655440001",
  "DocumentTypeId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "DocumentTypeName": "Ofício",
  "Number": 42,
  "Year": 2025,
  "FormattedNumber": "42/2025",
  "UserId": "550e8400-e29b-41d4-a716-446655440000",
  "UserName": "Maria Silva",
  "UserEmail": "maria.silva@itajai.sc.gov.br",
  "GeneratedAt": "2025-06-15T14:30:00.123Z",
  "GeneratedAtLocal": "2025-06-15T11:30:00-03:00"
}
```

**Queries Comuns**:
- Últimos N registros: Scan reverso por timestamp no RowKey
- Por período: `PartitionKey in ["LOG_2025_06", "LOG_2025_07"]`
- Por tipo: Filtro `DocumentTypeId == {id}`
- Por usuário: Filtro `UserId == {id}`

**Rationale para Desnormalização**:
- Azure Tables não suporta JOINs
- Nome/email inline evitam queries adicionais
- Histórico é imutável, não precisa atualizar

---

## Relacionamentos (Lógicos)

```
Users (1) ──────< NumberLogs (N)
    │
    └── UserId, UserName, UserEmail

DocumentTypes (1) ──────< NumberLogs (N)
    │                        │
    │                        └── DocumentTypeId, DocumentTypeName
    │
    └──────< Sequences (N por ano)
               │
               └── PartitionKey contém type_id
```

---

## Índices Secundários (se necessário)

Azure Tables não tem índices secundários nativos. Se queries por Email ficarem lentas:

**Opção 1**: Tabela de lookup `UsersByEmail`
```json
{
  "PartitionKey": "USEREMAIL",
  "RowKey": "maria.silva@itajai.sc.gov.br",
  "UserId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Opção 2**: Azure Cognitive Search (overkill para este volume)

Para v1 com ~50 usuários, scan com filtro é aceitável (~10ms).

---

## Validações por Entidade

### User
- Email: formato válido, único
- Name: 2-100 caracteres
- PasswordHash: presente se não for MustChangePassword
- Role: enum ["admin", "user"]

### DocumentType
- Name: 2-50 caracteres, único entre ativos
- Prefix: 1-10 caracteres, alfanumérico
- SortOrder: inteiro positivo

### Sequence
- LastNumber: inteiro positivo
- Year: 2020-2100 (sanidade)

### NumberLog
- Number: inteiro positivo
- Year: deve corresponder ao GeneratedAt
- Todos os campos obrigatórios

---

## Migrations / Versioning

Azure Tables é schema-less. Versionamento via:

1. **Novo campo**: Adicionar com valor default (código trata null)
2. **Remover campo**: Manter compatibilidade, não deletar registros antigos
3. **Alterar tipo**: Criar novo campo, migrar dados, depreciar antigo

**Exemplo de evolução**:
```python
# v1: FormattedNumber não existia
# v2: Adicionar FormattedNumber

def get_formatted_number(log: dict) -> str:
    # Compatibilidade com registros antigos
    if "FormattedNumber" in log:
        return log["FormattedNumber"]
    return f"{log['Number']}/{log['Year']}"
```

---

## Estimativa de Storage

| Tabela | Registros Estimados/Ano | Tamanho Médio | Total Anual |
|--------|------------------------|---------------|-------------|
| Users | 50 | 500 bytes | 25 KB |
| DocumentTypes | 10 | 300 bytes | 3 KB |
| Sequences | 30 (10 tipos × 3 anos) | 100 bytes | 3 KB |
| NumberLogs | 1,000 | 800 bytes | 800 KB |
| **Total** | | | **~1 MB/ano** |

Custo de storage: insignificante (< R$ 0.10/mês)

---

## Diagramas

### Entity-Relationship (Conceitual)

```
┌─────────────────┐       ┌─────────────────┐
│     Users       │       │  DocumentTypes  │
├─────────────────┤       ├─────────────────┤
│ PK: USER        │       │ PK: DOCTYPE     │
│ RK: {uuid}      │       │ RK: {uuid}      │
│ Email           │       │ Name            │
│ Name            │       │ Prefix          │
│ PasswordHash    │       │ IsActive        │
│ Role            │       │ SortOrder       │
│ IsActive        │       └────────┬────────┘
└────────┬────────┘                │
         │                         │
         │ UserId                  │ type_id in PK
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│   NumberLogs    │       │    Sequences    │
├─────────────────┤       ├─────────────────┤
│ PK: LOG_Y_M     │       │ PK: SEQ_{type}  │
│ RK: {ts}_{uuid} │       │ RK: {year}      │
│ DocumentTypeId  │       │ LastNumber      │
│ Number, Year    │       └─────────────────┘
│ UserId          │
└─────────────────┘
```

### Partition Strategy Visual

```
Azure Table: controle-pgm

Partitions:
├── USER                    # Todos os usuários
├── DOCTYPE                 # Todos os tipos
├── SEQ_type1              # Sequência tipo 1
├── SEQ_type2              # Sequência tipo 2
├── SEQ_type3              # Sequência tipo 3
├── LOG_2024_01            # Logs Jan/2024
├── LOG_2024_02            # Logs Fev/2024
├── ...
├── LOG_2025_06            # Logs Jun/2025
└── LOG_2025_07            # Logs Jul/2025
```
