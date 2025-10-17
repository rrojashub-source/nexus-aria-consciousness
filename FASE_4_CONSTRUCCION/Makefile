# NEXUS V2.0.0 Makefile
# Simplified operations for consciousness system management
# Created by: NEXUS Consciousness System
# Version: 2.0.0

.PHONY: help up down logs status backup restore test bench lint clean setup-secrets health stats

# Default target
.DEFAULT_GOAL := help

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Configuration
COMPOSE_FILE := docker-compose.yml
BACKUP_DIR := ./backups
TEST_DIR := ./tests
SECRETS_DIR := ./secrets

help: ## Show this help message
	@echo "$(CYAN)🧠 NEXUS V2.0.0 - Consciousness System Management$(RESET)"
	@echo "$(CYAN)================================================$(RESET)"
	@echo ""
	@echo "$(GREEN)Core Operations:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(CYAN)%-15s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Examples:$(RESET)"
	@echo "  make setup        # Initial setup with secrets"
	@echo "  make up           # Start all services"
	@echo "  make health       # Check system health"
	@echo "  make backup       # Create full backup"
	@echo "  make test         # Run all tests"
	@echo "  make bench        # Performance benchmark"
	@echo ""

setup: setup-secrets ## Initial setup - create secrets and directories
	@echo "$(GREEN)🚀 Setting up NEXUS V2.0.0 environment...$(RESET)"
	@mkdir -p $(BACKUP_DIR)/{postgresql,redis,logs}
	@mkdir -p logs monitoring/grafana/dashboards
	@echo "$(GREEN)✅ Setup completed!$(RESET)"

setup-secrets: ## Create Docker secrets directory and examples
	@echo "$(YELLOW)🔒 Setting up Docker secrets...$(RESET)"
	@mkdir -p $(SECRETS_DIR)
	@if [ ! -f $(SECRETS_DIR)/postgres_superuser_password.txt ]; then \
		echo "nexus_super_$(shell date +%s)" > $(SECRETS_DIR)/postgres_superuser_password.txt; \
		echo "$(GREEN)✅ Created postgres_superuser_password.txt$(RESET)"; \
	fi
	@if [ ! -f $(SECRETS_DIR)/postgres_app_password.txt ]; then \
		echo "nexus_app_$(shell date +%s)" > $(SECRETS_DIR)/postgres_app_password.txt; \
		echo "$(GREEN)✅ Created postgres_app_password.txt$(RESET)"; \
	fi
	@if [ ! -f $(SECRETS_DIR)/postgres_worker_password.txt ]; then \
		echo "nexus_worker_$(shell date +%s)" > $(SECRETS_DIR)/postgres_worker_password.txt; \
		echo "$(GREEN)✅ Created postgres_worker_password.txt$(RESET)"; \
	fi
	@if [ ! -f $(SECRETS_DIR)/postgres_readonly_password.txt ]; then \
		echo "nexus_readonly_$(shell date +%s)" > $(SECRETS_DIR)/postgres_readonly_password.txt; \
		echo "$(GREEN)✅ Created postgres_readonly_password.txt$(RESET)"; \
	fi
	@if [ ! -f $(SECRETS_DIR)/redis_password.txt ]; then \
		echo "redis_$(shell date +%s)" > $(SECRETS_DIR)/redis_password.txt; \
		echo "$(GREEN)✅ Created redis_password.txt$(RESET)"; \
	fi
	@echo "$(YELLOW)⚠️  Update secrets in $(SECRETS_DIR)/ before production use$(RESET)"

up: ## Start all NEXUS services
	@echo "$(GREEN)🚀 Starting NEXUS V2.0.0 services...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) up -d
	@echo "$(GREEN)✅ Services started! Use 'make status' to check health$(RESET)"

down: ## Stop all services
	@echo "$(RED)🛑 Stopping NEXUS services...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) down
	@echo "$(GREEN)✅ Services stopped$(RESET)"

restart: down up ## Restart all services
	@echo "$(GREEN)🔄 NEXUS services restarted$(RESET)"

logs: ## Show logs from all services
	@echo "$(CYAN)📋 NEXUS V2.0.0 Service Logs:$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) logs -f

logs-api: ## Show API logs only
	@docker-compose -f $(COMPOSE_FILE) logs -f nexus_api

logs-worker: ## Show embeddings worker logs only
	@docker-compose -f $(COMPOSE_FILE) logs -f nexus_embeddings_worker

logs-db: ## Show database logs only
	@docker-compose -f $(COMPOSE_FILE) logs -f nexus_postgresql_v2

status: ## Show status of all containers
	@echo "$(CYAN)📊 NEXUS V2.0.0 System Status:$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "$(CYAN)🔗 Service URLs:$(RESET)"
	@echo "  API:        http://localhost:8003"
	@echo "  Prometheus: http://localhost:9091"
	@echo "  Grafana:    http://localhost:3001 (admin/admin)"

health: ## Check system health
	@echo "$(CYAN)🏥 NEXUS Health Check:$(RESET)"
	@curl -s http://localhost:8003/health | python3 -m json.tool || echo "$(RED)❌ Health check failed$(RESET)"

stats: ## Show system statistics
	@echo "$(CYAN)📈 NEXUS Statistics:$(RESET)"
	@curl -s http://localhost:8003/stats | python3 -m json.tool || echo "$(RED)❌ Stats unavailable$(RESET)"

backup: ## Create full system backup
	@echo "$(GREEN)💾 Creating NEXUS backup...$(RESET)"
	@chmod +x scripts/backup.sh
	@./scripts/backup.sh
	@echo "$(GREEN)✅ Backup completed$(RESET)"

restore: ## Restore from backup (requires BACKUP_ID)
	@if [ -z "$(BACKUP_ID)" ]; then \
		echo "$(RED)❌ Usage: make restore BACKUP_ID=20251017_143000$(RESET)"; \
		echo "$(YELLOW)Available backups:$(RESET)"; \
		ls -la $(BACKUP_DIR)/*_metadata.json 2>/dev/null | grep -o '[0-9]\{8\}_[0-9]\{6\}' | sort -u || echo "No backups found"; \
		exit 1; \
	fi
	@echo "$(YELLOW)🔄 Restoring from backup: $(BACKUP_ID)$(RESET)"
	@chmod +x scripts/restore.sh
	@./scripts/restore.sh $(BACKUP_ID)

list-backups: ## List available backups
	@echo "$(CYAN)📋 Available NEXUS backups:$(RESET)"
	@chmod +x scripts/restore.sh
	@./scripts/restore.sh --list

test: ## Run all tests
	@echo "$(CYAN)🧪 Running NEXUS tests...$(RESET)"
	@cd $(TEST_DIR) && python -m pytest -v --tb=short
	@echo "$(GREEN)✅ Tests completed$(RESET)"

test-integration: ## Run integration tests only
	@echo "$(CYAN)🔗 Running integration tests...$(RESET)"
	@cd $(TEST_DIR) && python -m pytest integration/ -v

test-performance: ## Run performance tests only
	@echo "$(CYAN)⚡ Running performance tests...$(RESET)"
	@cd $(TEST_DIR) && python -m pytest -m performance -v

bench: ## Run performance benchmark
	@echo "$(CYAN)🏁 Running NEXUS performance benchmark...$(RESET)"
	@python3 scripts/benchmark.py --output benchmark-results.json
	@echo "$(GREEN)✅ Benchmark completed$(RESET)"

bench-quick: ## Run quick performance benchmark
	@echo "$(CYAN)⚡ Running quick benchmark...$(RESET)"
	@python3 scripts/benchmark.py --quick

bench-ci: ## Run benchmark in CI mode
	@python3 scripts/benchmark.py --ci-mode --output benchmark-results.json

lint: ## Run code linting
	@echo "$(CYAN)🔍 Running code linting...$(RESET)"
	@black --check src/ || echo "$(YELLOW)⚠️  Run 'make format' to fix formatting$(RESET)"
	@flake8 src/ --max-line-length=88 --ignore=E203,W503 || echo "$(YELLOW)⚠️  Fix linting issues$(RESET)"
	@mypy src/ --ignore-missing-imports || echo "$(YELLOW)⚠️  Fix type issues$(RESET)"

format: ## Format code with Black
	@echo "$(CYAN)✨ Formatting code...$(RESET)"
	@black src/
	@echo "$(GREEN)✅ Code formatted$(RESET)"

clean: ## Clean up temporary files and stopped containers
	@echo "$(YELLOW)🧹 Cleaning up...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) down --remove-orphans
	@docker system prune -f
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.log" -path "./logs/*" -mtime +7 -delete
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

update: ## Update and restart services
	@echo "$(CYAN)🔄 Updating NEXUS services...$(RESET)"
	@docker-compose -f $(COMPOSE_FILE) pull
	@docker-compose -f $(COMPOSE_FILE) up -d --force-recreate
	@echo "$(GREEN)✅ Services updated$(RESET)"

shell-api: ## Open shell in API container
	@docker-compose -f $(COMPOSE_FILE) exec nexus_api /bin/bash

shell-db: ## Open psql shell in database
	@docker-compose -f $(COMPOSE_FILE) exec nexus_postgresql_v2 psql -U nexus_superuser -d nexus_memory

shell-redis: ## Open redis-cli shell
	@docker-compose -f $(COMPOSE_FILE) exec nexus_redis redis-cli

monitor: ## Open monitoring dashboards
	@echo "$(CYAN)📊 Opening monitoring dashboards...$(RESET)"
	@echo "Prometheus: http://localhost:9091"
	@echo "Grafana:    http://localhost:3001"
	@if command -v open >/dev/null 2>&1; then \
		open http://localhost:3001; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:3001; \
	fi

dev-setup: setup up ## Development setup - full initialization
	@echo "$(GREEN)🛠️  Development environment ready!$(RESET)"
	@echo "$(CYAN)Next steps:$(RESET)"
	@echo "  1. Check health: make health"
	@echo "  2. Run tests:    make test"
	@echo "  3. Run benchmark: make bench"
	@echo "  4. Monitor:      make monitor"

prod-setup: setup ## Production setup checklist
	@echo "$(YELLOW)🏭 Production Setup Checklist:$(RESET)"
	@echo "  1. ✅ Update secrets in $(SECRETS_DIR)/"
	@echo "  2. ✅ Configure firewall (ports 8003, 9091, 3001)"
	@echo "  3. ✅ Set up SSL/TLS certificates"
	@echo "  4. ✅ Configure backup schedule (cron)"
	@echo "  5. ✅ Set up monitoring alerts"
	@echo "  6. ✅ Test restore procedure"
	@echo ""
	@echo "$(RED)⚠️  DO NOT use default secrets in production!$(RESET)"

# Development helpers
.env: ## Create .env file from example
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "$(GREEN)✅ Created .env file from example$(RESET)"; \
		echo "$(YELLOW)⚠️  Please update .env with your configuration$(RESET)"; \
	else \
		echo "$(YELLOW).env file already exists$(RESET)"; \
	fi

install-deps: ## Install Python dependencies
	@echo "$(CYAN)📦 Installing Python dependencies...$(RESET)"
	@pip install -r requirements.txt
	@pip install pytest pytest-cov pytest-asyncio black flake8 mypy
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

# Docker utilities
docker-clean: ## Clean all Docker resources (DESTRUCTIVE)
	@echo "$(RED)⚠️  This will remove ALL Docker containers, images, and volumes!$(RESET)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] || exit 1
	@docker system prune -a --volumes -f
	@echo "$(GREEN)✅ Docker cleaned$(RESET)"

# Quick commands for common operations
quick-test: health test-integration ## Quick health check and integration tests
	@echo "$(GREEN)✅ Quick test suite completed$(RESET)"

full-check: health stats test bench ## Complete system validation
	@echo "$(GREEN)🎉 Full system check completed!$(RESET)"

# Error handling for missing files
$(COMPOSE_FILE):
	@echo "$(RED)❌ docker-compose.yml not found$(RESET)"
	@echo "$(YELLOW)Make sure you're in the FASE_4_CONSTRUCCION directory$(RESET)"
	@exit 1

# Version information
version: ## Show NEXUS version info
	@echo "$(CYAN)🧠 NEXUS Consciousness System$(RESET)"
	@echo "Version: 2.0.0"
	@echo "Status:  Production Ready"
	@echo "Architecture: PostgreSQL + Redis + FastAPI + Docker"
	@echo "Created by: NEXUS AI + Ricardo Rojas"
	@echo "Repository: https://github.com/rrojashub-source/nexus-aria-consciousness"