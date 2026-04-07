# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [1.0.1] - 2026-04-07

### Corrigido

- Suporte a deploy em subdiretório (ex: `lucasbiason.com/cnab/`)
- `VITE_BASE_PATH` como build arg no Dockerfile do frontend
- `basename` no BrowserRouter para rotas SPA funcionarem sob subpath
- `BASE_URL` no axios baseURL para chamadas de API sob subdiretório
- Redirect de 401 e logout usando `BASE_URL` em vez de path fixo

---

## [1.0.0] - 2026-04-06

### Adicionado

**Infraestrutura**
- Arquitetura de microsserviços com Docker Compose (7 containers + 1 worker)
- PostgreSQL 16 com 3 bancos isolados (cnab_users, cnab_data, cnab_uploads)
- Nginx como proxy reverso com rotas por servico
- Makefile com comandos de setup, build, test, migrate, lint e health check
- Script de setup automatizado (`make setup`)
- Dockerfiles multi-stage (base, test, runtime) para todos os servicos

**user-service (Django)**
- Autenticação JWT com login e validação de token
- CRUD de usuarios com controle de permissão por nivel
- Swagger UI e Redoc via drf-yasg
- 106 testes, 98% cobertura

**cnab-service (FastAPI)**
- Armazenamento de lojas e transações CNAB
- Listagem de lojas com saldo agregado (entradas - saidas)
- Listagem de transações por loja com filtros (tipo, natureza, data)
- Detalhe individual de loja e transação
- 9 tipos de transação CNAB seedados via migration
- Endpoint de ingestão via Fernet token (`/transactions/upload/`)
- Deduplicação de transações via SHA-256 content hash
- Suporte a multiselect de tipos (type_codes CSV)
- Filtro de natureza accent-safe (usa sign em vez de nature)
- 83 testes, 98% cobertura

**upload-service (FastAPI)**
- Upload de arquivo CNAB via formulario com validação
- Parser de largura fixa (80 caracteres por linha)
- Histórico de uploads com status (pending, processing, completed, failed)
- Envio em lotes de 1000 transações (batch upload)
- 53 testes, 100% cobertura

**upload-worker**
- Processamento em background via polling (10s)
- Comunicação com cnab-service via Fernet token

**cnab-dashboard (FastAPI)**
- Servico read-only para analytics do dashboard (porta 7004)
- 8 endpoints: summary, balance-by-store, transactions-by-type, transactions-by-hour, advanced-kpis, transactions-detail, uploads-timeline, available-filters
- Paginação server-side e ordenação no transactions-detail
- Filtros: store_id, owner_name, date_from, date_to, nature
- 108 testes, 96% cobertura

**cnab-shared**
- BaseModel com UUID PK, soft delete, timestamps
- BaseRepository genérico com CRUD e raw SQL
- Middlewares: AuthMiddleware, CatchExceptionsMiddleware, LoggingMiddleware
- Dependencies: require_jwt, require_service_token, FernetValidator
- Health router factory (/health, /health/ready, /health/live)
- UserService client para validação JWT inter-servico

**frontend-service (React 19)**
- Tela de login com glass-morphism
- Dashboard analítico com 3 camadas narrativas (Panorama, Desempenho, Operacao)
- 4 KPIs com tooltips explicativos
- Graficos interativos: barras (saldo), donut (composição), area (densidade horária)
- Detalhamento de transações com paginação server-side e ordenação
- Upload com drag & drop e histórico com filtros
- Listagem de lojas com saldo e detalhe de transações
- Componentes genéricos: DataTable, DateInput, FilterChip, SectionDivider, ToggleGroup, StatCard
- Formatters centralizados (utils/formatters.ts)
- Tema bycoders_ (verde #02BE3B, fundo escuro #171616)

**Documentação**
- Spec-Driven Development completo (fases 0-6)
- README com passo a passo de instalação e screenshots
- API contracts com todos os endpoints documentados
- Colecao Postman com exemplos de sucesso e erro
- ADR-001: Separação do upload-service e autenticação Fernet
- CNAB_BIG.txt com 20k linhas de teste realistas

**Qualidade**
- 350 testes automatizados + 40 testes de integração
- Cobertura: user-service 98%, cnab-service 98%, upload-service 100%, cnab-dashboard 96%
- Lint clean: ruff (Python) + ESLint (frontend)
