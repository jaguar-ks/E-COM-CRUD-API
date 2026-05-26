VENV ?= .venv
HOST ?= 127.0.0.1
PORT ?= 8000
BASE_URL ?= http://$(HOST):$(PORT)

PYTHON ?= python3
ifeq ($(wildcard $(VENV)/bin/python),$(VENV)/bin/python)
PYTHON := $(VENV)/bin/python
endif

PIP := $(PYTHON) -m pip
UVICORN := $(PYTHON) -m uvicorn
ROBOT := $(PYTHON) -m robot
CI_API_LOG ?= api.log
CI_API_PID ?= api.pid
CI_API_URL ?= $(BASE_URL)

RESET := \033[0m
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m

.PHONY: help venv install run-api run-api-dev seed check-api test test-robot test-robot-live test-robot-dry test-pabot lint clean clean-results reset-db ci-setup ci-build ci-api-start ci-api-wait ci-api-stop ci-e2e test-robot-local

help:
	@printf "$(CYAN)🎛️  Available targets:$(RESET)\n"
	@printf "$(BLUE)  🐍 make venv$(RESET)             - create .venv if missing\n"
	@printf "$(BLUE)  📦 make install$(RESET)          - install dependencies from req.txt\n"
	@printf "$(BLUE)  🚀 make run-api$(RESET)          - run FastAPI app on $(HOST):$(PORT)\n"
	@printf "$(BLUE)  ⚡ make run-api-dev$(RESET)      - run FastAPI app with --reload\n"
	@printf "$(BLUE)  🌱 make seed$(RESET)             - seed database from CSV fixtures\n"
	@printf "$(BLUE)  🔎 make check-api$(RESET)        - verify API is running at $(BASE_URL)\n"
	@printf "$(BLUE)  🤖 make test-robot$(RESET)       - run Robot suites (requires API running first)\n"
	@printf "$(BLUE)  🛰️  make test-robot-live$(RESET)  - run Robot suites (requires API running first)\n"
	@printf "$(BLUE)  🧪 make test-robot-dry$(RESET)   - Robot dry-run validation\n"
	@printf "$(BLUE)  🚦 make test-robot-local$(RESET) - start API, run Robot suites, stop API\n"
	@printf "$(BLUE)  🧹 make lint$(RESET)             - basic Python syntax checks\n"
	@printf "$(BLUE)  🛠️  make ci-build$(RESET)         - install deps, syntax check, Robot dry-run\n"
	@printf "$(BLUE)  🚀 make ci-api-start$(RESET)      - start API in the background for CI\n"
	@printf "$(BLUE)  🔎 make ci-api-wait$(RESET)       - wait for API health in CI\n"
	@printf "$(BLUE)  🧯 make ci-api-stop$(RESET)       - stop CI API process and dump logs\n"
	@printf "$(BLUE)  🤖 make ci-e2e$(RESET)            - run API-backed Robot E2E workflow\n"
	@printf "$(BLUE)  🗂️  make clean-results$(RESET)    - remove Robot result files\n"
	@printf "$(BLUE)  🧨 make reset-db$(RESET)         - delete SQLite database file\n"
	@printf "$(BLUE)  ✨ make clean$(RESET)            - clean caches and test artifacts\n"

venv:
	@printf "$(GREEN)🐍 [venv] Ensuring virtual environment exists at $(VENV)$(RESET)\n"
	@-test -d $(VENV) || @python3 -m venv $(VENV)

install: venv
	@printf "$(GREEN)📦 [install] Installing Python dependencies from req.txt$(RESET)\n"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r req.txt

ci-setup:
	@printf "$(GREEN)📦 [ci-setup] Installing Python dependencies from req.txt$(RESET)\n"
	@$(PIP) install --upgrade pip
	@$(PIP) install -r req.txt

run-api:
	@printf "$(GREEN)🚀 [run-api] Starting API at $(BASE_URL)$(RESET)\n"
	@$(UVICORN) main:app --host $(HOST) --port $(PORT)

run-api-dev:
	@printf "$(GREEN)⚡ [run-api-dev] Starting API with auto-reload at $(BASE_URL)$(RESET)\n"
	@$(UVICORN) main:app --host $(HOST) --port $(PORT) --reload

seed:
	@printf "$(GREEN)🌱 [seed] Seeding database from CSV fixtures$(RESET)\n"
	@$(PYTHON) -m utils.seed_database

test: test-robot
	@printf "$(GREEN)✅ [test] Completed$(RESET)\n"

check-api:
	@printf "$(CYAN)🔎 [check-api] Verifying API availability at $(BASE_URL)$(RESET)\n"
	@curl -sf "$(BASE_URL)/" >/dev/null || (printf "$(RED)❌ API is not running. Start it first: make run-api$(RESET)\n" && exit 1)

test-robot: check-api test-robot-live
	@printf "$(GREEN)🤖 [test-robot] Robot tests completed$(RESET)\n"

test-robot-live: check-api
	@printf "$(MAGENTA)🛰️  [test-robot-live] Running Robot tests against $(BASE_URL)$(RESET)\n"
	@$(ROBOT) --variable BASE_URL:$(BASE_URL) --xunit xunit.xml -d tests/robot/results tests/robot/suites

test-robot-dry:
	@printf "$(MAGENTA)🧪 [test-robot-dry] Running Robot dry-run validation$(RESET)\n"
	@$(ROBOT) --dryrun --variable BASE_URL:$(BASE_URL) --xunit xunit.xml -d tests/robot/results tests/robot/suites

test-pabot: check-api
	@printf "$(MAGENTA)⚡ [test-pabot] Running Robot suites in parallel with pabot (test-level split) against $(BASE_URL)$(RESET)\n"
	@$(PYTHON) -m pabot.pabot --testlevelsplit --variable BASE_URL:$(BASE_URL) -d tests/robot/results tests/robot/suites

lint:
	@printf "$(CYAN)🧹 [lint] Running Python syntax checks$(RESET)\n"
	@$(PYTHON) -m py_compile main.py models/*.py routes/*.py utils/*.py

ci-build: ci-setup lint
	@printf "$(GREEN)🧱 [ci-build] Running Robot dry-run validation$(RESET)\n"
	@$(ROBOT) --dryrun --variable BASE_URL:$(BASE_URL) -d tests/robot/results tests/robot/suites

ci-api-start: ci-setup
	@printf "$(GREEN)🚀 [ci-api-start] Starting API at $(CI_API_URL)$(RESET)\n"
	@$(UVICORN) main:app --host $(HOST) --port $(PORT) > $(CI_API_LOG) 2>&1 & echo $$! > $(CI_API_PID)

ci-api-wait:
	@printf "$(CYAN)🔎 [ci-api-wait] Waiting for API at $(CI_API_URL)$(RESET)\n"
	@CI_API_URL="$(CI_API_URL)" $(PYTHON) -m utils.ci_wait_for_api

ci-api-stop:
	@printf "$(CYAN)🧯 [ci-api-stop] Stopping API$(RESET)\n"
	@-if [ -f $(CI_API_PID) ]; then kill "$$(cat $(CI_API_PID))" || true; fi
	@-tail -n 200 $(CI_API_LOG) || true

ci-e2e: ci-api-start ci-api-wait
	@printf "$(MAGENTA)🤖 [ci-e2e] Running Robot suites against $(CI_API_URL)$(RESET)\n"
	@$(ROBOT) --variable BASE_URL:$(CI_API_URL) --xunit xunit.xml -d tests/robot/results tests/robot/suites
	@$(MAKE) ci-api-stop

test-robot-local: ci-e2e
	@printf "$(GREEN)🚦 [test-robot-local] Completed$(RESET)\n"

clean-results:
	@printf "$(CYAN)🗂️  [clean-results] Removing Robot output files$(RESET)\n"
	@rm -rf tests/robot/results/*

reset-db:
	@printf "$(RED)🧨 [reset-db] Removing SQLite database file$(RESET)\n"
	@rm -f database.db

clean: clean-results
	@printf "$(CYAN)✨ [clean] Removing Python cache artifacts$(RESET)\n"
	@find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
