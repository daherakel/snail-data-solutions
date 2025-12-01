# Repository Guidelines

## Project Structure & Modules
- Monorepo con módulos listos para deploy en `modules/`: `snail-doc/` (Next.js + Terraform + Lambdas), `airflow-orchestration/` (DAGs en `dags/`, dbt/config en `include/`, tests en `tests/`), y `contact-lambda/`.
- Infra importada desde la consola AWS vive en `snail-data/terraform/`: proveedores en `provider.tf`, recursos por servicio en los `.tf` raíz, artefactos de Lambda en `artifacts/`, snapshots de referencia en `reference/`.
- Documentación compartida en `docs/`; lineamientos para agentes y contribución en `CLAUDE.md`.

## Build, Test, and Development Commands
- Snail Doc: `cd modules/snail-doc && ./scripts/deploy.sh dev`; `./scripts/upload-document.sh dev file.pdf`; `./scripts/test-query.sh dev "pregunta"`.
- Airflow: `cd modules/airflow-orchestration && make start` / `make stop`; `make dbt-run`, `make dbt-test`, `make pytest` (UI local http://localhost:8080, admin/admin).
- IaC (snail-data): `cd snail-data/terraform && terraform init` (backend remoto listo) y `terraform plan` para validar drift; no aplicar sin coordinación.

## Coding Style & Naming
- Usa `terraform fmt`; 2 espacios en JS/TS/JSON/YAML; Python estilo black/PEP8. Mantén los nombres existentes (`snail-bedrock-*`, `ahh_*`, `airflow_*`) y evita renombrar recursos importados.
- Agrupa assets por servicio (p. ej., referencias en `reference/apigw|iam|lambda`, artefactos en `artifacts/`). Si agregas nuevas Lambdas importadas, deja `artifacts/lambda/blank.zip` como placeholder.
- Cero secretos en código; usa variables, SSM/Secrets Manager y configura `AWS_PROFILE`/`AWS_REGION` en tu entorno.

## Testing Expectations
- Infra: siempre `terraform plan` antes de mergear y adjunta el resumen en el PR. Respeta `prevent_destroy` y `ignore_changes` para no recrear recursos importados.
- Código: tests cerca del código (Airflow en `modules/airflow-orchestration/tests/`, Lambdas con pytest u otro runner adyacente). Nombra tests `test_*.py`.
- Cambios en RAG/LLM (`snail-doc`): corre `./scripts/test-query.sh` y comparte la salida como smoke test.

## Commit & Pull Request Guidelines
- Commits cortos en imperativo con alcance (`snail-doc: ...`, `airflow: ...`, `iac: ...`); evita mezclar refactors grandes con fixes.
- PRs: resumen claro, issue/enlace, comandos ejecutados (`terraform plan`, `make pytest`, etc.) y evidencia (logs/capturas/respuestas). Señala cambios IAM/seguridad o nuevas vars/secretos requeridos.

## Security & Config Hygiene
- Principio de mínimo privilegio; no remuevas `prevent_destroy` ni cambies tags heredadas sin acuerdo. Usa `ignore_changes` para respetar el estado actual y evitar reprovisionar.
- Sanitiza logs (sin PII) y evita subir dumps o datasets grandes; revisa rutas/artefactos S3/layers antes de commitear.
