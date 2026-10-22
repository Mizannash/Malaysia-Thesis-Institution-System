.PHONY: all demo test clean help

all: demo

help:
	@echo "Malaysian Thesis Institution System (MTIS) Commands:"
	@echo "  make demo   - Boot full system with zero API keys on http://localhost:3000"
	@echo "  make test   - Run all acceptance test suites"
	@echo "  make clean  - Stop all Docker containers and wipe volumes"

demo:
	@if [ ! -f .env ]; then cp .env.example .env; echo "==> Created .env from .env.example (DEMO_MODE=true)"; fi
	@echo "==> Starting MTIS multi-container stack with Docker Compose..."
	docker compose up -d db backend frontend
	@echo "==> Waiting for backend service readiness..."
	@docker compose exec backend python -c "import time, urllib.request; [time.sleep(1) for _ in range(30) if not (urllib.request.urlopen('http://localhost:8000/health').getcode() == 200 rescue None)]" 2>/dev/null || true
	@echo ""
	@echo "=========================================================="
	@echo " 🚀 MTIS IS READY (Zero API Keys Needed)"
	@echo " Web Dashboard:  http://localhost:3000"
	@echo " REST API Docs:  http://localhost:8000/docs"
	@echo ""
	@echo " Seed Demo Login Accounts:"
	@echo "   Student:    student@demo.test"
	@echo "   Supervisor: supervisor@demo.test"
	@echo "   Admin:      admin@demo.test"
	@echo "=========================================================="

test:
	@if docker compose ps 2>/dev/null | grep -q "mtis-backend-api"; then \
		echo "==> Executing acceptance tests inside running backend container..."; \
		docker compose exec backend pytest tests/acceptance/ -v; \
	elif [ -f ".venv/Scripts/pytest.exe" ]; then \
		echo "==> Executing acceptance tests via local virtual environment..."; \
		./.venv/Scripts/pytest.exe tests/acceptance/ -v; \
	elif [ -f ".venv/bin/pytest" ]; then \
		./.venv/bin/pytest tests/acceptance/ -v; \
	elif command -v pytest >/dev/null 2>&1; then \
		pytest tests/acceptance/ -v; \
	else \
		echo "==> Executing acceptance tests via Docker container run..."; \
		docker compose run --rm backend pytest tests/acceptance/ -v; \
	fi

clean:
	@echo "==> Stopping all MTIS containers and removing volumes..."
	docker compose down -v --remove-orphans
	@echo "==> Clean complete."
