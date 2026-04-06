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

O upload-service recebe o arquivo do frontend, parseia o CNAB e cria um registro de histórico com status "pending". O upload-worker — um processo separado que usa a mesma imagem do upload-service — faz polling no banco a cada 10 segundos buscando registros pendentes e envia os dados ao cnab-service em **lotes de 1000 transações**. A comunicação entre os serviços é protegida por **Fernet token** — uma chave simétrica compartilhada via variável de ambiente que gera tokens com expiração automática.

O cnab-service implementa **deduplicação por content_hash**: cada transação recebe um hash SHA-256 calculado sobre seus campos. Inserções com hash já existente são ignoradas silenciosamente, garantindo que o mesmo arquivo importado duas vezes não duplique os dados.

| Serviço | O que faz |
|---------|-----------|
| **upload-service** | Recebe arquivo, parseia CNAB, cria registro com status "pending" |
| **upload-worker** | Busca uploads pendentes (polling 10s), envia lotes de 1000 transações ao cnab-service, atualiza status |
| **cnab-service** | Armazena lojas e transações (com deduplicação por content_hash), serve listagens com saldo |

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
4. A autenticação Fernet garante que só o upload-worker insere dados no cnab-service.
5. O modelo de worker com polling evita dependências de filas externas (sem Redis, sem Celery) mantendo a simplicidade operacional.
6. O envio em lotes de 1000 transações reduz o número de chamadas HTTP e melhora o desempenho na importação de arquivos grandes.
7. A deduplicação por content_hash torna a operação de upload idempotente: reimportar o mesmo arquivo é seguro.

## Trade-offs

- Mais um serviço para manter e mais um banco de dados
- O polling a cada 10s introduz latência máxima de 10s entre upload e processamento
- Comunicação entre serviços adiciona um pouco de latência (mitigada pelo processamento em background)
- A chave Fernet precisa ser tratada como segredo
