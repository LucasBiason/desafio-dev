# ============================================
# CNAB Parser - Makefile
# ============================================

.PHONY: help up down build restart logs migrate test lint shell-user shell-cnab shell-upload

# Colors
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RED    := \033[0;31m
NC     := \033[0m

COMPOSE := docker compose

help: ## Show this help message
	@echo ""
	@echo "$(CYAN)CNAB Parser$(NC) - Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================
# Docker
# ============================================

setup: ## Full setup: build, migrate, seed, create admin user
	@./scripts/setup.sh

up: ## Start the full stack (build + containers)
	@echo "$(CYAN)Starting CNAB Parser stack...$(NC)"
	$(COMPOSE) up --build -d
	@echo "$(GREEN)Stack is up!$(NC)"
	@echo "  Frontend:       http://localhost:7000"
	@echo "  User Service:   http://localhost:7001"
	@echo "  CNAB Service:   http://localhost:7002"
	@echo "  Upload Service: http://localhost:7003"

down: ## Stop all containers
	@echo "$(YELLOW)Stopping containers...$(NC)"
	$(COMPOSE) down
	@echo "$(GREEN)Containers stopped.$(NC)"

build: ## Rebuild images without cache
	@echo "$(CYAN)Rebuilding images...$(NC)"
	$(COMPOSE) build --no-cache

restart: ## Restart all containers
	@echo "$(YELLOW)Restarting...$(NC)"
	$(COMPOSE) restart

logs: ## Show logs for all services
	$(COMPOSE) logs -f

logs-user: ## Show user-service logs
	$(COMPOSE) logs -f user-service

logs-cnab: ## Show cnab-service logs
	$(COMPOSE) logs -f cnab-service

logs-upload: ## Show upload-service logs
	$(COMPOSE) logs -f upload-service

logs-frontend: ## Show frontend logs
	$(COMPOSE) logs -f frontend

# ============================================
# Migrations
# ============================================

migrate: migrate-user migrate-cnab migrate-upload ## Apply all migrations

migrate-user: ## Apply user-service migrations (Django)
	@echo "$(CYAN)Applying user-service migrations...$(NC)"
	$(COMPOSE) exec user-service /entrypoint.sh migrate
	@echo "$(GREEN)User-service migrations applied.$(NC)"

migrate-cnab: ## Apply cnab-service migrations (SQL)
	@echo "$(CYAN)Applying cnab-service migrations...$(NC)"
	$(COMPOSE) exec cnab-service /entrypoint.sh migrate
	@echo "$(GREEN)CNAB-service migrations applied.$(NC)"

migrate-upload: ## Apply upload-service migrations (SQL)
	@echo "$(CYAN)Applying upload-service migrations...$(NC)"
	$(COMPOSE) exec upload-service /entrypoint.sh migrate
	@echo "$(GREEN)Upload-service migrations applied.$(NC)"

makemigrations: ## Create user-service migrations (Django)
	@echo "$(CYAN)Creating migrations...$(NC)"
	$(COMPOSE) exec user-service python manage.py makemigrations
	@echo "$(GREEN)Migrations created.$(NC)"

createsuperuser: ## Create superuser on user-service
	@echo "$(CYAN)Creating superuser...$(NC)"
	$(COMPOSE) exec user-service python manage.py createsuperuser

# ============================================
# Tests
# ============================================

test: test-user test-cnab test-upload ## Run all tests

test-user: ## Run user-service tests
	@echo "$(CYAN)Running user-service tests...$(NC)"
	$(COMPOSE) exec user-service /entrypoint.sh test
	@echo "$(GREEN)User-service tests completed.$(NC)"

test-cnab: ## Run cnab-service tests
	@echo "$(CYAN)Running cnab-service tests...$(NC)"
	$(COMPOSE) exec cnab-service /entrypoint.sh test
	@echo "$(GREEN)CNAB-service tests completed.$(NC)"

test-upload: ## Run upload-service tests
	@echo "$(CYAN)Running upload-service tests...$(NC)"
	$(COMPOSE) exec upload-service /entrypoint.sh test
	@echo "$(GREEN)Upload-service tests completed.$(NC)"

# ============================================
# Code Quality
# ============================================

lint: ## Run ruff check + format on all services
	@echo "$(CYAN)Linting user-service...$(NC)"
	cd user-service && ruff check . --fix && ruff format .
	@echo "$(CYAN)Linting cnab-service...$(NC)"
	cd cnab-service && ruff check . --fix && ruff format .
	@echo "$(CYAN)Linting upload-service...$(NC)"
	cd upload-service && ruff check . --fix && ruff format .
	@echo "$(CYAN)Linting cnab-shared...$(NC)"
	cd cnab-shared && ruff check . --fix && ruff format .
	@echo "$(GREEN)Lint completed.$(NC)"

# ============================================
# Shell / Debug
# ============================================

shell-user: ## Open shell on user-service
	$(COMPOSE) exec user-service bash

shell-cnab: ## Open shell on cnab-service
	$(COMPOSE) exec cnab-service bash

shell-upload: ## Open shell on upload-service
	$(COMPOSE) exec upload-service bash

shell-db: ## Open psql on PostgreSQL
	$(COMPOSE) exec db psql -U cnab -d cnab_db

# ============================================
# Health Check
# ============================================

health: ## Check health of all services
	@echo "$(CYAN)Checking service health...$(NC)"
	@echo -n "  db:             " && ($(COMPOSE) exec db pg_isready -U cnab > /dev/null 2>&1 && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAILED$(NC)")
	@echo -n "  redis:          " && ($(COMPOSE) exec redis redis-cli ping > /dev/null 2>&1 && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAILED$(NC)")
	@echo -n "  user-service:   " && (curl -sf http://localhost:7001/health > /dev/null 2>&1 && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAILED$(NC)")
	@echo -n "  cnab-service:   " && (curl -sf http://localhost:7002/health > /dev/null 2>&1 && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAILED$(NC)")
	@echo -n "  upload-service: " && (curl -sf http://localhost:7003/health > /dev/null 2>&1 && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAILED$(NC)")
	@echo -n "  frontend:       " && (curl -sf http://localhost:7000/health > /dev/null 2>&1 && echo "$(GREEN)OK$(NC)" || echo "$(RED)FAILED$(NC)")

# ============================================
# Cleanup
# ============================================

clean: ## Remove volumes and containers (WARNING: deletes data!)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (y/N) " confirm && [ "$$confirm" = "y" ] || exit 1
	$(COMPOSE) down -v --remove-orphans
	@echo "$(GREEN)Cleanup completed.$(NC)"
