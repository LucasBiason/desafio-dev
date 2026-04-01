# System Context

## Visão Geral

Sistema web para importação e visualização de transações financeiras no formato CNAB (Centro Nacional de Automação Bancária). O sistema permite upload de arquivos CNAB, parsing e normalização dos dados, armazenamento em banco relacional e exibição das transações agrupadas por loja com totalizador de saldo.

## Stakeholders

| Stakeholder | Papel | Interesse |
|-------------|-------|-----------|
| Avaliador Bycoders | Avaliador técnico | Qualidade do código, testes, arquitetura |
| Operador | Usuário final | Upload e visualização de transações |

## Contexto do Sistema

```mermaid
flowchart LR
  subgraph User["Usuário"]
    OP[Operador]
  end

  subgraph Frontend
    FE["React + Nginx\n(porta 7000)"]
  end

  subgraph Backend["Microsserviços"]
    US["user-service\n(Django + JWT)\n(porta 7001)"]
    CS["cnab-service\n(FastAPI)\n(porta 7002)"]
  end

  subgraph Processing["Processamento"]
    UP["Upload CNAB"]
    PA["Parser + Normalizador"]
  end

  subgraph Data["Dados"]
    PG[("PostgreSQL 16")]
    RD[("Redis 7")]
  end

  OP --> FE
  FE -->|"/api/user/*"| US
  FE -->|"/api/cnab/*"| CS
  CS --> UP --> PA --> PG
  CS -->|"valida token"| US
  US --> PG
  CS --> RD
```

## Restrições

- Ambiente Unix (Linux/macOS)
- Apenas linguagens e bibliotecas livres/gratuitas
- Banco relacional: PostgreSQL
- Docker Compose para orquestração
- Git com commits atômicos e bem descritos

## Decisões de Stack

| Camada | Tecnologia | Justificativa |
|--------|-----------|---------------|
| Auth Service | Django 5 + DRF + PyJWT | Autenticação e gestão de usuários |
| CNAB Service | FastAPI + SQLAlchemy + Pydantic V2 | Processamento de arquivos CNAB |
| Shared Library | cnab-shared | Código compartilhado entre microsserviços |
| Frontend | React 18 + TypeScript + Vite + Tailwind | SPA moderna com tema Nord |
| Database | PostgreSQL 16 | Requisito do desafio, melhor DB relacional |
| Cache | Redis 7 | Cache e sessões |
| Infra | Docker Compose + Nginx | Orquestração e proxy reverso |
| CI | Makefile | Automação de comandos |
| Auth | JWT (PyJWT) | Diferencial solicitado |
| Docs API | Swagger/Redoc (drf-yasg) | Diferencial solicitado |
