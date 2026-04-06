# API Contracts

## Serviços

| Serviço | Base URL | Porta | Autenticação |
|---------|----------|-------|-------------|
| user-service | `http://localhost:7001` | 7001 | — (endpoints públicos + JWT) |
| upload-service | `http://localhost:7003` | 7003 | JWT (usuário) |
| cnab-service | `http://localhost:7002` | 7002 | JWT (consultas) / Fernet (upload) |
| cnab-dashboard | `http://localhost:7004` | 7004 | JWT (analytics) |

Via Nginx (frontend): `/api/user/*` → user-service, `/api/upload/*` → upload-service, `/api/cnab/*` → cnab-service, `/api/dashboard/*` → cnab-dashboard.

## Autenticação

### JWT (usuário → serviço)
```
Authorization: Bearer <encoded_token>
```

### Fernet (serviço → serviço)
```
X-Service-Token: <fernet_encrypted_token>
```
Usado pelo upload-service ao chamar o endpoint interno do cnab-service.

---

## User Service (porta 7001)

### Health Check

#### GET /health

Retorna status do serviço. Sem autenticação.

**Response 200:**
```json
{
    "status": "healthy",
    "system_name": "user-service",
    "version": "0.1.0",
    "environment": "development",
    "timestamp": "2026-04-01T10:00:00.000000Z"
}
```

#### GET /health/ready

Verifica conexão com o banco de dados.

**Response 200:** `{"status": "ready", ...}`
**Response 503:** `{"status": "not_ready", "error": "..."}`

#### GET /health/live

Verifica se o serviço está vivo.

**Response 200:** `{"status": "alive", ...}`

---

### Autenticação

#### POST /auth/v1/login/

Autentica o usuário e retorna token JWT.

**Request:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response 200:**
```json
{
    "encoded_token": "eyJhbGciOiJIUzI1NiIs...",
    "valid_until": "04/01/2026 15:00:00",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@cnabparser.dev",
        "first_name": "",
        "last_name": "",
        "is_active": true,
        "is_staff": true,
        "created_at": "2026-04-01T10:00:00.000000Z",
        "updated_at": "2026-04-01T10:00:00.000000Z"
    }
}
```

**Response 401:** Credenciais inválidas.
**Response 403:** Username ou password ausente.

---

#### POST /auth/v1/validate/

Valida um token JWT e retorna os dados do usuário.

**Headers:** `Authorization: Bearer <encoded_token>`

**Response 200:** Mesmo formato do login.
**Response 403:** Token inválido ou expirado.

---

### Gestão de Usuários

#### GET /users/v1/users/

Lista usuários com paginação e filtros. Requer JWT.

**Paginação:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 100) |

**Filtros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| is_active | bool | Filtrar por status ativo |
| username | string | Filtrar por username |
| email | string | Filtrar por email |
| name | string | Filtrar por nome (contém) |
| ordering | string | `username`, `-username`, `created_at`, `-created_at` |

**Response 200:** Lista paginada `{count, next, previous, results}`.

#### POST /users/v1/users/

Cria um novo usuário. Requer `is_staff` ou `is_superuser`.

#### GET /users/v1/users/{id}/

Retorna dados de um usuário. Autorização por nível.

#### PATCH /users/v1/users/{id}/

Atualiza parcialmente os dados de um usuário.

#### DELETE /users/v1/users/{id}/

Desativa um usuário (soft delete). Requer `is_staff` ou `is_superuser`.

**Response 204:** No Content.

---

## Upload Service (porta 7003)

### Health Check

#### GET /health

**Response 200:** `{"status": "healthy", "system_name": "upload-service", ...}`

#### GET /health/ready

**Response 200:** `{"status": "ready", ...}` | **503:** `{"status": "not_ready", ...}`

#### GET /health/live

**Response 200:** `{"status": "alive", ...}`

---

### Upload de Arquivo CNAB

#### POST /upload/

Recebe um arquivo CNAB, armazena e processa. Requer JWT do usuário.

**Request:** `multipart/form-data`
```
file: <arquivo.txt ou .cnab>
```

**Response 201:**
```json
{
    "id": "a1b2c3d4-...",
    "original_filename": "CNAB.txt",
    "status": "processing",
    "total_transactions": 0,
    "created_at": "2026-04-02T10:05:00Z"
}
```

**Response 400:** Arquivo inválido.
```json
{
    "detail": "Invalid file. CNAB format expected."
}
```

---

### Histórico de Uploads

#### GET /uploads/

Lista uploads do usuário com paginação e filtros. Requer JWT.

**Paginação:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 100) |

**Filtros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| status | string | `pending`, `processing`, `completed`, `failed` |
| ordering | string | `created_at`, `-created_at` |

**Response 200:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "a1b2c3d4-...",
            "original_filename": "CNAB.txt",
            "total_transactions": 21,
            "status": "completed",
            "created_at": "2026-04-02T10:05:00Z"
        }
    ]
}
```

#### GET /uploads/{id}/

Detalhe de um upload específico. Requer JWT.

---

## CNAB Service (porta 7002)

### Health Check

#### GET /health

**Response 200:** `{"status": "healthy", "system_name": "cnab-service", ...}`

#### GET /health/ready

**Response 200:** `{"status": "ready", ...}` | **503:** `{"status": "not_ready", ...}`

#### GET /health/live

**Response 200:** `{"status": "alive", ...}`

---

### Endpoint de Upload (Fernet)

#### POST /transactions/upload/

Recebe dados parseados do upload-service. **Requer Fernet token** no header `X-Service-Token`. Não aceita JWT — somente comunicação entre serviços. Transações duplicadas são ignoradas via content hash (SHA-256).

**Headers:**
```
X-Service-Token: <fernet_encrypted_token>
```

**Request:**
```json
{
    "upload_id": "a1b2c3d4-...",
    "transactions": [
        {
            "type_code": 3,
            "date": "2019-03-01",
            "amount": "142.00",
            "cpf": "09620676017",
            "card": "4753****3153",
            "time": "15:34:53",
            "store_owner": "JOÃO MACEDO",
            "store_name": "BAR DO JOÃO"
        }
    ]
}
```

**Response 201:**
```json
{
    "upload_id": "a1b2c3d4-...",
    "total_inserted": 21,
    "stores_created": 5
}
```

**Response 401:** Token Fernet ausente ou inválido.
**Response 422:** Erro no processamento dos dados.

---

### Lojas

#### GET /stores/

Lista lojas com saldo totalizado. Requer JWT.

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página |
| name | string | — | Filtrar por nome da loja (contém) |
| owner_name | string | — | Filtrar por nome do dono (contém) |

**Response 200:**
```json
{
    "count": 5,
    "results": [
        {
            "id": "uuid-...",
            "name": "BAR DO JOÃO",
            "owner_name": "JOÃO MACEDO",
            "owner_cpf": "09620676017",
            "balance": "152.32",
            "total_income": "264.00",
            "total_expense": "111.68",
            "transaction_count": 4
        }
    ]
}
```

#### GET /stores/{store_id}

Retorna uma loja específica com saldo. Requer JWT.

**Response 200:** Mesmo formato de um item da listagem.
**Response 404:** Loja não encontrada.

---

### Transações

#### GET /transactions/

Lista transações filtradas por loja. Requer JWT.

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| store_id | string | **obrigatório** | UUID da loja |
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página |
| type_code | int | — | Tipo de transação (1-9) |
| nature | string | — | `Entrada` ou `Saida` |
| date_from | date | — | Data início (YYYY-MM-DD) |
| date_to | date | — | Data fim (YYYY-MM-DD) |

**Response 200:**
```json
{
    "count": 4,
    "results": [
        {
            "id": "uuid-...",
            "transaction_type": {
                "id": "uuid-...",
                "code": 3,
                "description": "Financiamento",
                "nature": "Saida",
                "sign": "-"
            },
            "amount": "142.00",
            "card": "4753****3153",
            "occurred_at": "2019-03-01",
            "occurred_time": "15:34:53",
            "store": {
                "id": "uuid-...",
                "name": "BAR DO JOÃO",
                "owner_name": "JOÃO MACEDO",
                "owner_cpf": "09620676017"
            }
        }
    ]
}
```

#### GET /transactions/{transaction_id}

Retorna uma transação específica. Requer JWT.

**Response 200:** Mesmo formato de um item da listagem.
**Response 404:** Transação não encontrada.

---

#### GET /transaction-types/

Lista os 9 tipos de transação CNAB. Sem paginação (dados fixos). Requer JWT.

**Response 200:**
```json
[
    {"code": 1, "description": "Débito", "nature": "entrada", "sign": "+"},
    {"code": 2, "description": "Boleto", "nature": "saída", "sign": "-"},
    {"code": 3, "description": "Financiamento", "nature": "saída", "sign": "-"},
    {"code": 4, "description": "Crédito", "nature": "entrada", "sign": "+"},
    {"code": 5, "description": "Recebimento Empréstimo", "nature": "entrada", "sign": "+"},
    {"code": 6, "description": "Vendas", "nature": "entrada", "sign": "+"},
    {"code": 7, "description": "Recebimento TED", "nature": "entrada", "sign": "+"},
    {"code": 8, "description": "Recebimento DOC", "nature": "entrada", "sign": "+"},
    {"code": 9, "description": "Aluguel", "nature": "saída", "sign": "-"}
]
```

---

---

## CNAB Dashboard Service (porta 7004)

### Health Check

#### GET /health

**Response 200:** `{"status": "healthy", "system_name": "cnab-dashboard", ...}`

---

### Dashboard Analytics

Serviço read-only que consulta o banco `cnab_data` para fornecer estatísticas agregadas.

Todos os endpoints abaixo aceitam os mesmos parâmetros de filtro opcionais (exceto `transactions-detail`, que tem parâmetros adicionais):

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| store_id | UUID | Filtrar por UUID da loja |
| owner_name | string | Filtrar por nome do representante (correspondência parcial) |
| date_from | date | Data de início (YYYY-MM-DD) |
| date_to | date | Data de fim (YYYY-MM-DD) |

Todos requerem JWT.

---

#### GET /summary/

Retorna os KPIs da primeira camada do dashboard (O Panorama).

**Response 200:**
```json
{
    "total_balance": "1523.45",
    "average_ticket": "67.32",
    "total_transactions": 312,
    "attention_store": {
        "name": "LOJA X",
        "owner_name": "FULANO",
        "balance": "-450.00"
    }
}
```

---

#### GET /balance-by-store/

Retorna saldo por loja para o gráfico de barras (segunda camada — O Desempenho).

**Response 200:**
```json
[
    {"store_name": "BAR DO JOÃO", "balance": "152.32"},
    {"store_name": "LOJA X", "balance": "-450.00"}
]
```

---

#### GET /transactions-by-type/

Retorna distribuição de volume por tipo de transação para o gráfico donut (segunda camada).

**Response 200:**
```json
[
    {"type_code": 1, "description": "Débito", "nature": "entrada", "total_amount": "890.00", "count": 42},
    {"type_code": 2, "description": "Boleto", "nature": "saída", "total_amount": "320.00", "count": 15}
]
```

---

#### GET /transactions-by-hour/

Retorna densidade de transações por hora do dia para o gráfico de área (terceira camada — A Operação).

**Response 200:**
```json
[
    {"hour": 9, "count": 12, "total_amount": "540.00"},
    {"hour": 10, "count": 28, "total_amount": "1230.00"}
]
```

---

#### GET /transactions-detail/

DataTable da terceira camada com todas as transações do período filtrado. Aceita os filtros comuns (`store_id`, `owner_name`, `date_from`, `date_to`) mais parâmetros exclusivos:

| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| nature | string | — | `entrada` ou `saida` (ausente = ambas) |
| ordering | string | — | Campo de ordenação. Prefixo `-` para descendente. Valores: `amount`, `-amount`, `occurred_at`, `-occurred_at`, `store_name`, `-store_name`, `owner_name`, `-owner_name` |
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 200) |

**Response 200:** Lista paginada com transações detalhadas.

---

#### GET /available-filters/

Retorna as opções disponíveis para popular os filtros da UI dinamicamente.

**Response 200:**
```json
{
    "stores": [
        {"id": "uuid-...", "name": "BAR DO JOÃO", "owner_name": "JOÃO MACEDO"},
        {"id": "uuid-...", "name": "LOJA X", "owner_name": "FULANO DE TAL"}
    ],
    "owners": ["JOÃO MACEDO", "FULANO DE TAL"],
    "date_range": {
        "min_date": "2019-03-01",
        "max_date": "2019-03-31"
    }
}
```

> O campo `stores[].id` é o UUID da loja usado no parâmetro `store_id` dos demais endpoints.

---

#### GET /advanced-kpis/

Retorna métricas adicionais para complementar o Panorama (ticket médio, volume por natureza).

**Response 200:**
```json
{
    "total_income": "2340.00",
    "total_expense": "816.55",
    "income_count": 198,
    "expense_count": 114
}
```

---

#### GET /uploads-timeline/

Retorna histórico de uploads ao longo do tempo (para contexto temporal no dashboard).

**Response 200:**
```json
[
    {"date": "2019-03-01", "uploads_count": 3, "transactions_count": 63}
]
```

---

## Status Codes Padrão

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (soft delete) |
| 400 | Bad Request (validação) |
| 401 | Unauthorized (credenciais inválidas / Fernet inválido) |
| 403 | Forbidden (sem token / sem permissão) |
| 404 | Not Found |
| 422 | Unprocessable Entity (erro de processamento) |
| 500 | Internal Server Error |
| 503 | Service Unavailable (banco indisponível) |

## Documentação Interativa

| URL | Serviço | Ferramenta |
|-----|---------|-----------|
| `http://localhost:7001/swagger/` | user-service | Swagger UI (drf-yasg) |
| `http://localhost:7001/redoc/` | user-service | Redoc |
