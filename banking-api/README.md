# Banking API

API REST para gerenciamento de agências bancárias, construída com **FastAPI**, **SQLAlchemy** e **MySQL**. Projetada para ser usada como projeto de exemplo em pipelines Jenkins com análise de qualidade via SonarQube e publicação de imagens no Docker Hub.

---

## Sumário

- [Pré-requisitos](#pré-requisitos)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Variáveis de Ambiente](#variáveis-de-ambiente)
- [Como Subir o Ambiente](#como-subir-o-ambiente)
- [Endpoints da API](#endpoints-da-api)
- [Como Rodar os Testes](#como-rodar-os-testes)
- [Pipeline Jenkins](#pipeline-jenkins)
- [SonarQube](#sonarqube)
- [Docker Hub](#docker-hub)

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/install/) v2+
- Python 3.12+ (apenas para desenvolvimento local sem Docker)

---

## Estrutura do Projeto

```
banking-api/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Ponto de entrada FastAPI
│   ├── database.py              # Configuração SQLAlchemy + get_db
│   ├── models/
│   │   └── agencia.py           # Model ORM Agencia
│   ├── schemas/
│   │   └── agencia.py           # Schemas Pydantic (Create, Update, Response)
│   └── routers/
│       └── agencias.py          # Endpoints CRUD /agencias
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures: client, db_session, agencia_data
│   └── test_agencias.py        # 10 testes (4 smoke + 6 regression)
├── Dockerfile
├── docker-compose.yml           # Ambiente dev: app + mysql
├── requirements.txt
├── pytest.ini
├── .flake8
├── sonar-project.properties
├── Jenkinsfile                  # Pipeline declarativa 9 stages
└── README.md
```

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DATABASE_URL` | `mysql+pymysql://banking:banking@localhost:3308/banking_db` | URL de conexão com o banco MySQL |

> **Atenção:** o arquivo `.env` **não é versionado** (está no `.gitignore`). Copie o `.env.example`, renomeie para `.env` e preencha com os seus valores antes de subir o ambiente.
> Em pipelines de CI/CD, as credenciais devem ser gerenciadas via secrets (Jenkins Credentials, GitHub Actions Secrets, HashiCorp Vault) — nunca em arquivos commitados.

---

## Como Subir o Ambiente

### Ambiente completo (Jenkins + MySQL + SonarQube)

A partir da raiz do repositório (onde está o `docker-compose.yml` principal):

```bash
docker-compose up -d
```

Serviços disponíveis:

| Serviço | URL |
|---------|-----|
| Jenkins | http://localhost:9090 |
| MySQL | localhost:3308 |
| SonarQube | http://localhost:9000 |

### Apenas a API (desenvolvimento local)

```bash
cd banking-api
docker-compose up -d
```

A API ficará disponível em **http://localhost:8000**.  
Documentação interativa: **http://localhost:8000/docs**

---

## Endpoints da API

### Base URL: `http://localhost:8000`

#### Listar todas as agências
```http
GET /agencias
```
```bash
curl http://localhost:8000/agencias
```

#### Buscar agência por ID
```http
GET /agencias/{id}
```
```bash
curl http://localhost:8000/agencias/1
```

#### Criar agência
```http
POST /agencias
Content-Type: application/json
```
```bash
curl -X POST http://localhost:8000/agencias \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Agência Central",
    "codigo": "AG001",
    "endereco": "Rua das Flores, 100",
    "cidade": "São Paulo",
    "estado": "SP",
    "telefone": "11999999999"
  }'
```
Retorna `201 Created`.

#### Atualizar agência (parcial)
```http
PUT /agencias/{id}
Content-Type: application/json
```
```bash
curl -X PUT http://localhost:8000/agencias/1 \
  -H "Content-Type: application/json" \
  -d '{"nome": "Agência Central Atualizada", "telefone": "11888888888"}'
```

#### Remover agência
```http
DELETE /agencias/{id}
```
```bash
curl -X DELETE http://localhost:8000/agencias/1
```
Retorna `204 No Content`.

---

## Como Rodar os Testes

### Instalação local

```bash
cd banking-api
python3 -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

### Rodar todos os testes

```bash
pytest
```

### Rodar apenas Smoke Tests (todo build)

```bash
pytest -m smoke
```

### Rodar Smoke + Regression (PRs e schedule diário)

```bash
pytest -m "smoke or regression"
```

### Ver relatório de cobertura

Após executar `pytest`, o arquivo `coverage.xml` é gerado na raiz de `banking-api/`.  
Para ver no terminal:

```bash
pytest --cov=app --cov-report=term-missing
```

### Rodar linter

```bash
flake8 app/
```

---

## Pipeline Jenkins

### Pré-requisitos no Jenkins

1. Plugin **SonarQube Scanner** instalado
2. Plugin **Docker Pipeline** instalado
3. Credencial `dockerhub-credentials` (Username/Password) cadastrada no Jenkins  
   → *Manage Jenkins → Credentials → System → Global credentials*
4. SonarQube configurado em *Manage Jenkins → Configure System → SonarQube servers* com nome `SonarQube`
5. SonarScanner configurado em *Manage Jenkins → Global Tool Configuration* com nome `SonarScanner`

### Stages da Pipeline

| # | Stage | Condição |
|---|-------|----------|
| 1 | Checkout | Sempre |
| 2 | Install | Sempre |
| 3 | Lint | Sempre |
| 4 | Smoke Tests | Sempre |
| 5 | Regression Tests | Apenas `main`, PR para `main` ou schedule diário |
| 6 | SonarQube Analysis | Sempre |
| 7 | Docker Build | Sempre |
| 8 | Docker Push | Sempre |
| 9 | Deploy | Sempre |

### Configurar o schedule diário (Regression)

No Jenkins, na configuração do job, em **Build Triggers → Build periodically**:

```
H 2 * * *
```
Executa diariamente às 2h da manhã.

### Configurar Docker Hub username

Edite o `Jenkinsfile` e substitua o valor de `DOCKERHUB_IMAGE`:

```groovy
environment {
    DOCKERHUB_IMAGE = "seu-dockerhub-user/banking-api"  // <- altere aqui
}
```

---

## SonarQube

Acesse **http://localhost:9000** (usuário padrão: `admin` / senha: `admin`).

Após a primeira execução da pipeline, o projeto `banking-api` aparecerá no dashboard com:
- Cobertura de testes (gerada pelo `pytest --cov`)
- Métricas de qualidade de código
- Análise de bugs, vulnerabilidades e code smells

---

## Docker Hub

A pipeline publica automaticamente duas tags a cada build bem-sucedido:

- `seu-dockerhub-user/banking-api:{BUILD_NUMBER}` — versão imutável do build
- `seu-dockerhub-user/banking-api:latest` — sempre aponta para o último build

Para puxar manualmente:

```bash
docker pull seu-dockerhub-user/banking-api:latest
```
