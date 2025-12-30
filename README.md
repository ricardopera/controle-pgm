# Controle PGM - Sistema de Numeração de Documentos

Sistema para a Procuradoria-Geral do Município de Itajaí controlar a numeração sequencial de documentos de cada ano.

## 🎯 Visão Geral

O Controle PGM é uma aplicação web que permite aos servidores da Procuradoria solicitar números sequenciais para diferentes tipos de documentos (ofícios, pareceres, etc.), com garantia de unicidade e rastreabilidade.

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Frontend      │────▶│   Azure         │────▶│   Azure         │
│   (React SPA)   │     │   Functions     │     │   Tables        │
│                 │     │   (Python)      │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
    Static Web             Flex Consumption          NoSQL DB
```

### Stack Tecnológico

- **Frontend**: React 18 + TypeScript 5 + Vite 5 + Tailwind CSS + Shadcn/UI
- **Backend**: Python 3.11 + Azure Functions v4 (Flex Consumption)
- **Banco de Dados**: Azure Tables (NoSQL)
- **Hospedagem**: Azure Storage Static Website + Azure Functions
- **Região**: Brazil South

## 📁 Estrutura do Projeto

```
controle-pgm/
├── backend/                 # API em Python (Azure Functions)
│   ├── core/               # Configurações, middleware, exceções
│   ├── functions/          # Endpoints da API
│   ├── models/             # Modelos Pydantic
│   └── services/           # Lógica de negócio
├── frontend/               # SPA em React
│   ├── src/
│   │   ├── components/     # Componentes UI e features
│   │   ├── lib/            # Utilitários e contextos
│   │   └── pages/          # Páginas da aplicação
│   └── public/
├── infra/                  # Infraestrutura como código (Bicep)
└── specs/                  # Especificações e documentação
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Node.js 20+
- Azure CLI (opcional, para deploy)
- Azurite (emulador de storage local)

### Desenvolvimento Local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/pmi-itajai/controle-pgm.git
   cd controle-pgm
   ```

2. **Configure o backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure o frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Inicie o Azurite** (emulador de Azure Storage)
   ```bash
   npm install -g azurite
   azurite --silent &
   ```

5. **Inicialize os dados**
   ```bash
   cd backend
   python scripts/seed_data.py
   ```

6. **Inicie os servidores de desenvolvimento**
   
   Terminal 1 (Backend):
   ```bash
   cd backend
   func start
   ```
   
   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

7. **Acesse a aplicação**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:7071/api

### Credenciais de Teste

| Email | Senha | Perfil |
|-------|-------|--------|
| admin@pgm.itajai.sc.gov.br | Admin@123 | Administrador |
| servidor@pgm.itajai.sc.gov.br | Servidor@123 | Usuário |

## 📖 Funcionalidades

### Para Usuários

- ✅ **Login seguro** com JWT em cookie HttpOnly
- ✅ **Solicitar números** para documentos com confirmação
- ✅ **Visualizar histórico** de números gerados com filtros
- ✅ **Exportar para CSV** o histórico de numeração

### Para Administradores

- ✅ **Gerenciar tipos de documento** (criar, editar, desativar)
- ✅ **Gerenciar usuários** (criar, editar, desativar, resetar senha)
- ✅ **Visualizar auditoria** completa de ações

### Sistema

- ✅ **Reinício anual automático** de sequências
- ✅ **Concorrência segura** com ETag (optimistic locking)
- ✅ **Timezone Brasil** (America/Sao_Paulo)

## 🔒 Segurança

- Autenticação via JWT com expiração de 8 horas
- Cookies HttpOnly para proteção contra XSS
- Senhas hasheadas com bcrypt (cost factor 12)
- CORS configurado por ambiente
- Rotas administrativas protegidas por role

## 🧪 Testes

```bash
# Backend
cd backend
python -m pytest tests/ -v

# Frontend
cd frontend
npm run test
```

## 📦 Deploy

O deploy é automatizado via GitHub Actions:

1. **Push para `main`** dispara os workflows
2. **Backend** é deployado para Azure Functions
3. **Frontend** é deployado para Azure Storage Static Website
4. **Infra** é provisionada via Bicep

### Configuração de Secrets

Configure os seguintes secrets no GitHub:

- `AZURE_CREDENTIALS`: Service principal com acesso ao Resource Group

Configure as seguintes variáveis:

- `VITE_API_URL`: URL da API em produção
- `STORAGE_ACCOUNT_NAME`: Nome do Storage Account

## 📚 Documentação Adicional

- [Backend API](backend/README.md)
- [Frontend](frontend/README.md)
- [Infraestrutura](infra/README.md)
- [Especificação Técnica](specs/001-controle-numeracao/)

## 📝 Licença

Projeto interno da Procuradoria-Geral do Município de Itajaí.

## 🤝 Contribuição

Este é um projeto interno. Para contribuições, entre em contato com a equipe de TI da PGM.
