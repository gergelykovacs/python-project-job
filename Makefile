# Variables
VENV_PATH := .venv/bin
SYSTEM_PYTHON := python3
PYTHON := $(VENV_PATH)/python3
PIP := $(VENV_PATH)/pip
PIP_COMPILE := $(VENV_PATH)/pip-compile
RUFF := $(VENV_PATH)/ruff
PYTEST := $(VENV_PATH)/pytest
TWINE := $(VENV_PATH)/twine
BANDIT := $(VENV_PATH)/bandit
PRECOMMIT := $(VENV_PATH)/pre-commit
PCU := $(VENV_PATH)/pcu
DOCKER := docker
VERSION := $(strip $(shell cat VERSION))

APP_NAME := my-job
DOCKER_TAG := $(VERSION)
AWS_REGION := us-east-1
AWS_ACCOUNT_ID := 123456789012
ECR_REPO := $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/$(APP_NAME)

# Default target (runs when you just type "make")
.PHONY: all
all: lock install upgrade lint test build

# --- Dependency Management ---

.PHONY: venv
venv:
	@echo "🛠 Creating virtual environment..."
	$(SYSTEM_PYTHON) -m venv .venv
	@. ./.venv/bin/activate
	@echo "✅ virtual environment created."

# Lock: Generates requirements.txt from pyproject.toml
.PHONY: lock
lock:
	@echo "🔒 Locking dependencies..."
	$(PIP_COMPILE) -o requirements.txt pyproject.toml --resolver=backtracking
	@echo "✅ requirements.txt generated."

# Upgrade: Updates all packages to the latest allowed versions
.PHONY: upgrade
upgrade:
	@echo "⬆️  Upgrading dependencies..."
	$(PIP_COMPILE) --upgrade -o requirements.txt pyproject.toml --resolver=backtracking
	@echo "✅ requirements.txt upgraded."

# Install: Syncs environment with locked deps and installs the app
.PHONY: install
install:
	@echo "📦 Installing dependencies..."
	$(PIP) install -r requirements.txt
	$(PIP) install -e ".[dev]"
	@echo "✅ Environment synced."

# Setup: Installs dependencies and sets up git hooks
.PHONY: setup
setup: install
	@echo "🪝 Installing Git hooks..."
	$(PRECOMMIT) install
	@echo "✅ Setup complete."

# Outdated: Checks for newer versions of dependencies
.PHONY: outdated
outdated:
	@echo "🔍 Checking for newer versions of dependencies..."
	$(PCU) pyproject.toml -t latest --extra dev --fail_on_update
	@echo "✅ Dependency outdated check passed."

# PIP Upgrade: upgrade PIP to its latest version
.PHONY: pip-upgrade
pip-upgrade:
	@echo "⬆️ Upgrading pip..."
	$(PIP) install --upgrade pip
	@echo "✅ pip upgraded."

# --- Quality Assurance (Linting & Testing) ---

# Lint: Checks code style without modifying files
.PHONY: lint
lint:
	@echo "🔍 Linting code..."
	$(RUFF) check .
	$(RUFF) format --check .
	@echo "✅ Lint check passed."

# Format: Automatically fixes code style issues
.PHONY: format
format:
	@echo "💅 Formatting code..."
	$(RUFF) check --fix .
	$(RUFF) format .
	@echo "✅ Code formatted."

# Security: Runs bandit to check for vulnerabilities
.PHONY: security
security:
	@echo "🛡️ Running security scan..."
	# -c: configuration file, -r: recursive
	$(BANDIT) -c pyproject.toml -r .
	@echo "✅ Security scan passed."

# Test: Runs the unit/integration tests
.PHONY: test
test: security
	@echo "🧪 Running tests..."
	$(PYTEST)

# SBOM: Generates Software Bill of Materials in CycloneDX JSON format
.PHONY: sbom
sbom: install
	@echo "📋 Generating SBOM..."
	$(VENV_PATH)/cyclonedx-py requirements requirements.txt -o sbom.json
	@echo "✅ SBOM generated as sbom.json"

# Audit: Generates security audit report in JSON format
.PHONY: audit
audit: install
	@echo "🔒 Running security audit..."
	$(VENV_PATH)/pip-audit --format=json --output=audit.json
	@echo "✅ Security audit saved as audit.json"

# --- Packaging & Publishing ---

# Build: Creates the distribution files (Wheel & Tarball)
.PHONY: build
build: clean install
	@echo "🏗️  Building package..."
	$(PIP) install build
	$(PYTHON) -m build
	@echo "✅ Build complete. Artifacts in dist/"

# Publish: Uploads artifacts to the repository
# Usage: make publish repo=nexus
.PHONY: publish
publish: build
	@echo "🚀 Publishing to repository..."
	# If 'repo' arg is provided, use it; otherwise default to standard upload
ifdef repo
	$(TWINE) upload --repository $(repo) dist/* --verbose > twine-publish.log 2>&1
else
	$(TWINE) upload dist/* --verbose > twine-publish.log 2>&1
endif
	@echo "✅ Published successfully."

# --- Docker Local Development ---

# Up: Starts the app locally using docker-compose
.PHONY: docker-up
docker-up:
	@echo "🐳 Starting application..."
	docker-compose up --build

# Down: Stops the app
.PHONY: docker-down
docker-down:
	docker-compose down

# --- Docker Packaging & Publishing (AWS) ---

# Docker Build: Builds the production image
.PHONY: docker-build
docker-build:
	@echo "🏗️  Building Docker image..."
	$(DOCKER) build -t $(APP_NAME):$(DOCKER_TAG) .

# Docker Run: Runs the Docker container
.PHONY: docker-run
docker-run:
	@echo "🚀 Running the Docker container..."
	touch test.db
	sqlite3 test.db ".exit"
	chmod 666 test.db
	$(DOCKER) run --rm -v ./test/resources/source_data.csv:/app/source_data.csv:ro -v ./test.db:/app/production.db:rw  $(APP_NAME):$(DOCKER_TAG)
	sqlite3 -header -column test.db "SELECT * FROM daily_sales;"
	rm -f test.db
	@echo "✅ Docker container stopped."

# ECR Login: Authenticates Docker with AWS ECR
# Java Equivalent: docker login via maven plugin
.PHONY: aws-login
aws-login:
	@echo "🔑 Logging into AWS ECR..."
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

# Publish Container: Tags and pushes to ECR
.PHONY: docker-publish
docker-publish: docker-build aws-login
	@echo "🚀 Pushing to ECR..."
	$(DOCKER) tag $(APP_NAME):$(DOCKER_TAG) $(ECR_REPO):$(DOCKER_TAG)
	$(DOCKER) push $(ECR_REPO):$(DOCKER_TAG)
	@echo "✅ Image pushed to: $(ECR_REPO):$(DOCKER_TAG)"

# --- Utilities ---

 Docs: Generates documentation from docstrings
.PHONY: docs
docs: install
	@echo "📚 Generating documentation..."
	$(VENV_PATH)/pdoc -o docs src/my_job
	@echo "✅ Documentation generated in docs/ directory"

# Clean: Removes build artifacts and caches
.PHONY: clean
clean:
	@echo "🧹 Cleaning up..."
	rm -rf docs/ dist/ build/ *.egg-info src/*.egg-info .pytest_cache .coverage test/.coverage .ruff_cache
	find . -type d -name __pycache__ -exec rm -r {} +
	@echo "✅ Clean complete."