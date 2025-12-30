# Research: Controle de Numeração de Documentos

**Date**: 2025-12-29  
**Purpose**: Resolver decisões técnicas e NEEDS CLARIFICATION do Technical Context

---

## 1. Azure Tables vs SQL para Sequência Atômica

### Decisão: Azure Tables com ETag para concorrência otimista

### Rationale

Azure Tables não suporta transações ACID tradicionais, mas oferece **Entity Group Transactions** (operações batch atômicas na mesma partição) e **ETag-based optimistic concurrency**. Para o caso de geração sequencial:

1. **Leitura**: Obter entidade `Sequence` com o último número
2. **Incremento**: Calcular próximo número
3. **Escrita condicional**: Atualizar com `If-Match: ETag` - falha se outro processo atualizou
4. **Retry**: Em caso de conflito, repetir o processo

Este padrão é amplamente usado e funciona bem para volume baixo (<1000 ops/dia).

### Alternativas Consideradas

| Opção | Prós | Contras | Decisão |
|-------|------|---------|---------|
| Azure SQL Serverless | ACID nativo | Custo maior, cold start longo | ❌ |
| Cosmos DB | Transações ACID em partição | Custo por RU, complexidade | ❌ |
| Azure Tables + Retry | Simples, barato | Retry necessário | ✅ |

### Código de Referência (Python)

```python
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceModifiedError

def get_next_number(table_client: TableClient, doc_type: str, year: int) -> int:
    partition_key = f"SEQ_{doc_type}"
    row_key = str(year)
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Lê entidade atual
            entity = table_client.get_entity(partition_key, row_key)
            current_number = entity["LastNumber"]
            etag = entity.metadata["etag"]
            
            # Incrementa e atualiza com concorrência otimista
            entity["LastNumber"] = current_number + 1
            table_client.update_entity(entity, etag=etag, match_condition="IfMatch")
            
            return current_number + 1
            
        except ResourceNotFoundError:
            # Primeiro número do ano
            entity = {
                "PartitionKey": partition_key,
                "RowKey": row_key,
                "LastNumber": 1
            }
            table_client.create_entity(entity)
            return 1
            
        except ResourceModifiedError:
            # Conflito - outro processo atualizou primeiro
            if attempt == max_retries - 1:
                raise ConcurrencyError("Max retries exceeded")
            continue
```

---

## 2. Azure Function App Flex Consumption

### Decisão: Usar Flex Consumption para cold start zero e custo baixo

### Rationale

O plano **Flex Consumption** é a evolução do Consumption plan, oferecendo:

- **Cold start próximo de zero**: Instâncias "always ready" opcionais
- **Scale to zero**: Sem custos quando inativo
- **Python 3.11+**: Runtime moderno
- **Custo**: ~$0.20/milhão execuções + tempo de computação

Para o volume esperado (~1000 números/mês, ~5000 requests/mês considerando UI):
- Estimativa: **< R$ 5/mês** em execuções

### Configuração Recomendada

```json
{
  "runtime": {
    "name": "python",
    "version": "3.11"
  },
  "scaleAndConcurrency": {
    "maximumInstanceCount": 10,
    "instanceMemoryMB": 512,
    "triggers": {
      "http": {
        "perInstanceConcurrency": 16
      }
    }
  }
}
```

---

## 3. Autenticação para Static Website + Functions

### Decisão: JWT com Azure Functions + Cookie HttpOnly

### Rationale

Static websites no Storage Account não têm servidor, então a autenticação deve ser:

1. **Login endpoint** no Function App valida credenciais
2. **JWT gerado** com claims do usuário
3. **Cookie HttpOnly** para armazenar token (mais seguro que localStorage)
4. **Middleware** em cada Function valida JWT

### Alternativa Descartada

- **Azure AD B2C**: Overkill para ~20 usuários, custo adicional
- **Easy Auth (App Service)**: Não disponível para Storage Account static website

### Implementação

```python
# Biblioteca: PyJWT
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.environ["JWT_SECRET"]  # Vem do Key Vault

def create_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=8),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

---

## 4. Frontend React com Shadcn/UI

### Decisão: React SPA com Vite + Shadcn/UI, hospedado em Storage Account

### Rationale

- **Vite**: Build rápido, bundle otimizado
- **Shadcn/UI**: Componentes acessíveis, customizáveis, sem runtime pesado
- **Storage Account Static Website**: Grátis no tier Standard_LRS, CDN opcional

### Componentes Shadcn Necessários

| Componente | Uso |
|------------|-----|
| button | Ações principais |
| card | Dashboard, containers |
| dialog | Modais de confirmação e sucesso |
| form + input + label | Formulários |
| table | Histórico, listagens |
| select | Seleção de tipo documento |
| tabs | Navegação em configurações |
| toast (sonner) | Feedback de ações |
| badge | Status de usuários/tipos |
| dropdown-menu | Menu do usuário |
| skeleton | Loading states |

### Instalação

```bash
# Inicialização
npx create-vite@latest frontend --template react-ts
cd frontend
npx shadcn@latest init

# Componentes
npx shadcn@latest add button card dialog form input label table select tabs sonner badge dropdown-menu skeleton
```

---

## 5. Design de Partition Keys para Azure Tables

### Decisão: Partition por entidade lógica para distribuição e queries eficientes

### Estratégia

| Tabela | PartitionKey | RowKey | Rationale |
|--------|--------------|--------|-----------|
| Users | `USER` | `{user_id}` | Poucos usuários, query por ID |
| DocumentTypes | `DOCTYPE` | `{type_id}` | Poucos tipos, query por ID |
| Sequences | `SEQ_{type_id}` | `{year}` | Partição por tipo para lock granular |
| NumberLogs | `LOG_{year}_{month}` | `{timestamp}_{uuid}` | Partição temporal para queries de histórico |

### Justificativa NumberLogs

Para histórico, partição mensal permite:
- Query eficiente por período
- Distribuição de carga ao longo do tempo
- Potencial arquivamento futuro de partições antigas

---

## 6. CORS e Comunicação Frontend-Backend

### Decisão: CORS configurado no Function App, frontend usa fetch nativo

### Configuração

```json
// host.json
{
  "extensions": {
    "http": {
      "routePrefix": "api"
    }
  }
}

// local.settings.json e App Settings
{
  "CORS_ORIGINS": "https://controlepgm.z15.web.core.windows.net"
}
```

### Headers de Resposta

```python
def add_cors_headers(response: func.HttpResponse) -> func.HttpResponse:
    response.headers["Access-Control-Allow-Origin"] = os.environ["CORS_ORIGINS"]
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response
```

---

## 7. Estimativa de Custo Atualizada

| Recurso | SKU | Custo Estimado/mês |
|---------|-----|-------------------|
| Storage Account (Static Website) | Standard_LRS | ~R$ 5 (1GB, tráfego mínimo) |
| Storage Account (Tables) | Standard_LRS | ~R$ 1 (transações mínimas) |
| Function App | Flex Consumption | ~R$ 5 (execuções + compute) |
| Key Vault | Standard | ~R$ 1 |
| Application Insights | Basic | R$ 0 (5GB grátis) |
| **Total Estimado** | | **~R$ 12-15/mês** |

**Economia vs SQL Serverless**: ~R$ 25-30/mês (SQL Serverless custa ~R$ 30-40)

---

## 8. Dependências Python

### requirements.txt

```txt
azure-functions==1.18.0
azure-data-tables==12.5.0
azure-identity==1.15.0
azure-keyvault-secrets==4.8.0
pyjwt==2.8.0
bcrypt==4.1.2
pydantic==2.5.0
python-dateutil==2.8.2
```

### Justificativa

- **azure-data-tables**: SDK oficial para Azure Tables
- **azure-identity**: Autenticação com Managed Identity (produção)
- **pyjwt**: Geração/validação de tokens JWT
- **bcrypt**: Hash de senhas
- **pydantic**: Validação de request/response
- **python-dateutil**: Manipulação de timezone (America/Sao_Paulo)

---

## 9. Timezone e Formatação

### Decisão: Todas as operações usam America/Sao_Paulo

```python
from datetime import datetime
from zoneinfo import ZoneInfo

BRAZIL_TZ = ZoneInfo("America/Sao_Paulo")

def get_current_year() -> int:
    return datetime.now(BRAZIL_TZ).year

def format_number(number: int, year: int) -> str:
    return f"{number}/{year}"
```

### Armazenamento

- **Azure Tables**: Timestamps sempre em UTC
- **Frontend**: Converte para horário local na exibição
- **Lógica de negócio**: Usa timezone Brasília para determinar ano

---

## Sumário de Decisões

| Área | Decisão | Confiança |
|------|---------|-----------|
| Database | Azure Tables com ETag concurrency | Alta |
| Compute | Function App Flex Consumption | Alta |
| Auth | JWT em Cookie HttpOnly | Alta |
| Frontend | React + Vite + Shadcn/UI | Alta |
| Hosting Frontend | Storage Account Static Website | Alta |
| IaC | Bicep | Alta (per constitution) |
| Custo | ~R$ 15/mês (sob R$ 50 target) | Alta |
