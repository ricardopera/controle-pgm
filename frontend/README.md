# Frontend - Controle PGM

Interface web em React para o sistema de controle de numeração de documentos.

## 🛠️ Stack

- **Framework**: React 18
- **Build Tool**: Vite 5
- **Linguagem**: TypeScript 5
- **Estilos**: Tailwind CSS 3
- **Componentes**: Shadcn/UI (Radix UI)
- **Roteamento**: React Router 6
- **HTTP Client**: Fetch API nativo
- **Notificações**: Sonner

## 📁 Estrutura

```
frontend/
├── public/                 # Assets estáticos
├── src/
│   ├── components/
│   │   ├── auth/          # Componentes de autenticação
│   │   ├── features/      # Componentes de funcionalidades
│   │   ├── layout/        # Layout (Sidebar, Header)
│   │   └── ui/            # Componentes Shadcn/UI
│   ├── lib/
│   │   ├── api.ts         # Cliente HTTP
│   │   ├── auth-context.tsx # Contexto de autenticação
│   │   └── utils.ts       # Utilitários
│   ├── pages/             # Páginas da aplicação
│   ├── types/             # Tipos TypeScript
│   ├── App.tsx            # Componente principal
│   ├── main.tsx           # Entry point
│   └── index.css          # Estilos globais
├── tests/                 # Testes
├── index.html             # HTML template
├── vite.config.ts         # Configuração Vite
├── tailwind.config.js     # Configuração Tailwind
├── tsconfig.json          # Configuração TypeScript
└── package.json
```

## 🚀 Desenvolvimento Local

### Pré-requisitos

- Node.js 20+
- npm ou yarn

### Setup

```bash
# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
```

### Iniciar servidor

```bash
npm run dev
```

A aplicação estará disponível em `http://localhost:5173`.

### Build de produção

```bash
npm run build
```

Os arquivos serão gerados em `dist/`.

## 📱 Páginas

| Rota | Página | Autenticação | Permissão |
|------|--------|--------------|-----------|
| `/login` | Login | Não | - |
| `/` | Home (Geração) | Sim | Usuário |
| `/historico` | Histórico | Sim | Usuário |
| `/tipos-documento` | Tipos de Documento | Sim | Admin |
| `/usuarios` | Usuários | Sim | Admin |

## 🧩 Componentes Principais

### Features

- `NumberGenerator` - Formulário de geração de números
- `HistoryTable` - Tabela de histórico com filtros
- `DocumentTypesList` - CRUD de tipos de documento
- `UsersList` - CRUD de usuários

### Layout

- `MainLayout` - Layout principal com sidebar
- `Sidebar` - Menu lateral de navegação
- `Header` - Cabeçalho com informações do usuário

### Auth

- `ProtectedRoute` - Wrapper para rotas protegidas
- `RequireAdmin` - Wrapper para rotas admin-only

## 🔐 Autenticação

O frontend usa cookies HttpOnly para autenticação:

1. Usuário faz login em `/login`
2. API retorna JWT em cookie `auth_token`
3. Browser envia cookie automaticamente
4. `AuthContext` gerencia estado de autenticação

### AuthContext

```tsx
const { user, isAuthenticated, isAdmin, login, logout, loading } = useAuth();
```

## 🌐 API Client

O cliente HTTP em `src/lib/api.ts` provê:

```typescript
// GET request
const data = await api.get<UserResponse>('/api/auth/me');

// POST request
const result = await api.post<LoginResponse>('/api/auth/login', {
  email: 'user@example.com',
  password: 'password'
});

// PUT request
await api.put('/api/users/123', { name: 'Novo Nome' });

// DELETE request
await api.delete('/api/users/123');
```

### Tratamento de Erros

O cliente converte erros da API em exceções JavaScript:

```typescript
try {
  await api.post('/api/auth/login', credentials);
} catch (error) {
  // error.message contém a mensagem da API
  toast.error(error.message);
}
```

## 🎨 Estilos

### Tailwind CSS

Classes utilitárias são usadas diretamente nos componentes:

```tsx
<div className="flex items-center gap-4 p-4 bg-muted rounded-lg">
  ...
</div>
```

### Shadcn/UI

Componentes pré-construídos em `src/components/ui/`:

```tsx
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
```

### Tema

O tema é definido em `src/index.css` com variáveis CSS:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  /* ... */
}
```

## 🧪 Testes

```bash
# Rodar testes
npm run test

# Rodar testes com watch
npm run test:watch

# Rodar testes com cobertura
npm run test:ci
```

### Estrutura de Testes

```
tests/
├── components/       # Testes de componentes
├── pages/           # Testes de páginas
└── setup.ts         # Configuração do Vitest
```

## 📝 Scripts NPM

| Script | Descrição |
|--------|-----------|
| `dev` | Inicia servidor de desenvolvimento |
| `build` | Build de produção |
| `preview` | Preview do build |
| `lint` | Executa ESLint |
| `typecheck` | Verifica tipos TypeScript |
| `test` | Roda testes |
| `test:watch` | Testes em modo watch |
| `test:ci` | Testes para CI |

## ⚙️ Variáveis de Ambiente

| Variável | Descrição | Default |
|----------|-----------|---------|
| `VITE_API_URL` | URL base da API | `http://localhost:7071` |

### Exemplo `.env.local`

```env
VITE_API_URL=http://localhost:7071
```

### Exemplo `.env.production`

```env
VITE_API_URL=https://func-controle-pgm.azurewebsites.net
```

## 🔍 Troubleshooting

### Erro de CORS

```
Access-Control-Allow-Origin
```

Verifique se o backend está configurado com a origem correta em `CORS_ORIGINS`.

### Erro de autenticação

```
401 Unauthorized
```

O cookie pode ter expirado. Faça login novamente.

### Erro de build

```
Type error
```

Execute `npm run typecheck` para ver detalhes do erro de tipo.

## 📚 Recursos

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [Shadcn/UI](https://ui.shadcn.com)
- [React Router](https://reactrouter.com)
