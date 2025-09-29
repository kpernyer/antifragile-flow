# Frontend Makefile using Centralized Configuration
# Manages React application development, build, and deployment

# Import shared configuration values
include ../shared/config/makefile.config

# Frontend specific configuration
FRONTEND_DIR := $(shell pwd)
BUILD_DIR := $(FRONTEND_DIR)/build
NODE_MODULES := $(FRONTEND_DIR)/node_modules
PACKAGE_JSON := $(FRONTEND_DIR)/package.json

# Development server configuration (uses centralized ports)
DEV_PORT := $(FRONTEND_PORT)
DEV_HOST := localhost

# Environment configuration files
ENV_EXAMPLE := .env.example
ENV_LOCAL := .env.local
ENV_PRODUCTION := .env.production

# Default target
.PHONY: help
help: ## Show this help message
	@echo "Frontend Development Commands (using centralized config)"
	@echo "=================================================="
	@echo "Ports from shared config:"
	@echo "  Frontend:    $(FRONTEND_PORT)"
	@echo "  API Server:  $(API_PORT)"
	@echo "  GraphQL:     $(GRAPHQL_PORT)"
	@echo "  Temporal:    $(TEMPORAL_PORT)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

.PHONY: install
install: $(NODE_MODULES) ## Install dependencies
	@echo "📦 Installing frontend dependencies..."

$(NODE_MODULES): $(PACKAGE_JSON)
	npm install
	@touch $(NODE_MODULES)

.PHONY: start
start: $(NODE_MODULES) check-env ## Start development server
	@echo "🚀 Starting React development server on port $(DEV_PORT)..."
	@echo "🔗 Frontend will be available at: http://$(DEV_HOST):$(DEV_PORT)"
	@echo "🔗 API endpoint configured for: http://$(DEV_HOST):$(API_PORT)"
	@echo "🔗 GraphQL endpoint configured for: http://$(DEV_HOST):$(GRAPHQL_PORT)/graphql"
	PORT=$(DEV_PORT) npm start

.PHONY: build
build: $(NODE_MODULES) check-env ## Build for production
	@echo "🏗️ Building React application for production..."
	@echo "🔧 Using environment configuration:"
	@echo "   API_URL: http://$(DEV_HOST):$(API_PORT)"
	@echo "   GRAPHQL_ENDPOINT: http://$(DEV_HOST):$(GRAPHQL_PORT)/graphql"
	npm run build
	@echo "✅ Build complete. Files in $(BUILD_DIR)/"

.PHONY: test
test: $(NODE_MODULES) ## Run tests
	@echo "🧪 Running React tests..."
	npm test -- --coverage --watchAll=false

.PHONY: lint
lint: $(NODE_MODULES) ## Run ESLint
	@echo "🔍 Linting TypeScript/React code..."
	npx eslint src/ --ext .ts,.tsx

.PHONY: lint-fix
lint-fix: $(NODE_MODULES) ## Fix ESLint issues
	@echo "🔧 Fixing ESLint issues..."
	npx eslint src/ --ext .ts,.tsx --fix

.PHONY: type-check
type-check: $(NODE_MODULES) ## Run TypeScript type checking
	@echo "📝 Checking TypeScript types..."
	npx tsc --noEmit

.PHONY: format
format: $(NODE_MODULES) ## Format code with Prettier
	@echo "💅 Formatting code with Prettier..."
	npx prettier --write src/

.PHONY: format-check
format-check: $(NODE_MODULES) ## Check code formatting
	@echo "🔍 Checking code formatting..."
	npx prettier --check src/

.PHONY: clean
clean: ## Clean build artifacts and dependencies
	@echo "🧹 Cleaning frontend build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -rf $(NODE_MODULES)
	rm -rf coverage/

.PHONY: check-env
check-env: ## Check environment configuration
	@echo "🌍 Environment Configuration Check:"
	@echo "=================================="
	@if [ -f "$(ENV_LOCAL)" ]; then \
		echo "✅ Local environment file exists: $(ENV_LOCAL)"; \
		echo "📋 Current configuration:"; \
		grep -E "^REACT_APP_" $(ENV_LOCAL) || echo "   No REACT_APP_ variables found"; \
	else \
		echo "⚠️  Local environment file not found: $(ENV_LOCAL)"; \
		echo "💡 Consider copying $(ENV_EXAMPLE) to $(ENV_LOCAL)"; \
	fi
	@echo ""
	@echo "🔧 Shared Configuration Values:"
	@echo "   Frontend Port: $(FRONTEND_PORT)"
	@echo "   API Port:      $(API_PORT)"
	@echo "   GraphQL Port:  $(GRAPHQL_PORT)"
	@echo "   Temporal Port: $(TEMPORAL_PORT)"

.PHONY: setup-env
setup-env: ## Set up environment configuration
	@echo "🔧 Setting up environment configuration..."
	@if [ ! -f "$(ENV_LOCAL)" ]; then \
		cp $(ENV_EXAMPLE) $(ENV_LOCAL); \
		echo "✅ Created $(ENV_LOCAL) from $(ENV_EXAMPLE)"; \
	else \
		echo "ℹ️  $(ENV_LOCAL) already exists"; \
	fi

.PHONY: dev
dev: setup-env start ## Full development setup and start

.PHONY: ci
ci: install lint type-check test build ## Run all CI checks

.PHONY: serve-build
serve-build: build ## Serve production build locally
	@echo "🌐 Serving production build on port 5000..."
	npx serve -s $(BUILD_DIR) -p 5000

.PHONY: analyze-bundle
analyze-bundle: build ## Analyze bundle size
	@echo "📊 Analyzing bundle size..."
	npx webpack-bundle-analyzer $(BUILD_DIR)/static/js/*.js

# Docker support
.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	docker build -t antifragile-flow-frontend:latest .

.PHONY: docker-run
docker-run: ## Run Docker container
	@echo "🐳 Running Docker container on port $(FRONTEND_PORT)..."
	docker run -p $(FRONTEND_PORT):80 antifragile-flow-frontend:latest

# Health check using centralized configuration
.PHONY: health-check
health-check: ## Check if all services are accessible
	@echo "🏥 Health Check (using centralized config):"
	@echo "==========================================="
	@echo "Checking Frontend ($(DEV_HOST):$(DEV_PORT))..."
	@curl -f http://$(DEV_HOST):$(DEV_PORT) > /dev/null 2>&1 && echo "✅ Frontend is running" || echo "❌ Frontend is not responding"
	@echo "Checking API Server ($(DEV_HOST):$(API_PORT))..."
	@curl -f http://$(DEV_HOST):$(API_PORT)/health > /dev/null 2>&1 && echo "✅ API Server is running" || echo "❌ API Server is not responding"
	@echo "Checking GraphQL Server ($(DEV_HOST):$(GRAPHQL_PORT))..."
	@curl -f http://$(DEV_HOST):$(GRAPHQL_PORT)/graphql > /dev/null 2>&1 && echo "✅ GraphQL Server is running" || echo "❌ GraphQL Server is not responding"

# Show configuration
.PHONY: show-config
show-config: ## Show current configuration
	@echo "📋 Frontend Configuration (from centralized config):"
	@echo "=================================================="
	@echo "Frontend URL:    http://$(DEV_HOST):$(FRONTEND_PORT)"
	@echo "API URL:         http://$(DEV_HOST):$(API_PORT)"
	@echo "GraphQL URL:     http://$(DEV_HOST):$(GRAPHQL_PORT)"
	@echo "GraphQL Endpoint: http://$(DEV_HOST):$(GRAPHQL_PORT)/graphql"
	@echo "GraphQL Playground: http://$(DEV_HOST):$(GRAPHQL_PORT)/playground"
	@echo "Temporal UI:     http://$(DEV_HOST):$(TEMPORAL_UI_PORT)"
