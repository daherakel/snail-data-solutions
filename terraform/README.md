# Terraform Cloud POC (S3)

POC minima para crear un bucket S3 en `us-east-1`. Por ahora corre local, con opcion de mover a Terraform Cloud.

## Requisitos
- Terraform >= 1.5
- AWS CLI o variables de entorno (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` opcional)

## Uso rapido
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Variables
- `bucket_name` tiene default en `variables.tf` (`bucket-poc-1`). Cambialo si el nombre ya existe en S3.
- Si preferis, podes usar `terraform.tfvars` en lugar del default.

## Terraform Cloud (opcional)
Cuando quieras usar Terraform Cloud, descomenta el bloque `cloud` en `versions.tf` y configura tu organizacion/workspace.
