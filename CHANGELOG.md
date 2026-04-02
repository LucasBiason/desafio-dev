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
- Arquivo CNAB de exemplo movido para assets/
- README do projeto com instruções de setup
