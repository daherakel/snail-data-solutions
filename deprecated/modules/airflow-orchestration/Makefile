.PHONY: help start stop restart logs clean shell dbt-debug dbt-run dbt-test

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

start: ## Levantar el entorno de Airflow
	@astro dev start
	@echo ""
	@echo "✅ Servicios levantados!"
	@echo "🌐 Airflow UI: http://localhost:8080"
	@echo "👤 Usuario: admin"
	@echo "🔑 Password: admin"

stop: ## Detener el entorno
	@astro dev stop

kill: ## Detener y eliminar contenedores
	@astro dev kill

restart: ## Reiniciar el entorno
	@astro dev restart

logs: ## Ver logs de todos los servicios
	@astro dev logs

logs-scheduler: ## Ver logs del scheduler
	@astro dev logs --scheduler

logs-webserver: ## Ver logs del webserver
	@astro dev logs --webserver

clean: ## Limpiar volúmenes y datos
	@astro dev kill
	@docker volume prune -f

shell: ## Abrir shell en el scheduler
	@astro dev bash

dbt-debug: ## Ejecutar dbt debug
	@astro dev bash -c "cd include/dbt && dbt debug"

dbt-run: ## Ejecutar dbt run
	@astro dev bash -c "cd include/dbt && dbt run"

dbt-test: ## Ejecutar dbt test
	@astro dev bash -c "cd include/dbt && dbt test"

dbt-compile: ## Ejecutar dbt compile
	@astro dev bash -c "cd include/dbt && dbt compile"

pytest: ## Ejecutar tests de Airflow
	@astro dev pytest

init: start ## Inicializar el proyecto
