# AGENTS.md

## Contexto
Carpeta `terraform/` creada para una POC local de Terraform que provisiona un bucket S3 en `us-east-1`. La configuracion esta preparada para moverse a Terraform Cloud cuando se necesite.

## Que se hizo
- Estructura minima de Terraform:
  - `versions.tf` con providers y bloque `cloud` comentado.
  - `main.tf` con provider AWS y recurso `aws_s3_bucket`.
  - `variables.tf` con defaults (incluye `bucket_name = "bucket-poc-1"`).
  - `outputs.tf` con `bucket_name` y `bucket_arn`.
  - `terraform.tfvars.example` como referencia.
  - `README.md` con pasos de uso local y nota para Terraform Cloud.

## Uso local rapido
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Notas
- El nombre del bucket debe ser unico global en S3. Si `bucket-poc-1` ya existe, cambiar el default en `variables.tf`.
- Para usar Terraform Cloud, descomentar el bloque `cloud` en `versions.tf` y configurar organizacion/workspace.
