# 🤖 Bot de Onboarding da The100s

Bot de onboarding automático com Inteligência Artificial para a **The100s**, desenvolvido com [Rasa](https://rasa.com/) (open-source) e integração com **Microsoft Teams**.

---

## 📋 Índice

1. [Descrição do Projeto](#-descrição-do-projeto)
2. [Arquitetura do Sistema](#-arquitetura-do-sistema)
3. [Pré-requisitos](#-pré-requisitos)
4. [Instalação](#-instalação)
5. [Configuração do Azure Bot](#-configuração-do-azure-bot)
6. [Correr Localmente com ngrok](#-correr-localmente-com-ngrok)
7. [Testar no Microsoft Teams](#-testar-no-microsoft-teams)
8. [Estrutura do Projeto](#-estrutura-do-projeto)
9. [Como Contribuir](#-como-contribuir)
10. [Próximos Passos](#-próximos-passos)

---

## 📖 Descrição do Projeto

O **Bot de Onboarding da The100s** é um assistente virtual inteligente que automatiza e melhora o processo de integração de novos colaboradores. O bot responde em **Português de Portugal** e guia os novos colaboradores através de todas as etapas do onboarding.

### Funcionalidades Principais

- 👋 **Boas-vindas personalizadas** — Saúda o novo colaborador pelo nome
- 🏢 **Informações da empresa** — Missão, visão, valores e cultura da The100s
- 🎁 **Benefícios** — Informações sobre seguro de saúde, férias, subsídios, etc.
- 📄 **Documentos** — Links para manual do colaborador, código de conduta, contratos
- 🎬 **Vídeo de boas-vindas** — Acesso ao vídeo institucional de boas-vindas
- 📝 **Quiz de conhecimento** — Teste de conhecimento sobre a empresa
- 📅 **Agendamento de reuniões** — Integração com Microsoft Calendar (via Graph API)
- 🖥️ **Suporte TI** — Informações e contactos de helpdesk
- 👥 **Apresentação da equipa** — Diretório e organigrama da empresa
- ❓ **FAQ** — Perguntas frequentes sobre o início de funções
- 💬 **Feedback** — Recolha de feedback sobre o processo de onboarding
- 👤 **Escalamento humano** — Direcionamento para equipa de RH

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────┐
│                  Microsoft Teams                     │
│            (Canal de comunicação principal)          │
└───────────────────────┬─────────────────────────────┘
                        │ Bot Framework Connector
                        ▼
┌─────────────────────────────────────────────────────┐
│                  Rasa Server (porta 5005)            │
│  ┌─────────────────┐  ┌─────────────────────────┐   │
│  │   Rasa NLU      │  │     Rasa Core           │   │
│  │  (spaCy pt)     │  │  (Dialogue Management)  │   │
│  │  - DIETClassif. │  │  - MemoizationPolicy    │   │
│  │  - EntityMapper │  │  - RulePolicy           │   │
│  │  - FallbackCls. │  │  - TEDPolicy            │   │
│  └─────────────────┘  └─────────────────────────┘   │
└───────────────────────┬─────────────────────────────┘
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
┌─────────────────────┐  ┌────────────────────────┐
│  Action Server      │  │  PostgreSQL             │
│  (porta 5055)       │  │  (Tracker Store)        │
│  - Custom Actions   │  │  - Histórico de conv.   │
│  - Graph API calls  │  │  - Estado dos slots     │
└─────────────────────┘  └────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────┐
│              Microsoft 365 (via Graph API)           │
│         Outlook Calendar  |  Outlook Email           │
└─────────────────────────────────────────────────────┘
```

### Stack Tecnológica

| Componente | Tecnologia |
|---|---|
| Bot Framework | Rasa 3.x (open-source) |
| Linguagem | Python 3.10 |
| Canal Principal | Microsoft Teams |
| NLU | spaCy (`pt_core_news_md`) + DIETClassifier |
| Email/Calendário | Microsoft Graph API |
| Base de Dados | PostgreSQL (tracker store) |
| Containerização | Docker + Docker Compose |

---

## 🛠️ Pré-requisitos

Antes de começar, certifique-se de que tem instalado:

- **Python 3.10** — [Download](https://www.python.org/downloads/)
- **Docker** e **Docker Compose** — [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Git** — [Download](https://git-scm.com/)
- **ngrok** (para testes locais com Teams) — [Download](https://ngrok.com/download)
- **Conta Azure** com permissões para criar Bot Services — [Portal Azure](https://portal.azure.com)

---

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/PedroGGomess/onboarding-bot.git
cd onboarding-bot
```

### 2. Configurar Variáveis de Ambiente

```bash
cp .env.example .env
```

Edite o ficheiro `.env` com as suas credenciais:

```env
MICROSOFT_APP_ID=<o-seu-app-id>
MICROSOFT_APP_PASSWORD=<a-sua-app-password>
DB_HOST=localhost
DB_PORT=5432
DB_NAME=onboarding_bot
DB_USER=postgres
DB_PASSWORD=postgres
AZURE_TENANT_ID=<o-seu-tenant-id>
AZURE_CLIENT_ID=<o-seu-client-id>
AZURE_CLIENT_SECRET=<o-seu-client-secret>
```

### 3. Instalação Local (sem Docker)

#### a) Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### b) Instalar dependências

```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_md
```

#### c) Treinar o modelo Rasa

```bash
rasa train
```

#### d) Iniciar o Action Server

```bash
# Terminal 1
rasa run actions --port 5055
```

#### e) Iniciar o Rasa Server

```bash
# Terminal 2
rasa run --enable-api --cors "*" --credentials credentials.yml --endpoints endpoints.yml
```

### 4. Instalação com Docker Compose

```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Treinar o modelo (primeira vez)
docker-compose exec rasa-server rasa train

# Verificar logs
docker-compose logs -f
```

### 5. Testar o Bot Localmente

```bash
# Interface de linha de comandos interativa
rasa shell

# Testar via API REST
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{"sender": "teste", "message": "olá"}'
```

---

## ☁️ Configuração do Azure Bot

### 1. Criar um Azure Bot Service

1. Aceda ao [Portal Azure](https://portal.azure.com)
2. Clique em **"Criar um recurso"** → pesquise **"Azure Bot"**
3. Preencha os campos:
   - **Nome do bot:** `the100s-onboarding-bot`
   - **Subscrição:** Selecione a sua subscrição
   - **Grupo de recursos:** Crie ou selecione um existente
   - **Plano de preços:** F0 (gratuito para desenvolvimento)
   - **Microsoft App ID:** Selecione "Criar novo Microsoft App ID"
4. Clique em **"Rever + criar"** → **"Criar"**

### 2. Configurar as Credenciais

Após a criação:

1. Aceda ao bot criado → **"Configuração"**
2. Copie o **Microsoft App ID** para o `.env`
3. Clique em **"Gerir"** ao lado do App ID
4. Aceda a **"Certificados e segredos"** → **"Novo segredo do cliente"**
5. Copie o valor do segredo para `MICROSOFT_APP_PASSWORD` no `.env`

### 3. Configurar o Messaging Endpoint

1. No Azure Bot → **"Configuração"**
2. Em **"Messaging endpoint"**, insira:
   ```
   https://<seu-domínio>/webhooks/botframework/webhook
   ```
   (use o URL do ngrok para testes locais)
3. Clique em **"Guardar"**

---

## 🌐 Correr Localmente com ngrok

O ngrok cria um túnel seguro do internet para a sua máquina local, permitindo que o Microsoft Teams comunique com o bot.

### 1. Instalar e Configurar ngrok

```bash
# Após download, autenticar (obtenha o token em https://dashboard.ngrok.com)
ngrok authtoken <o-seu-token>
```

### 2. Iniciar o Túnel

```bash
# Expõe a porta 5005 do Rasa Server
ngrok http 5005
```

O ngrok fornecerá um URL similar a:
```
https://abc123.ngrok.io
```

### 3. Atualizar o Messaging Endpoint

No Azure Bot → **Configuração**, atualize o endpoint para:
```
https://abc123.ngrok.io/webhooks/botframework/webhook
```

### 4. Iniciar o Bot

```bash
# Terminal 1: Action Server
rasa run actions --port 5055

# Terminal 2: Rasa Server
rasa run --enable-api --cors "*" \
  --credentials credentials.yml \
  --endpoints endpoints.yml
```

---

## 💬 Testar no Microsoft Teams

### 1. Adicionar o Canal Teams

1. No Azure Bot → **"Canais"**
2. Clique em **"Microsoft Teams"**
3. Aceite os termos e clique em **"Guardar"**

### 2. Testar no Teams

1. Clique em **"Testar no Microsoft Teams"** no Azure Portal
2. O Teams abrirá com uma conversa com o bot
3. Envie uma mensagem para testar: `olá`

### 3. Publicar para uma Equipa (Opcional)

Para disponibilizar o bot a toda a equipa:

1. No Teams → **"Aplicações"** → **"Gerir as suas aplicações"**
2. Selecione **"Submeter uma aplicação"**
3. Siga as instruções para criar o manifesto da aplicação Teams

---

## 📁 Estrutura do Projeto

```
onboarding-bot/
├── 📄 config.yml              # Pipeline NLU (spaCy + DIETClassifier)
├── 📄 domain.yml              # Intents, slots, responses, actions
├── 📄 credentials.yml         # Credenciais dos canais (Bot Framework)
├── 📄 endpoints.yml           # Action server + tracker store
├── 📄 Dockerfile              # Container do Rasa Server
├── 📄 docker-compose.yml      # Orquestração de todos os serviços
├── 📄 requirements.txt        # Dependências Python
├── 📄 .env.example            # Exemplo de variáveis de ambiente
├── 📄 .gitignore              # Ficheiros ignorados pelo Git
├── 📁 data/
│   ├── 📄 nlu.yml             # Dados de treino NLU (português)
│   ├── 📄 stories.yml         # Histórias de conversação
│   └── 📄 rules.yml           # Regras determinísticas
├── 📁 actions/
│   ├── 📄 __init__.py         # Init do módulo
│   ├── 📄 actions.py          # Custom actions Python
│   ├── 📄 Dockerfile          # Container do Action Server
│   └── 📄 requirements.txt    # Dependências do action server
├── 📁 models/                 # Modelos treinados (ignorado pelo Git)
└── 📁 tests/
    └── 📄 test_actions.py     # Testes unitários das actions
```

---

## 🤝 Como Contribuir

1. **Fork** o repositório
2. Crie uma **branch** para a sua funcionalidade:
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```
3. **Commit** as suas alterações:
   ```bash
   git commit -m "feat: adicionar nova funcionalidade de X"
   ```
4. **Push** para a branch:
   ```bash
   git push origin feature/nova-funcionalidade
   ```
5. Abra um **Pull Request**

### Convenções de Commit

Utilizamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — Nova funcionalidade
- `fix:` — Correção de bug
- `docs:` — Documentação
- `refactor:` — Refatorização
- `test:` — Testes

---

## 🔮 Próximos Passos

### Fase 2 — Integrações
- [ ] 📧 Integração completa com Microsoft Graph API (envio de emails automáticos)
- [ ] 📅 Agendamento automático de reuniões via Outlook Calendar
- [ ] 👤 Sincronização com Azure AD para dados do colaborador

### Fase 3 — Melhorias NLU
- [ ] 🧠 Adicionar mais dados de treino para melhorar a precisão
- [ ] 🔄 Pipeline de atualização contínua do modelo
- [ ] 📊 Dashboard de analytics de conversas

### Fase 4 — Funcionalidades Avançadas
- [ ] 🔔 Notificações proativas (check-ins automáticos)
- [ ] 📋 Formulários dinâmicos para recolha de dados
- [ ] 🌐 Suporte multi-idioma (inglês)
- [ ] 📱 Integração com aplicação móvel

### Fase 5 — Produção
- [ ] 🔒 Implementação de autenticação SSO
- [ ] 📈 Monitorização e alertas com Azure Monitor
- [ ] 🚀 CI/CD pipeline com GitHub Actions
- [ ] ♻️ Infraestrutura como código (Terraform)

---

## 📜 Licença

Este projeto é propriedade da **The100s**. Todos os direitos reservados.

---

## 📞 Contacto

Para questões sobre este projeto, contacte a equipa de IT da The100s:
- 📧 Email: it@the100s.com
- 💬 Teams: Equipa de IT
