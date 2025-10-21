# ====== Project Setup ======
PROJECT_NAME := palabra
DOCKER_COMPOSE := docker-compose
PYTHON_WORKER_SERVICE := rq-worker
PYTHON_API_SERVICE := worker-api
DBMATE_SERVICE := palabra_dbmate
MIGRATIONS_DIR := ./services/api/db/migrations

# ====== General ======
.PHONY: up down restart build logs shell worker-shell api-shell ps clean dbshell migrate create-migration rollback seed

## 🟢 Bring up the full environment
up:
	$(DOCKER_COMPOSE) up --build -d
	@echo "✅ $(PROJECT_NAME) environment started"

## 🔴 Stop all containers
down:
	$(DOCKER_COMPOSE) down
	@echo "🧹 Environment stopped"

## ♻️ Restart containers
restart:
	$(DOCKER_COMPOSE) down && $(DOCKER_COMPOSE) up -d
	@echo "🔄 Restarted containers"

## 🧱 Rebuild all Docker images
build:
	$(DOCKER_COMPOSE) build --no-cache
	@echo "🏗️ Rebuilt Docker images"

## 📜 Tail all logs (Ctrl+C to exit)
logs:
	$(DOCKER_COMPOSE) logs -f

## 🧩 Show container status
ps:
	$(DOCKER_COMPOSE) ps

## 🧑‍💻 Shell into the main worker container
worker-shell:
	$(DOCKER_COMPOSE) exec $(PYTHON_WORKER_SERVICE) bash || $(DOCKER_COMPOSE) run --rm $(PYTHON_WORKER_SERVICE) bash

## 🧑‍💻 Shell into the worker API container
api-shell:
	$(DOCKER_COMPOSE) exec $(PYTHON_API_SERVICE) bash || $(DOCKER_COMPOSE) run --rm $(PYTHON_API_SERVICE) bash

## 💻 Open a Postgres shell
dbshell:
	$(DOCKER_COMPOSE) exec postgres psql -U palabra -d palabra

## 🧼 Remove all containers, volumes, and networks
clean:
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@echo "🧽 Cleaned up all containers, networks, and volumes"


# ====== Database Migrations ======

## 🧩 Create a new migration
create-migration:
	@if [ -z "$(name)" ]; then \
		echo "❌ Please provide a migration name, e.g. 'make create-migration name=add_users_table'"; \
		exit 1; \
	fi
	$(DOCKER_COMPOSE) run --rm dbmate new $(name)
	@echo "✅ Created new migration: $(name)"

## 🚀 Apply all pending migrations
migrate:
	$(DOCKER_COMPOSE) run --rm dbmate up
	@echo "✅ Applied all pending migrations"

## ⏪ Roll back the last migration
rollback:
	$(DOCKER_COMPOSE) run --rm dbmate down
	@echo "↩️ Rolled back the last migration"


# ====== Data Management ======

## 🌱 Seed the database (build + load lemma dataset)
seed:
	$(DOCKER_COMPOSE) run --rm $(PYTHON_WORKER_SERVICE) python -m worker.tasks.build_dataset
	$(DOCKER_COMPOSE) run --rm $(PYTHON_WORKER_SERVICE) python -m worker.tasks.load_dataset
	@echo "✅ Database seeded with language dataset"
