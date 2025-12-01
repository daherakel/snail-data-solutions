# Migrar recursos existentes a IaC (Terraform)

Esta carpeta centraliza el IaC de recursos ya creados en AWS UI. No es un módulo nuevo: aquí solo declaramos e importamos lo que ya existe para mantenerlo versionado.

## Estructura propuesta
- `snail-data/terraform/` — Código Terraform raíz.
  - Archivos por dominio en raíz: `network.tf`, `security.tf`, `storage.tf`, `compute.tf`, `apigw.tf`, `apigw_stages.tf`, `iam*.tf`, `sfn.tf`, `glue.tf`, `bedrock.tf`, `provider.tf`, `variables.tf`, `versions.tf`.
  - Artefactos: `artifacts/lambda/blank.zip` placeholder para Lambdas (se ignora con `ignore_changes`).
  - Referencias/exports (solo lectura): `reference/apigw/{exports,stages}`, `reference/lambda/configs`, `reference/iam/{roles,policies/{attached,inline}}`, `reference/glue/jobs`, `reference/sfn/definitions`, con README en cada carpeta.
- Estado remoto recomendado en S3 + DynamoDB (evita tfstate local).

## Requisitos
- Terraform ≥ 1.5.
- Credenciales AWS vía perfil (`~/.aws/credentials`) o variables de entorno.

## Configurar backend de estado remoto
Backend ya creado en esta cuenta:
- Bucket S3: `snail-data-terraform-state-471112687668`
- DynamoDB lock table: `snail-data-terraform-locks`

Inicializa con:
```bash
cd snail-data/terraform
terraform init \
  -backend-config="bucket=snail-data-terraform-state-471112687668" \
  -backend-config="key=snail-data/terraform.tfstate" \
  -backend-config="region=us-east-1" \
  -backend-config="dynamodb_table=snail-data-terraform-locks"
```

Multi-región:
- `aws` (default): `us-east-1`
- `aws.use2`: `us-east-2` (para buckets como `amplify-backend-dev-98473-deployment`)

## Flujo para llevar recursos existentes a Terraform
1) Identifica el ARN o ID del recurso en AWS Console.
2) Declara un bloque mínimo en `main.tf` con el mismo nombre lógico que usarás en import (ejemplo S3):
```hcl
resource "aws_s3_bucket" "docs_bucket" {}
```
3) Importa al state:
```bash
terraform import aws_s3_bucket.docs_bucket <bucket-name>
```
4) Inspecciona el estado para generar el código:
```bash
terraform state show aws_s3_bucket.docs_bucket > snippets/docs_bucket.txt
```
5) Traslada los atributos relevantes a `main.tf` (elimina defaults generados por AWS). Luego:
```bash
terraform fmt
terraform plan
```
6) Repite por servicio (VPC/SGs, RDS, Lambda, S3, IAM, etc.). Mantén nombres con prefijos claros (ej. `snail_doc_*`, `airflow_*`).

## Organización recomendada en `main.tf`
- Secciones por servicio: VPC/red, seguridad (SG/IAM), datos (S3/RDS), cómputo (Lambda/Step Functions), observabilidad.
- Usa variables para parámetros cambiantes (ARNs externos, tamaños, rutas de código). No hardcodear ARNs de cuentas ajenas.
- Mantén `default_tags` en `provider.tf` para trazabilidad de costos.

## Validación antes de PR
- `terraform fmt`
- `terraform validate`
- `terraform plan` (incluye salida o captura de resumen en el PR; no incluyas secrets)

## Buenas prácticas específicas
- No commits de `tfstate` ni `.terraform/` (ya ignorados).
- Sin credenciales ni datos de clientes en variables por defecto.
- Para Lambdas ya desplegadas, importa primero la función y luego el alias/versionado. Para VPC, importa subnets/route tables con IDs exactos.
- Si algo no aplica a Terraform (ej. artefacto manual), documenta el gap en el PR.
