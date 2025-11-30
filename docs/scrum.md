# Metodologia Ágil SCRUM - Atelimatch

## 📋 Visão do Produto

O **Atelimatch** é uma plataforma web que revoluciona a gestão de ateliês de costura ao integrar ferramentas profissionais de gestão com inteligência artificial generativa, permitindo que pequenos e médios ateliês possam competir com grandes empresas do setor.

### Objetivo

Democratizar o acesso a ferramentas profissionais de gestão e criação para ateliês de costura, aumentando a produtividade e criatividade dos profissionais da área.

## 👥 Personas

### Persona 1: Maria - Costureira e Proprietária de Ateliê

- **Idade**: 45 anos
- **Experiência**: 20 anos de costura, 5 anos com ateliê próprio
- **Dores**: Dificuldade em controlar estoque, perda de pedidos, falta de ideias criativas
- **Objetivos**: Organizar melhor o negócio, aumentar vendas, criar peças inovadoras
- **Tecnologia**: Usa smartphone, conhecimento básico de computador

### Persona 2: João - Cliente de Ateliê

- **Idade**: 28 anos
- **Perfil**: Profissional liberal que valoriza peças exclusivas
- **Dores**: Dificuldade em encontrar ateliês confiáveis, falta de acompanhamento de pedidos
- **Objetivos**: Encomendar peças personalizadas, acompanhar status do pedido
- **Tecnologia**: Usuário avançado de tecnologia

### Persona 3: Ana - Gerente de Ateliê

- **Idade**: 35 anos
- **Perfil**: Administradora contratada para gerir ateliê de médio porte
- **Dores**: Controle manual de estoque, dificuldade em gerar relatórios
- **Objetivos**: Automatizar processos, ter visão geral do negócio, reduzir custos
- **Tecnologia**: Experiência com sistemas de gestão

## 📝 Backlog do Produto

### Must Have (Essencial)

| ID | User Story | Critério de Aceite | Prioridade |
|----|------------|---------------------|------------|
| US01 | Como ateliê, quero cadastrar produtos para gerenciar meu catálogo | - CRUD completo de produtos<br>- Validação de campos obrigatórios<br>- Lista paginada | Must |
| US02 | Como ateliê, quero controlar estoque para evitar rupturas | - Cadastro de itens de estoque<br>- Alerta de baixo estoque<br>- Atualização de quantidades | Must |
| US03 | Como ateliê, quero gerenciar pedidos para organizar produção | - Criar pedidos com itens<br>- Atualizar status<br>- Cálculo automático de valor total | Must |
| US04 | Como usuário, quero fazer login por e-mail para acessar o sistema | - Login com e-mail e senha<br>- Redirecionamento por perfil<br>- Logout funcional | Must |
| US05 | Como ateliê, quero visualizar dashboard com métricas para acompanhar negócio | - Cards com métricas principais<br>- Gráfico de pedidos<br>- Atualização em tempo real | Must |

### Should Have (Importante)

| ID | User Story | Critério de Aceite | Prioridade |
|----|------------|---------------------|------------|
| US06 | Como ateliê, quero gerar ideias de looks com IA para inspirar clientes | - Campo de prompt<br>- Geração de imagem com DALL-E<br>- Histórico de gerações | Should |
| US07 | Como cliente, quero acompanhar meus pedidos para saber o status | - Lista de pedidos do cliente<br>- Visualização de detalhes<br>- Status atualizado | Should |
| US08 | Como usuário, quero auto-preenchimento de CEP para facilitar cadastro | - Integração com ViaCEP<br>- Preenchimento automático de endereço<br>- Tratamento de erros | Should |

### Could Have (Desejável)

| ID | User Story | Critério de Aceite | Prioridade |
|----|------------|---------------------|------------|
| US09 | Como ateliê, quero geolocalização para aparecer em buscas locais | - Campos de latitude/longitude<br>- Integração com mapas (futuro) | Could |
| US10 | Como usuário, quero interface responsiva para usar em qualquer dispositivo | - Layout mobile-first<br>- Testes em diferentes resoluções | Could |

### Won't Have (Não será feito agora)

| ID | User Story | Prioridade |
|----|------------|------------|
| US11 | Como cliente, quero fazer pagamento online | Won't |
| US12 | Como ateliê, quero enviar notificações por WhatsApp | Won't |

## 🏃 Sprints

### Sprint 1: Fundação e Autenticação (1 semana)

**Objetivo**: Estabelecer base do projeto e sistema de autenticação

**Backlog da Sprint**:
- US04: Login por e-mail
- Configuração inicial do Django
- Modelos de usuário customizados
- Templates base

**Definição de Pronto (DoD)**:
- ✅ Código commitado no GitHub
- ✅ Testes passando
- ✅ Login funcionando com redirecionamento
- ✅ Documentação atualizada

**Resultado**: ✅ Concluído

---

### Sprint 2: CRUD e Gestão Básica (1 semana)

**Objetivo**: Implementar funcionalidades de gestão de produtos e estoque

**Backlog da Sprint**:
- US01: CRUD de produtos
- US02: Controle de estoque
- Templates de listagem e formulários

**Definição de Pronto (DoD)**:
- ✅ CRUD completo funcionando
- ✅ Validações implementadas
- ✅ Testes de CRUD passando
- ✅ Interface responsiva

**Resultado**: ✅ Concluído

---

### Sprint 3: Pedidos e Dashboard (1 semana)

**Objetivo**: Implementar gestão de pedidos e dashboard com métricas

**Backlog da Sprint**:
- US03: Gestão de pedidos
- US05: Dashboard com métricas
- Signals para cálculo automático
- Gráficos com Chart.js

**Definição de Pronto (DoD)**:
- ✅ Pedidos criados e listados
- ✅ Valor total calculado automaticamente
- ✅ Dashboard com métricas funcionando
- ✅ Gráficos renderizando

**Resultado**: ✅ Concluído

---

### Sprint 4: IA e Integrações (1 semana)

**Objetivo**: Integrar IA generativa e APIs externas

**Backlog da Sprint**:
- US06: Studio IA com DALL-E
- US08: Auto-preenchimento de CEP
- US07: Dashboard do cliente
- Integração com OpenAI
- Integração com ViaCEP

**Definição de Pronto (DoD)**:
- ✅ IA gerando imagens
- ✅ Histórico de gerações
- ✅ CEP auto-preenchendo
- ✅ Cliente visualizando pedidos
- ✅ Tratamento de erros

**Resultado**: ✅ Concluído

---

### Sprint 5: Deploy e Finalização (1 semana)

**Objetivo**: Deploy em produção e documentação final

**Backlog da Sprint**:
- Deploy no Render
- Configuração de PostgreSQL
- Documentação completa
- Testes finais
- Ajustes de segurança

**Definição de Pronto (DoD)**:
- ✅ Aplicação rodando em produção
- ✅ Banco de dados na nuvem
- ✅ README completo
- ✅ Todos os testes passando
- ✅ Variáveis de ambiente configuradas

**Resultado**: ✅ Concluído

## 📊 Quadro Kanban

**Link para GitHub Projects**: [https://github.com/seu-usuario/Atelimatch/projects/1](https://github.com/seu-usuario/Atelimatch/projects/1)

### Estrutura do Quadro

| To Do | Doing | Review | Done |
|-------|-------|--------|------|
| Novas funcionalidades | Em desenvolvimento | Em revisão | Concluídas |

## 📅 Cerimônias SCRUM

### Planning (Início de cada Sprint)

**Objetivo**: Planejar o trabalho da sprint

**Participantes**: Product Owner, Scrum Master, Time de Desenvolvimento

**Duração**: 2 horas

**Atividades**:
1. Revisar backlog do produto
2. Selecionar user stories para a sprint
3. Estimar esforço (Planning Poker)
4. Definir objetivo da sprint
5. Criar tarefas técnicas

**Template de Ata**:
```
Sprint Planning - Sprint X
Data: DD/MM/YYYY
Participantes: [nomes]

Objetivo da Sprint: [objetivo]

User Stories Selecionadas:
- US01: [descrição] - Estimativa: X pontos
- US02: [descrição] - Estimativa: Y pontos

Tarefas Técnicas:
- [ ] Tarefa 1
- [ ] Tarefa 2

Observações: [observações]
```

---

### Daily Standup (Diário)

**Objetivo**: Sincronizar o time e identificar impedimentos

**Participantes**: Time de Desenvolvimento, Scrum Master

**Duração**: 15 minutos

**Perguntas**:
1. O que fiz ontem?
2. O que farei hoje?
3. Há algum impedimento?

---

### Review (Fim de cada Sprint)

**Objetivo**: Demonstrar o trabalho concluído

**Participantes**: Product Owner, Scrum Master, Time, Stakeholders

**Duração**: 1 hora

**Atividades**:
1. Demonstração das funcionalidades
2. Feedback dos stakeholders
3. Atualização do backlog

**Template de Ata**:
```
Sprint Review - Sprint X
Data: DD/MM/YYYY
Participantes: [nomes]

Funcionalidades Demonstradas:
- US01: [descrição] - Status: ✅ Aprovado
- US02: [descrição] - Status: ⏳ Ajustes necessários

Feedback:
- [feedback 1]
- [feedback 2]

Próximos Passos:
- [ação 1]
- [ação 2]
```

---

### Retrospective (Fim de cada Sprint)

**Objetivo**: Melhorar o processo

**Participantes**: Scrum Master, Time de Desenvolvimento

**Duração**: 1 hora

**Formato**: Start/Stop/Continue

**Template de Ata**:
```
Sprint Retrospective - Sprint X
Data: DD/MM/YYYY
Participantes: [nomes]

Start (Começar a fazer):
- [item 1]
- [item 2]

Stop (Parar de fazer):
- [item 1]
- [item 2]

Continue (Continuar fazendo):
- [item 1]
- [item 2]

Ações de Melhoria:
- [ ] Ação 1 - Responsável: [nome]
- [ ] Ação 2 - Responsável: [nome]
```

## 📈 Métricas

### Velocity

- Sprint 1: 13 pontos
- Sprint 2: 21 pontos
- Sprint 3: 18 pontos
- Sprint 4: 16 pontos
- Sprint 5: 8 pontos

**Média**: 15.2 pontos por sprint

### Burndown Chart

*(Gráfico seria inserido aqui mostrando progresso diário da sprint)*

## 🎯 Definição de Pronto (DoD) Global

Uma funcionalidade é considerada "pronta" quando:

- ✅ Código implementado e funcionando
- ✅ Testes automatizados criados e passando
- ✅ Code review aprovado
- ✅ Documentação atualizada
- ✅ Commitado no GitHub com mensagem adequada
- ✅ Deploy em ambiente de desenvolvimento bem-sucedido
- ✅ Aceito pelo Product Owner

## 📚 Referências

- [Scrum Guide](https://scrumguides.org/)
- [Agile Manifesto](https://agilemanifesto.org/)
- [User Story Mapping](https://www.jpattonassociates.com/user-story-mapping/)
