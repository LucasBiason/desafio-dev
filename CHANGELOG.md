# Changelog

Todas as mudancas notaveis neste projeto serao documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [1.0.1] - 2026-04-06

### Adicionado

**cnab-dashboard (novo microsservico)**
- Servico read-only na porta 7004 para analytics do dashboard
- 8 endpoints: summary, balance-by-store, transactions-by-type, transactions-by-hour, advanced-kpis, transactions-detail, uploads-timeline, available-filters
- Todos os endpoints com filtros: store_id, owner_name, date_from, date_to
- Paginacao server-side e ordenacao no transactions-detail
- Filtro de natureza (entrada/saida) no backend
- 108 testes, 96% cobertura

**Dashboard analitico (frontend)**
- 3 camadas narrativas: O Panorama, O Desempenho, A Operacao
- 4 KPIs com tooltips explicativos: Fluxo de Caixa, Ticket Medio, Volume Operacional, Ponto de Atencao
- Graficos interativos: barras (Saldo por Unidade), donut (Composicao de Gastos), area (Densidade por Hora)
- Detalhamento de transacoes com paginacao server-side e ordenacao por coluna
- Filtros globais recarregam graficos; filtro de natureza recarrega apenas a tabela

**Deduplicacao de transacoes**
- Coluna content_hash (SHA-256) na tabela cnab_transaction
- Upload duplicado nao insere transacoes repetidas

**Componentes genericos (frontend)**
- DateInput com icone de calendario e showPicker
- SectionDivider para separacao visual de secoes
- ToggleGroup para selecao de opcoes
- Formatters centralizados em utils/formatters.ts

### Alterado

**cnab-service**
- StoreController e TransactionController separados (um dominio por controller)
- store_router e transaction_router separados
- Endpoint renomeado: /internal/transactions/ para /transactions/upload/
- internal_controller/schema renomeados para upload_controller/schema
- SQL movido dos controllers para os repositories
- Modulos services/ e validators/ removidos (vazios)
- Suporte a multiplos type_codes via CSV

**cnab-shared**
- require_jwt, require_service_token e FernetValidator movidos para cnab-shared
- Novo modulo dependencies/ com autenticacao reutilizavel

**upload-service**
- Batch upload em lotes de 1000 transacoes
- URL atualizada para /transactions/upload/

**Frontend**
- Types extraidos para types/dashboard.ts
- Labels nos filtros de Tipo, Natureza e Periodo (Stores)
- Layout dos graficos ajustado (barras 2/5 + donut 3/5)
- DataTable com suporte a paginacao e ordenacao server-side

### Corrigido

- Swagger do user-service (ref_name nos UserSerializer duplicados)
- Transaction-types retornava erro UUID (cast para string)
- Transactions-by-type falhava com filtro de owner_name (JOIN order)
- Filtro de natureza nas transacoes (usa tt.sign, accent-safe)
- SQLite in-memory para todos os testes
- Tooltip do PieChart animando do canto (isAnimationActive=false)
- Icone duplicado no datepicker

### Documentacao

- README atualizado com arquitetura de 4 servicos e screenshots
- API contracts, system-context e architecture atualizados
- Colecao Postman completa (cnab-service + dashboard)
- CNAB_BIG.txt com 20k linhas de teste realistas
- 6 screenshots recapturadas

---

## [1.0.0] - 2026-04-04

### Adicionado

**Infraestrutura**
- Arquitetura de microsservicos com Docker Compose
- PostgreSQL 16 com 3 bancos isolados (cnab_users, cnab_data, cnab_uploads)
- Nginx como proxy reverso com rotas por servico
- Makefile com comandos de setup, build, test, migrate, lint e health
- Dockerfiles multi-stage (base, test, runtime)

**user-service (Django)**
- Autenticacao JWT com login e validacao de token
- CRUD de usuarios com controle de permissao
- Swagger UI e Redoc via drf-yasg
- 106 testes, 98% cobertura

**cnab-service (FastAPI)**
- Armazenamento de lojas e transacoes CNAB
- Listagem de lojas com saldo agregado
- 9 tipos de transacao CNAB seedados via migration
- Endpoint de ingestao via Fernet token

**upload-service (FastAPI)**
- Upload de arquivo CNAB com validacao
- Parser de largura fixa (80 caracteres por linha)
- Historico de uploads com status
- 52 testes, 100% cobertura

**upload-worker**
- Processamento em background via polling (10s)
- Comunicacao com cnab-service via Fernet token

**cnab-shared**
- BaseModel, BaseRepository, middlewares, health router, UserService client

**frontend-service (React)**
- Login com glass-morphism
- Upload com drag & drop
- Historico de uploads com filtros
- Listagem de lojas com saldo
- Tema bycoders_ (verde #02BE3B, fundo escuro #171616)

**Documentacao**
- Spec-Driven Development completo (fases 0-6)
- ADR-001: Separacao do upload-service
- Colecao Postman com exemplos
