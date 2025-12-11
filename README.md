# Atelimatch 🎨


Sistema completo de gestão para ateliês de costura com IA generativa de imagens.

## 📋 Visão Geral

O **Atelimatch** é uma plataforma web desenvolvida com Django que oferece gestão completa para ateliês de costura, incluindo:

- 📦 **Gestão de Produtos**: Catálogo completo com CRUD
- 📊 **Controle de Estoque**: Monitore quantidades e pontos de reposição
- 🛍️ **Pedidos**: Acompanhe pedidos desde a criação até a entrega
- 📈 **Dashboard**: Métricas e gráficos em tempo real
- 🗺️ **Auto-preenchimento de CEP**: Integração com ViaCEP


## 📦 Instalação e Execução

### Pré-requisitos

- Python 3.11+
- pip
- virtualenv (recomendado)

### Desenvolvimento Local

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/Atelimatch.git
cd Atelimatch
```

2. **Crie e ative o ambiente virtual**

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**

Copie o arquivo `.env.example` para `.env` e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# OpenAI (obrigatório para IA)
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...sua-chave-aqui

# Microsoft Clarity (opcional)
CLARITY_ID=seu-clarity-id-aqui
```

5. **Execute as migrações**

```bash
python manage.py migrate
```

6. **Crie um superusuário**

```bash
python manage.py createsuperuser
```

7. **Colete arquivos estáticos**

```bash
python manage.py collectstatic --noinput
```

8. **Execute o servidor**

```bash
python manage.py runserver
```

Acesse: [http://localhost:8000](http://localhost:8000)

## 🧪 Testes

Execute os testes automatizados:

```bash
python manage.py test tests
```

Ou com pytest:

```bash
pytest
```

### Cobertura de Testes

- ✅ Autenticação por e-mail
- ✅ Redirecionamento por perfil (ateliê/cliente)
- ✅ CRUD de produtos
- ✅ Cálculo automático de valor total do pedido
- ✅ Signals para atualização de pedidos

`

## 📁 Estrutura do Projeto

```
Atelimatch/
├── core/                   # Configurações do projeto
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── context_processors.py
├── usuarios/               # App de usuários e autenticação
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── admin.py
├── atelie/                 # App de gestão do ateliê
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── signals.py
│   └── admin.py
├── ia/                     # App de IA generativa
│   ├── models.py
│   ├── views.py
│   ├── services.py
│   ├── urls.py
│   ├── admin.py
│   └── providers/
│       ├── base.py
│       ├── openai_provider.py
│       └── __init__.py
├── templates/              # Templates HTML
│   ├── base.html
│   ├── home.html
│   ├── sobre.html
│   ├── 404.html
│   ├── 500.html
│   ├── usuarios/
│   ├── atelie/
│   └── ia/
├── static/                 # Arquivos estáticos
├── media/                  # Arquivos de mídia (uploads)
├── tests/                  # Testes automatizados
│   ├── test_auth.py
│   ├── test_produto.py
│   └── test_pedido.py
├── docs/                   # Documentação
│   ├── scrum.md
│   └── artigo.md
├── requirements.txt
├── .env.example
├── .gitignore
├── pytest.ini
├── manage.py
└── README.md
```



Desenvolvido com ❤️ para ateliês de costura
