# 📅 MeuHorário API

API REST desenvolvida com **FastAPI** para gerenciamento de agendamentos, permitindo o cadastro de clientes, profissionais e serviços, além da marcação, consulta e cancelamento de horários.

O projeto foi desenvolvido com foco em boas práticas de arquitetura, programação assíncrona, autenticação JWT, testes automatizados e conteinerização com Docker.

---

## ✨ Funcionalidades

- Cadastro de clientes
- Cadastro de profissionais (apenas administradores)
- Autenticação com JWT
- Controle de permissões por perfil (`client`, `professional`, `admin`)
- Cadastro e gerenciamento de serviços
- Criação, edição e cancelamento de agendamentos
- Consulta de horários disponíveis
- Validação automática de conflitos de agenda
- Paginação e filtros
- Documentação automática via Swagger/OpenAPI

---

# 🚀 Tecnologias

### Linguagem

- Python 3.14+

### Framework

- FastAPI

### Banco de Dados

- PostgreSQL
- SQLAlchemy 2 (Assíncrono)
- Psycopg
- Alembic

### Autenticação

- JWT
- OAuth2 Password Bearer
- PyJWT

### Segurança

- Argon2 (`pwdlib`)

### Validação

- Pydantic v2

### Infraestrutura

- Docker
- Docker Compose

### Testes

- Pytest
- Testes automatizados
- Integração Contínua (CI)

---

# 🧠 Conceitos e Habilidades Demonstradas

- Programação Assíncrona (`async`/`await`)
- Arquitetura REST
- CRUD completo
- Controle de acesso baseado em Roles (RBAC)
- OAuth2
- JWT
- Validação de regras de negócio
- SQLAlchemy ORM Assíncrono
- Alembic Migrations
- Dockerização
- Testes Automatizados
- Integração Contínua (CI)

---

# 📂 Estrutura do Projeto

```text
.
├── frontend/
├── meuhorario/
│   ├── routers/
│   │   ├── appointments.py
│   │   ├── auth.py
│   │   ├── services.py
│   │   ├── users.py
│   ├── app.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── settings.py
├── migrations/
├── tests/
├── compose.yaml
├── Dockerfile
├── entrypoint.sh
└── README.md
```

---

# 🗄️ Modelagem

## User

| Campo | Tipo | Descrição |
|---------|------|------------|
| id | int | PK |
| first_name | str | Nome |
| last_name | str | Sobrenome |
| email | str | Único |
| password | str | Hash Argon2 |
| role | enum | client • professional • admin |
| created_at | datetime | Data de criação |

---

## Service

| Campo | Tipo |
|---------|------|
| id | int |
| name | str |
| duration | int (minutos) |
| price | float |

---

## Appointment

| Campo | Tipo |
|---------|------|
| id | int |
| client_id | FK User |
| professional_id | FK User |
| service_id | FK Service |
| start_time | datetime |
| end_time | datetime |

O campo **end_time** é calculado automaticamente utilizando a duração do serviço.

---

# 🔐 Autenticação

A API utiliza OAuth2 Password Flow com JWT Bearer Token.

## Endpoints

| Método | Endpoint |
|---------|-----------|
| POST | `/auth/token` |
| POST | `/auth/refresh_token` |

O JWT possui:

- `sub = email`
- algoritmo HS256
- tempo de expiração configurável via variável de ambiente.

---

# 👤 Usuários

| Método | Endpoint | Permissão |
|---------|-----------|------------|
| POST | `/users/` | Público |
| POST | `/users/professional` | Admin |
| GET | `/users/me` | Autenticado |
| GET | `/users/{id}` | Próprio usuário ou Admin |
| GET | `/users/` | Admin |
| PUT | `/users/{id}` | Próprio usuário |
| DELETE | `/users/{id}` | Próprio usuário ou Admin |

## Regras

- Cadastro público cria apenas usuários do tipo **client**.
- Apenas administradores podem criar profissionais.
- Não existe endpoint público para criação de administradores.

---

# 🛠️ Serviços

| Método | Endpoint | Permissão |
|---------|-----------|------------|
| POST | `/services/` | Admin |
| GET | `/services/` | Público |
| GET | `/services/{id}` | Público |
| PATCH | `/services/{id}` | Admin |
| DELETE | `/services/{id}` | Admin |

---

# 📅 Agendamentos

| Método | Endpoint |
|---------|-----------|
| GET | `/appointments/selection` |
| POST | `/appointments/` |
| GET | `/appointments/` |
| GET | `/appointments/slots` |
| PATCH | `/appointments/{id}` |
| DELETE | `/appointments/{id}` |

---

## Permissões

### Cliente

- agenda apenas para si mesmo
- escolhe apenas o profissional
- visualiza somente seus agendamentos

### Profissional

- agenda apenas para si mesmo
- escolhe apenas o cliente
- visualiza somente seus atendimentos

### Administrador

- possui acesso total
- pode criar agendamentos para qualquer usuário
- visualiza todos os registros

---

# ✅ Regras de Negócio

Antes da criação ou atualização de um agendamento, a API verifica automaticamente:

- Não permite datas passadas
- Respeita o horário de funcionamento
- Impede conflitos de horário do cliente
- Impede conflitos de horário do profissional
- Calcula automaticamente o horário de término

## Horário de funcionamento

| Dia | Horário |
|------|----------|
| Segunda a Sexta | 08:00 às 18:00 |
| Sábado | 08:00 às 16:00 |
| Domingo | Fechado |

---

# 📆 Horários Disponíveis

O endpoint

```
GET /appointments/slots
```

gera automaticamente uma grade semanal dos próximos **7 dias**.

Características:

- intervalos de 15 minutos
- considera horário de funcionamento
- verifica conflitos do cliente
- verifica conflitos do profissional
- calcula disponibilidade em tempo real

---

# 🌐 CORS

Origens permitidas:

```
http://localhost:3000
http://localhost:5173
https://matheusfilipe.github.io
```

---

# ▶️ Executando o projeto

## Clone o repositório

```bash
git clone https://github.com/seu-usuario/meuhorario.git

cd meuhorario
```

---

## Docker

```bash
docker compose up --build
```

---

## Ambiente virtual e instalação

```bash
pip install --user pipx
pipx ensurepath
```

```bash
pipx install poetry
poetry install
```

---

## Banco de dados

```bash
alembic upgrade head
```

---

## Executando

```bash
fastapi dev app.py
```

ou

```bash
uvicorn app:app --reload
```

---

# 🧪 Testes

Execute os testes automatizados:

```bash
pytest
```

---

# 📖 Documentação da API

Após iniciar a aplicação:

Swagger UI

```
http://localhost:8000/docs
```

ReDoc

```
http://localhost:8000/redoc
```

---

# 📌 Objetivos do Projeto

Este projeto foi desenvolvido para demonstrar conhecimentos em:

- Desenvolvimento de APIs REST
- FastAPI
- SQLAlchemy Assíncrono
- PostgreSQL
- Docker
- Alembic
- OAuth2
- JWT
- Programação Assíncrona
- Arquitetura em Camadas
- Testes Automatizados
- Integração Contínua
- Boas práticas de desenvolvimento backend