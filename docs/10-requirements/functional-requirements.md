# Requisitos Funcionais

## RF-001: Upload de Arquivo CNAB

**Prioridade:** Obrigatório
**Serviço:** upload-service

O sistema deve disponibilizar um formulário web para upload de arquivos CNAB.

- Aceitar arquivos .txt e .cnab
- Validar formato do arquivo antes do processamento
- Exibir feedback de sucesso/erro ao usuário
- Rejeitar arquivos vazios ou com formato inválido
- Armazenar histórico de uploads com status (pending, processing, completed, failed)
- Processar o arquivo em background após o upload

## RF-002: Parsing de Arquivo CNAB

**Prioridade:** Obrigatório
**Serviço:** upload-service

O upload-service deve interpretar o arquivo CNAB no formato de largura fixa.

- Extrair campos: tipo, data, valor, CPF, cartão, hora, dono_loja, nome_loja
- Normalizar valor dividindo por 100
- Converter data de YYYYMMDD para date
- Converter hora de HHMMSS para time
- Fazer strip/trim em campos texto (dono_loja, nome_loja)
- Validar tipo de transação (1-9)
- Ignorar linhas vazias
- Enviar dados parseados para o cnab-service via API interna (Fernet token)

## RF-003: Armazenamento em Banco de Dados

**Prioridade:** Obrigatório
**Serviço:** cnab-service (transações) + upload-service (histórico)

Os dados devem ser armazenados em bancos PostgreSQL separados por serviço.

- cnab-service: armazena lojas, transações e tipos de transação (banco cnab_data)
- upload-service: armazena histórico de uploads (banco cnab_uploads)
- Criar/reutilizar registro de loja (por nome_loja + CPF do dono)
- Tipos de transação pré-carregados via seed (9 tipos fixos)
- Evitar duplicatas: mesmo arquivo importado 2x não deve duplicar dados
- Endpoint interno do cnab-service protegido por Fernet token

## RF-004: Listagem de Transações por Loja

**Prioridade:** Obrigatório
**Serviço:** cnab-service

O sistema deve exibir as transações importadas agrupadas por loja.

- Listar todas as lojas com transações (paginado, com filtros)
- Para cada loja: nome, dono, CPF, saldo, total de transações
- Detalhe de transações por loja (paginado, com filtros por tipo, data, natureza)
- Totalizador de saldo por loja (soma de entradas - soma de saídas)
- Indicação visual de saldo positivo/negativo no frontend

## RF-005: Autenticação e Segurança

**Prioridade:** Bônus (diferencial)
**Serviço:** user-service + cnab-shared

O sistema implementa dois níveis de autenticação:

**JWT (usuário → serviço):**
- Login retornando encoded_token com expiração
- Validação de token via endpoint dedicado
- Gestão de usuários (CRUD com controle de permissões)
- Proteção dos endpoints de upload e listagem

**Fernet Token (serviço → serviço):**
- Comunicação segura entre upload-service e cnab-service
- Token criptografado com expiração automática (TTL)
- Chave compartilhada via variável de ambiente (SERVICE_SECRET_KEY)
- Endpoints internos aceitam apenas Fernet, não JWT

## RF-006: Documentação da API

**Prioridade:** Bônus (diferencial)
**Serviço:** user-service

O sistema disponibiliza documentação interativa da API.

- Swagger UI acessível em /swagger/
- Redoc acessível em /redoc/
- Endpoints documentados com schemas de request/response
- Collection Postman com environment local
