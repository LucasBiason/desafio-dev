# API Contracts

## Serviços

| Serviço | Base URL | Porta |
|---------|----------|-------|
| user-service | `http://localhost:7001` | 7001 |
| cnab-service | `http://localhost:7002` | 7002 |

Via Nginx (frontend): `/api/user/*` → user-service, `/api/cnab/*` → cnab-service.

## Autenticação

Todos os endpoints protegidos requerem header:
```
Authorization: Bearer <encoded_token>
```

---

## User Service (porta 7001)

### Health Check

#### GET /health

Retorna status do serviço. Sem autenticação.

**Response 200:**
```json
{
    "service": "user-service",
    "version": "0.1.0",
    "dt": "2026-04-01T10:00:00.000000Z"
}
```

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
        "email": "admin@cnab.com",
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
```json
{
    "detail": "Unable to authenticate with provided credentials."
}
```

**Response 403:** Username ou password ausente.
```json
{
    "detail": "Username is required."
}
```

---

#### POST /auth/v1/validate/

Valida um token JWT e retorna os dados do usuário associado.

**Headers:**
```
Authorization: Bearer <encoded_token>
```

**Response 200:**
```json
{
    "encoded_token": "eyJhbGciOiJIUzI1NiIs...",
    "valid_until": "04/01/2026 15:00:00",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@cnab.com",
        "first_name": "",
        "last_name": "",
        "is_active": true,
        "is_staff": true,
        "created_at": "2026-04-01T10:00:00.000000Z",
        "updated_at": "2026-04-01T10:00:00.000000Z"
    }
}
```

**Response 403:** Token inválido ou expirado.
```json
{
    "detail": "Invalid Token"
}
```

---

### Gestão de Usuários

#### GET /users/v1/users/

Lista usuários visíveis ao usuário autenticado, com paginação e filtros.

**Autorização:**
- Superusers: veem todos os usuários
- Staff: veem todos exceto superusers
- Usuários comuns: veem apenas a si mesmos

**Paginação:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 100) |

**Filtros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| is_active | bool | Filtrar por status ativo |
| username | string | Filtrar por username (exato) |
| email | string | Filtrar por email (exato) |
| name | string | Filtrar por nome (contém, em first_name ou last_name) |
| ordering | string | Ordenação: `username`, `-username`, `created_at`, `-created_at` |

**Response 200:**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@cnab.com",
            "first_name": "",
            "last_name": "",
            "is_active": true,
            "is_staff": true,
            "created_at": "2026-04-01T10:00:00.000000Z",
            "updated_at": "2026-04-01T10:00:00.000000Z"
        }
    ]
}
```

---

#### POST /users/v1/users/

Cria um novo usuário. Requer `is_staff` ou `is_superuser`.

**Request:**
```json
{
    "username": "operador",
    "email": "operador@cnab.com",
    "password": "oper123456",
    "first_name": "Operador",
    "last_name": "CNAB"
}
```

**Response 201:**
```json
{
    "id": 2,
    "username": "operador",
    "email": "operador@cnab.com",
    "first_name": "Operador",
    "last_name": "CNAB",
    "is_active": true,
    "is_staff": false,
    "created_at": "2026-04-01T10:05:00.000000Z",
    "updated_at": "2026-04-01T10:05:00.000000Z"
}
```

**Response 400:** Username ou email duplicado.
```json
{
    "code": 400,
    "detail": "Username already in use.",
    "status": "InvalidUserData"
}
```

**Response 403:** Sem permissão.
```json
{
    "code": 403,
    "detail": "You do not have permission to perform this action.",
    "status": "UnauthorizedUser"
}
```

---

#### GET /users/v1/users/{id}/

Retorna dados de um usuário específico.

**Autorização:**
- Usuários podem acessar seus próprios dados
- Superusers podem acessar qualquer usuário
- Staff pode acessar não-superusers

**Response 200:**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@cnab.com",
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "is_staff": true,
    "created_at": "2026-04-01T10:00:00.000000Z",
    "updated_at": "2026-04-01T10:00:00.000000Z"
}
```

**Response 404:** Usuário não encontrado.
```json
{
    "code": 404,
    "detail": "User with id 99999 not found.",
    "status": "UserNotFound"
}
```

---

#### PATCH /users/v1/users/{id}/

Atualiza parcialmente os dados de um usuário.

**Request:**
```json
{
    "first_name": "Nome Atualizado"
}
```

**Response 200:** Dados atualizados do usuário.

---

#### DELETE /users/v1/users/{id}/

Desativa um usuário (soft delete: `is_active=false`). Requer `is_staff` ou `is_superuser`.

**Response 204:** No Content.

---

## CNAB Service (porta 7002)

### Health Check

#### GET /health

Retorna status do serviço. Sem autenticação.

**Response 200:**
```json
{
    "status": "healthy"
}
```

---

### Upload CNAB

#### POST /cnab/upload/

Upload e processamento de arquivo CNAB. *(A ser implementado)*

**Request:** `multipart/form-data`
```
file: <arquivo.txt>
```

**Response 201:**
```json
{
    "id": 1,
    "original_filename": "CNAB.txt",
    "total_transactions": 21,
    "status": "completed",
    "created_at": "2026-04-01T10:05:00Z"
}
```

---

### Lojas e Transações

#### GET /cnab/stores/

Lista lojas com saldo totalizado, com paginação e filtros. *(A ser implementado)*

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
| ordering | string | Ordenação: `name`, `-name`, `balance`, `-balance` |

**Response 200:**
```json
{
    "count": 5,
    "next": "http://localhost:7002/cnab/stores/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
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

#### GET /cnab/stores/{store_id}/transactions/

Lista transações de uma loja específica, com paginação e filtros. *(A ser implementado)*

**Paginação:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 100) |

**Filtros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| type | int | Filtro por tipo de transação (1-9) |
| nature | string | Filtro por natureza: `entrada` ou `saida` |
| date_from | date | Data início (YYYY-MM-DD) |
| date_to | date | Data fim (YYYY-MM-DD) |
| ordering | string | Ordenação: `occurred_at`, `-occurred_at`, `amount`, `-amount` |

**Response 200:**
```json
{
    "count": 4,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "transaction_type": {
                "code": 3,
                "description": "Financiamento",
                "nature": "saida",
                "sign": "-"
            },
            "amount": "142.00",
            "card": "4753****3153",
            "occurred_at": "2019-03-01",
            "occurred_time": "15:34:53"
        }
    ]
}
```

---

#### GET /cnab/uploads/

Histórico de uploads com paginação e filtros. *(A ser implementado)*

**Paginação:**
| Parâmetro | Tipo | Default | Descrição |
|-----------|------|---------|-----------|
| page | int | 1 | Número da página |
| page_size | int | 20 | Itens por página (max: 100) |

**Filtros:**
| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| status | string | Filtro por status: `pending`, `processing`, `completed`, `failed` |
| ordering | string | Ordenação: `created_at`, `-created_at` |

**Response 200:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "original_filename": "CNAB.txt",
            "total_transactions": 21,
            "status": "completed",
            "created_at": "2026-04-01T10:05:00Z"
        }
    ]
}
```

---

#### GET /cnab/transaction-types/

Lista tipos de transação (referência). *(A ser implementado)*

---

## Status Codes Padrão

| Código | Significado |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content (soft delete) |
| 400 | Bad Request (validação) |
| 401 | Unauthorized (credenciais inválidas) |
| 403 | Forbidden (sem token / token inválido / sem permissão) |
| 404 | Not Found |
| 500 | Internal Server Error |

## Documentação Interativa

| URL | Serviço | Ferramenta |
|-----|---------|-----------|
| `http://localhost:7001/swagger/` | user-service | Swagger UI (drf-yasg) |
| `http://localhost:7001/redoc/` | user-service | Redoc |
