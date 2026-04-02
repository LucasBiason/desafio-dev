# Requisitos Funcionais

## RF-001: Upload de Arquivo CNAB

**Prioridade:** Obrigatório

O sistema deve disponibilizar um formulário web para upload de arquivos CNAB.

- Aceitar arquivos .txt e .cnab
- Validar formato do arquivo antes do processamento
- Exibir feedback de sucesso/erro ao usuário
- Rejeitar arquivos vazios ou com formato inválido

## RF-002: Parsing de Arquivo CNAB

**Prioridade:** Obrigatório

O sistema deve interpretar o arquivo CNAB no formato de largura fixa.

- Extrair campos: tipo, data, valor, CPF, cartão, hora, dono_loja, nome_loja
- Normalizar valor dividindo por 100
- Converter data de YYYYMMDD para date
- Converter hora de HHMMSS para time
- Fazer strip/trim em campos texto (dono_loja, nome_loja)
- Validar tipo de transação (1-9)
- Ignorar linhas vazias

## RF-003: Armazenamento em Banco de Dados

**Prioridade:** Obrigatório

O sistema deve armazenar os dados normalizados em PostgreSQL.

- Criar/reutilizar registro de loja (por nome_loja + dono_loja)
- Criar/reutilizar tipo de transação (tabela de referência)
- Armazenar cada transação vinculada à loja e tipo
- Evitar duplicatas: mesmo arquivo importado 2x não deve duplicar dados
- Manter histórico de uploads (arquivo, data, qtd_transações, status)

## RF-004: Listagem de Transações por Loja

**Prioridade:** Obrigatório

O sistema deve exibir as transações importadas agrupadas por loja.

- Listar todas as lojas com transações
- Para cada loja: nome, dono, lista de transações
- Cada transação: tipo, descrição, natureza, data, hora, valor, cartão
- Totalizador de saldo por loja (soma de entradas - soma de saídas)
- Indicação visual de saldo positivo/negativo

## RF-005: Autenticação JWT

**Prioridade:** Bônus (diferencial)

O sistema deve implementar autenticação via JWT.

- Registro de usuário (username, email, password)
- Login retornando access_token + refresh_token
- Refresh de token expirado
- Proteção dos endpoints de upload e listagem
- Logout (invalidação de token)

## RF-006: Documentação da API

**Prioridade:** Bônus (diferencial)

O sistema deve disponibilizar documentação interativa da API.

- Swagger UI acessível em /api/docs/
- Redoc acessível em /api/redoc/
- Todos os endpoints documentados com schemas de request/response
- Exemplos de uso
