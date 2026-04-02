# ADR-001: Separação do serviço de upload do serviço CNAB

**Status:** Aceito
**Data:** 2026-04-02

## Contexto

Na primeira versão, o cnab-service ia cuidar de tudo: receber o arquivo, processar e servir os dados. Na prática, isso junta duas coisas bem diferentes — o processamento de arquivo (pesado, demorado) e a consulta de dados (leve, rápida). Conforme o sistema cresce, um gargalo no processamento travaria as consultas.

## Decisão

Criar um upload-service separado que recebe e processa os arquivos CNAB. O cnab-service fica responsável só por armazenar e consultar lojas, transações e saldos.

```
Frontend → upload-service (recebe arquivo, parseia, processa)
                  ↓ Fernet token
            cnab-service (armazena lojas/transações, serve consultas)
```

## Como funciona

O upload-service recebe o arquivo do frontend, cria um registro de histórico, parseia o CNAB e chama a API do cnab-service para inserir os dados. A comunicação entre os dois serviços é protegida por **Fernet token** — uma chave simétrica compartilhada via variável de ambiente que gera tokens com expiração automática.

| Serviço | O que faz |
|---------|-----------|
| **upload-service** | Recebe arquivo, armazena histórico, parseia CNAB, chama cnab-service |
| **cnab-service** | Armazena lojas e transações, serve listagens com saldo |

## Por que Fernet?

- Token criptografado com expiração automática (TTL)
- Impossível de forjar sem a chave
- Simples de implementar (uma linha para gerar, uma para validar)
- O endpoint de inserção do cnab-service só aceita chamadas com token válido

## Bancos separados

Cada serviço tem seu próprio banco no mesmo PostgreSQL. Assim as migrations de um nunca interferem no outro.

| Banco | Serviço |
|-------|---------|
| cnab_users | user-service (Django) |
| cnab_uploads | upload-service (Alembic) |
| cnab_data | cnab-service (Alembic) |

## Por que separar?

1. Upload é I/O pesado e pode demorar. Consulta é leve. Perfis de carga diferentes.
2. Se o processamento falhar, as consultas continuam funcionando.
3. Cada serviço pode escalar de forma independente.
4. A autenticação Fernet garante que só o upload-service insere dados.

## Trade-offs

- Mais um serviço para manter e mais um banco de dados
- Comunicação entre serviços adiciona um pouco de latência (mitigada pelo processamento em background)
- A chave Fernet precisa ser tratada como segredo
