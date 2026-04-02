# API Contracts

## Serviços

| Serviço | Base URL | Porta | Autenticação |
|---------|----------|-------|-------------|
| user-service | `http://localhost:7001` | 7001 | — (endpoints públicos + JWT) |
| upload-service | `http://localhost:7003` | 7003 | JWT (usuário) |
| cnab-service | `http://localhost:7002` | 7002 | JWT (consultas) / Fernet (inserção interna) |

Via Nginx (frontend): `/api/user/*` → user-service, `/api/upload/*` → upload-service, `/api/cnab/*` → cnab-service.

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

### Endpoint Interno (Fernet)

#### POST /internal/transactions/

Recebe dados parseados do upload-service. **Requer Fernet token** no header `X-Service-Token`. Não aceita JWT — somente comunicação entre serviços.

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

### Lojas e Transações (consulta pública)

#### GET /stores/

Lista lojas com saldo totalizado. Requer JWT.

**Paginação:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 100) |

**Filtros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| name | string | Filtrar por nome da loja (contém) |
| owner_name | string | Filtrar por nome do dono (contém) |
| ordering | string | `name`, `-name`, `balance`, `-balance` |

**Response 200:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid-...",
            "name": "BAR DO JOÃO",
            "owner_name": "JOÃO MACEDO",
            "owner_cpf": "09620676017",
            "balance": "152.32",
            "total_income": "264.00",
            "total_expense": "-111.68",
            "transaction_count": 4
        }
    ]
}
```

---

#### GET /stores/{store_id}/transactions/

Lista transações de uma loja. Requer JWT.

**Paginação:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 100) |

**Filtros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| type | int | Tipo de transação (1-9) |
| nature | string | `entrada` ou `saida` |
| date_from | date | Data início (YYYY-MM-DD) |
| date_to | date | Data fim (YYYY-MM-DD) |
| ordering | string | `occurred_at`, `-occurred_at`, `amount`, `-amount` |

**Response 200:**
```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "uuid-...",
            "transaction_type": {
                "code": 3,
                "description": "Financiamento",
                "nature": "saída",
                "sign": "-"
            },
            "amount": "142.00",
            "card": "4753****3153",
            "occurred_at": "2019-03-01",
            "occurred_time": "15:34:53",
            "store": {
                "id": "uuid-...",
                "name": "BAR DO JOÃO",
                "owner_name": "JOÃO MACEDO"
            }
        }
    ]
}
```

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
