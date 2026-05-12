# =============================================================================
# Synthos Docker Makefile
# =============================================================================

# ─── Configuration ───────────────────────────────────────────────────────────
IMAGE_NAME ?= synthos
CONTAINER_NAME ?= synthos

# ─── Build ───────────────────────────────────────────────────────────────────
.PHONY: build
build:
	docker build -t $(IMAGE_NAME) .

.PHONY: build-nc
build-nc:
	docker build --no-cache -t $(IMAGE_NAME) .

# ─── Run ─────────────────────────────────────────────────────────────────────
.PHONY: run
run: check-env
	docker run -it --rm \
		-e DEEPSEEK_API_KEY \
		-e SEMANTIC_SCHOLAR_API_KEY \
		-e OPENROUTER_API_KEY \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

.PHONY: run-bg
run-bg: check-env
	docker run -d \
		-e DEEPSEEK_API_KEY \
		-e SEMANTIC_SCHOLAR_API_KEY \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME) \
		hermes gateway run

.PHONY: query
query: check-env
	docker run --rm \
		-e DEEPSEEK_API_KEY \
		-e SEMANTIC_SCHOLAR_API_KEY \
		$(IMAGE_NAME) \
		hermes chat -q "$(Q)"

# ─── Compose ─────────────────────────────────────────────────────────────────
.PHONY: up
up:
	docker compose up

.PHONY: down
down:
	docker compose down

.PHONY: logs
logs:
	docker compose logs -f

# ─── Utility ─────────────────────────────────────────────────────────────────
.PHONY: shell
shell:
	docker run -it --rm --entrypoint /bin/bash $(IMAGE_NAME)

.PHONY: check-env
check-env:
	@if [ -z "$(DEEPSEEK_API_KEY)" ]; then \
		echo "ERROR: DEEPSEEK_API_KEY not set. Run: export DEEPSEEK_API_KEY=sk-xxx"; \
		exit 1; \
	fi

.PHONY: clean
clean:
	docker rmi $(IMAGE_NAME) 2>/dev/null; true

# ─── Help ────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo "Synthos Docker Commands"
	@echo "────────────────────────"
	@echo "make build       Build the Docker image"
	@echo "make run         Interactive Hermes session"
	@echo "make query Q=... Single query (e.g. Q='Find ADHD papers')"
	@echo "make up          Docker Compose (foreground)"
	@echo "make shell       Open bash inside container"
	@echo ""
	@echo "Required: export DEEPSEEK_API_KEY=sk-xxx"
