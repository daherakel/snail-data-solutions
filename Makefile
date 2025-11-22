.PHONY: help build up down restart logs clean test dbt-debug dbt-run dbt-test

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Construir las imágenes de Docker
	docker-compose build

up: ## Levantar todos los servicios
	docker-compose up -d
	@echo "Esperando a que los servicios estén listos..."
	@sleep 10
	@echo ""
	@echo "✅ Servicios levantados!"
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "👤 Usuario: airflow"
	@echo "🔑 Password: airflow"
	@echo ""
	@echo "📊 PostgreSQL disponible en localhost:5432"

down: ## Detener todos los servicios
	docker-compose down

restart: ## Reiniciar todos los servicios
	docker-compose restart

logs: ## Ver logs de todos los servicios
	docker-compose logs -f

logs-scheduler: ## Ver logs del scheduler
	docker-compose logs -f airflow-scheduler

logs-webserver: ## Ver logs del webserver
	docker-compose logs -f airflow-webserver

clean: ## Limpiar volúmenes y datos
	docker-compose down -v
	rm -rf logs/

shell-scheduler: ## Abrir shell en el scheduler
	docker-compose exec airflow-scheduler bash

shell-webserver: ## Abrir shell en el webserver
	docker-compose exec airflow-webserver bash

shell-db: ## Abrir shell de PostgreSQL
	docker-compose exec postgres psql -U airflow -d airflow

dbt-debug: ## Ejecutar dbt debug
	docker-compose exec airflow-scheduler bash -c "cd include/dbt && dbt debug"

dbt-run: ## Ejecutar dbt run
	docker-compose exec airflow-scheduler bash -c "cd include/dbt && dbt run"

dbt-test: ## Ejecutar dbt test
	docker-compose exec airflow-scheduler bash -c "cd include/dbt && dbt test"

dbt-compile: ## Ejecutar dbt compile
	docker-compose exec airflow-scheduler bash -c "cd include/dbt && dbt compile"

trigger-default: ## Trigger del DAG default
	docker-compose exec airflow-scheduler airflow dags trigger default_dag

test: ## Ejecutar tests de Airflow
	docker-compose exec airflow-scheduler pytest /usr/local/airflow/tests

init: build up ## Inicializar el proyecto (build + up)
