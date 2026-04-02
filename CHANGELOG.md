# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Added
- Documentação Spec-Driven (contexto, requisitos, design, API contracts)
- Diagrama de banco de dados (DBML)
- Diagrama de contexto do sistema
- Collection Postman com environment local
- Infraestrutura do projeto (Docker Compose, Makefile, .gitignore, .editorconfig)
- user-service: autenticação JWT (login, validação de token)
- user-service: gestão de usuários (CRUD com paginação e filtros)
- user-service: controle de permissões por nível (superuser, staff, usuário)
- user-service: Swagger UI e Redoc
- user-service: Dockerfile multi-stage (base, test, runtime)
- user-service: 106 testes unitários, 98% de cobertura
- user-service: health checks (/health, /health/ready, /health/live)
- user-service: LoggingMiddleware com timing de request/response
- cnab-shared: BaseModel com UUID, soft delete e timestamps
- cnab-shared: BaseRepository genérico com CRUD e SQL parametrizado
- cnab-shared: CNABFastAPI para setup centralizado (CORS, middleware, routers)
- cnab-shared: hierarquia de exceções customizadas (401, 400, 403, 404, 409, 500)
- cnab-shared: AuthMiddleware para validação de JWT via user-service
- cnab-shared: CatchExceptionsMiddleware e LoggingMiddleware
- cnab-shared: health router factory com /health, /health/ready e /health/live
- cnab-shared: schemas de paginação (PaginationParams, PaginatedResponse)
- cnab-shared: UserService como cliente HTTP para validação de token
- cnab-shared: módulo de logging centralizado
- frontend-service: tela de login com glass-morphism e tema Nord
- frontend-service: dashboard com cards de resumo
- frontend-service: sidebar, header e rotas protegidas
- frontend-service: integração JWT com user-service
- frontend-service: Nginx como proxy reverso com headers anti-cache
- frontend-service: ícones via Font Awesome
- Arquivo CNAB de exemplo movido para assets/
- README do projeto com instruções de setup
