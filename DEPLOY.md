# 🚀 Guia de Deploy - Atelimatch

Este guia detalha o processo completo de deploy da aplicação Atelimatch no Render (plano gratuito).

## 📋 Pré-requisitos

- Conta no [GitHub](https://github.com)
- Conta no [Render](https://render.com)
- Chave de API da [OpenAI](https://platform.openai.com/api-keys)
- (Opcional) ID do [Microsoft Clarity](https://clarity.microsoft.com/)

## 🔧 Passo 1: Preparar Repositório GitHub

### 1.1 Criar Repositório

1. Acesse [GitHub](https://github.com/new)
2. Nome do repositório: `Atelimatch`
3. Descrição: "Sistema de gestão para ateliês de costura com IA generativa"
4. Visibilidade: **Public**
5. Clique em **Create repository**

### 1.2 Fazer Push do Código

```bash
cd /caminho/para/Atelimatch
git init
git add .
git commit -m "feat: implementação inicial do Atelimatch"
git branch -M main
git remote add origin https://github.com/seu-usuario/Atelimatch.git
git push -u origin main
```

## 🗄️ Passo 2: Criar Banco de Dados PostgreSQL no Render

### 2.1 Criar Database

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Clique em **New** → **PostgreSQL**
3. Configure:
   - **Name**: `Atelimatch-db`
   - **Database**: `Atelimatch`
   - **User**: `Atelimatch_user` (gerado automaticamente)
   - **Region**: Escolha a mais próxima (ex: Ohio - US East)
   - **PostgreSQL Version**: 15
   - **Plan**: **Free**
4. Clique em **Create Database**

### 2.2 Copiar Database URL

1. Aguarde a criação do banco (1-2 minutos)
2. Na página do banco, copie a **Internal Database URL**
   - Formato: `postgresql://user:password@host:5432/dbname`
3. **Guarde essa URL** - será usada no próximo passo

## 🌐 Passo 3: Criar Web Service no Render

### 3.1 Criar Service

1. No Render Dashboard, clique em **New** → **Web Service**
2. Conecte seu repositório GitHub:
   - Clique em **Connect account** (se primeira vez)
   - Autorize o Render a acessar seus repositórios
   - Selecione o repositório `Atelimatch`
3. Clique em **Connect**

### 3.2 Configurar Service

Preencha os campos:

- **Name**: `Atelimatch` (ou outro nome único)
- **Region**: Mesma do banco de dados
- **Branch**: `main`
- **Root Directory**: (deixe em branco)
- **Runtime**: `Python 3`
- **Build Command**:
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
  ```
- **Start Command**:
  ```bash
  gunicorn core.wsgi:application
  ```
- **Plan**: **Free**

### 3.3 Configurar Variáveis de Ambiente

Role até a seção **Environment Variables** e adicione:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Gere uma chave forte [aqui](https://djecrety.ir/) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com` |
| `DATABASE_URL` | Cole a URL copiada no Passo 2.2 |
| `CSRF_TRUSTED_ORIGINS` | `https://Atelimatch.onrender.com` (substitua pelo seu domínio) |
| `AI_PROVIDER` | `openai` |
| `OPENAI_API_KEY` | Sua chave da OpenAI (ex: `sk-...`) |
| `AI_IMAGE_SIZE` | `512x512` |
| `CLARITY_ID` | Seu ID do Clarity (opcional) |

### 3.4 Deploy

1. Clique em **Create Web Service**
2. Aguarde o deploy (5-10 minutos)
3. Acompanhe os logs em tempo real

## ✅ Passo 4: Verificar Deploy

### 4.1 Acessar Aplicação

1. Após conclusão do deploy, clique no link gerado
   - Formato: `https://Atelimatch.onrender.com`
2. Você deve ver a página inicial do Atelimatch

### 4.2 Criar Superusuário

Para acessar o admin Django:

1. No Render Dashboard, vá até seu Web Service
2. Clique na aba **Shell**
3. Execute:
   ```bash
   python manage.py createsuperuser
   ```
4. Preencha:
   - Email: `admin@Atelimatch.com`
   - Password: (escolha uma senha forte)
5. Acesse: `https://seu-app.onrender.com/admin`

### 4.3 Testar Funcionalidades

- ✅ Cadastro de cliente
- ✅ Cadastro de ateliê
- ✅ Login
- ✅ Dashboard
- ✅ CRUD de produtos
- ✅ Geração de imagens com IA (requer OPENAI_API_KEY válida)

## 🔧 Passo 5: Configurações Adicionais

### 5.1 Domínio Customizado (Opcional)

1. No Render, vá em **Settings** → **Custom Domain**
2. Adicione seu domínio (ex: `www.Atelimatch.com.br`)
3. Configure DNS conforme instruções do Render
4. Atualize `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`

### 5.2 Configurar Microsoft Clarity

1. Acesse [Microsoft Clarity](https://clarity.microsoft.com/)
2. Crie um novo projeto
3. Copie o **Clarity ID**
4. No Render, adicione variável `CLARITY_ID` com o valor copiado
5. Redeploy da aplicação

### 5.3 Monitoramento

O Render oferece:
- **Logs**: Acesse pela aba "Logs"
- **Metrics**: CPU, memória, requests
- **Alerts**: Configure notificações por e-mail

## 🐛 Troubleshooting

### Erro: "Application failed to start"

**Causa**: Erro na build ou start command

**Solução**:
1. Verifique os logs no Render
2. Confirme que `requirements.txt` está correto
3. Teste localmente: `gunicorn core.wsgi:application`

### Erro: "DisallowedHost"

**Causa**: `ALLOWED_HOSTS` não configurado

**Solução**:
1. Adicione variável `ALLOWED_HOSTS=.onrender.com`
2. Redeploy

### Erro: "CSRF verification failed"

**Causa**: `CSRF_TRUSTED_ORIGINS` não configurado

**Solução**:
1. Adicione variável `CSRF_TRUSTED_ORIGINS=https://seu-app.onrender.com`
2. Redeploy

### Erro: "Database connection failed"

**Causa**: `DATABASE_URL` incorreta

**Solução**:
1. Verifique se copiou a **Internal Database URL** completa
2. Confirme que o banco está ativo no Render
3. Teste conexão via Shell

### IA não gera imagens

**Causa**: `OPENAI_API_KEY` inválida ou sem créditos

**Solução**:
1. Verifique se a chave está correta
2. Confirme que tem créditos na conta OpenAI
3. Teste a chave em [OpenAI Playground](https://platform.openai.com/playground)

## 📊 Custos

### Plano Free do Render

- **Web Service**: Gratuito (com limitações)
  - 750 horas/mês
  - Suspende após 15 minutos de inatividade
  - Reinicia automaticamente ao receber request
- **PostgreSQL**: Gratuito
  - 1 GB de armazenamento
  - Expira após 90 dias (pode renovar)

### OpenAI DALL-E 3

- **Custo**: ~$0.04 por imagem (1024x1024)
- **Estimativa**: 100 imagens = $4.00

### Total Estimado

- **Desenvolvimento/Teste**: $0 - $10/mês
- **Produção (baixo volume)**: $5 - $20/mês

## 🔄 Atualizações

Para fazer deploy de novas versões:

1. Faça commit e push das alterações:
   ```bash
   git add .
   git commit -m "feat: nova funcionalidade"
   git push origin main
   ```
2. O Render fará **auto-deploy** automaticamente
3. Acompanhe o progresso no Dashboard

## 📚 Recursos Adicionais

- [Documentação do Render](https://render.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

---

✅ **Deploy concluído com sucesso!**

Sua aplicação está rodando em: `https://seu-app.onrender.com`
