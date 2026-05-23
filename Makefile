SHELL := /bin/bash

VENV ?= .venv
HOST ?= 127.0.0.1
PORT ?= 8001
BASE_URL ?= http://$(HOST):$(PORT)

PYTHON ?= python3
ifeq ($(wildcard $(VENV)/bin/python),$(VENV)/bin/python)
PYTHON := $(VENV)/bin/python
endif

PIP := $(PYTHON) -m pip
UVICORN := $(PYTHON) -m uvicorn
ROBOT := $(PYTHON) -m robot

.PHONY: help venv install run-api run-api-dev seed check-api test test-robot test-robot-live test-robot-dry test-robot-local test-pabot lint clean clean-results reset-db

help:
	@echo "🎛️  Available targets:"
	@echo "  🐍 make venv             - create .venv if missing"
	@echo "  📦 make install          - install dependencies from req.txt"
	@echo "  🚀 make run-api          - run FastAPI app on $(HOST):$(PORT)"
	@echo "  ⚡ make run-api-dev      - run FastAPI app with --reload"
	@echo "  🌱 make seed             - seed database from CSV fixtures"
	@echo "  🔎 make check-api        - verify API is running at $(BASE_URL)"
	@echo "  🤖 make test-robot       - run Robot suites (requires API running first)"
	@echo "  🛰️  make test-robot-live  - run Robot suites (requires API running first)"
	@echo "  🧪 make test-robot-dry   - Robot dry-run validation"
	@echo "  🚦 make test-robot-local - start API, run Robot suites, stop API"
	@echo "  🧹 make lint             - basic Python syntax checks"
	@echo "  🗂️  make clean-results    - remove Robot result files"
	@echo "  🧨 make reset-db         - delete SQLite database file"
	@echo "  ✨ make clean            - clean caches and test artifacts"

venv:
	@echo "🐍 [venv] Ensuring virtual environment exists at $(VENV)"
	@-test -d $(VENV) || @python3 -m venv $(VENV)

install: venv
	@echo "📦 [install] Installing Python dependencies from req.txt"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r req.txt

run-api:
	@echo "🚀 [run-api] Starting API at $(BASE_URL)"
	@$(UVICORN) main:app --host $(HOST) --port $(PORT)

run-api-dev:
	@echo "⚡ [run-api-dev] Starting API with auto-reload at $(BASE_URL)"
	@$(UVICORN) main:app --host $(HOST) --port $(PORT) --reload

seed:
	@echo "🌱 [seed] Seeding database from CSV fixtures"
	@$(PYTHON) -m utils.seed_database

test: test-robot
	@echo "✅ [test] Completed"

check-api:
	@echo "🔎 [check-api] Verifying API availability at $(BASE_URL)"
	@curl -sf "$(BASE_URL)/" >/dev/null || (echo "❌ API is not running. Start it first: make run-api" && exit 1)

test-robot: check-api test-robot-live
	@echo "🤖 [test-robot] Robot tests completed"

test-robot-live: check-api
	@echo "🛰️  [test-robot-live] Running Robot tests against $(BASE_URL)"
	@$(ROBOT) --variable BASE_URL:$(BASE_URL) -d tests/robot/results tests/robot/suites

test-robot-dry:
	@echo "🧪 [test-robot-dry] Running Robot dry-run validation"
	@$(ROBOT) --dryrun --variable BASE_URL:$(BASE_URL) -d tests/robot/results tests/robot/suites

test-pabot: check-api
	@echo "⚡ [test-pabot] Running Robot suites in parallel with pabot (test-level split) against $(BASE_URL)"
	@$(PYTHON) -m pabot.pabot --testlevelsplit --variable BASE_URL:$(BASE_URL) -d tests/robot/results tests/robot/suites

test-robot-local:
	@set -euo pipefail; \
	@echo "🚦 [test-robot-local] Starting API on $(BASE_URL) (logs: /tmp/ecom-api.log)"; \
	@$(UVICORN) main:app --host $(HOST) --port $(PORT) >/tmp/ecom-api.log 2>&1 & \
	API_PID=$$!; \
	@echo "⏳ [test-robot-local] Waiting for API health endpoint"; \
	trap 'kill $$API_PID >/dev/null 2>&1 || true' EXIT INT TERM; \
	for i in {1..30}; do \
		if curl -sf "$(BASE_URL)/" >/dev/null; then break; fi; \
		sleep 1; \
		if [ $$i -eq 30 ]; then echo "API did not start in time"; exit 1; fi; \
	done; \
	@echo "🎯 [test-robot-local] API is up, running Robot suites"; \
	@$(ROBOT) --variable BASE_URL:$(BASE_URL) -d tests/robot/results tests/robot/suites

lint:
	@echo "🧹 [lint] Running Python syntax checks"
	@$(PYTHON) -m py_compile main.py db.py models/*.py routes/*.py utils/*.py

clean-results:
	@echo "🗂️  [clean-results] Removing Robot output files"
	@rm -rf tests/robot/results/*

reset-db:
	@echo "🧨 [reset-db] Removing SQLite database file"
	@rm -f database.db

clean: clean-results
	@echo "✨ [clean] Removing Python cache artifacts"
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
