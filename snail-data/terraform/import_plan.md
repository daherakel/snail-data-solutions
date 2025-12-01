# Plan de importación Terraform (us-east-1, perfil `default`)

Ya se inventariaron recursos en la cuenta `471112687668` con perfil `default` y región `us-east-1`. Usa este plan como checklist para declarar en `main.tf` y luego importar.

Backend remoto configurado:
- S3 bucket: `snail-data-terraform-state-471112687668`
- DynamoDB lock table: `snail-data-terraform-locks`
- State key: `snail-data/terraform.tfstate`

Importes ya ejecutados (archivos en `services/`, snapshots en `reference/`):
- VPC `vpc-02c36d47d8c7216f3`, subnets públicas A-F, route table `rtb-06ab9a1153e1184aa`.
- Buckets importados: todos los listados (incluye `amplify-backend-dev-98473-deployment` en `us-east-2` vía provider alias).
- Security groups importados: `sg-025175389718d9e9d` (default), `sg-07f810fbfa7082ebb`, `sg-0788f4d055d291699`, `sg-0c019bcf557e6c712`, `sg-026f70d083cadee67`, `sg-000bae9b88eb5ab27`, `sg-0828d54864499e74b`, `sg-05e039398aef25553`.
- Step Functions importada: `snail-bedrock-dev-document-processing` (definición en `state_machines/snail-bedrock-dev-document-processing.asl.json`).
- API Gateway REST importadas: `208hokbs1g` (ahh_get_mp3), `2wvwse9yvb` (ahh_process_mp3), `45popfs293` (ahh_notes_api), `hwb5xmz2a1` (ipoc_snail), `pi7aucalk6` (ahh_api), `ppaxiqr0n7` (iphone_store).
- Lambdas importadas: todas las listadas en `compute.tf` (23 funciones, us-east-1) con placeholder de código `files/blank.zip` y `ignore_changes` para código/entorno.
- IAM roles importados: AHH_* roles, ibold-price-detector role, y roles snail-bedrock dev (eventbridge, lambda-* y step-functions). Policies adjuntas e inline importadas (ver `iam_attachments.tf`, `iam_inline.tf`).
- Glue jobs importados: `CDC`, `csv-to-tabla`.
- Bedrock Agents: importados `ibold-agent-providers` (B7QHIU3JYR), `ibold-agent-stock` (GEWDZTHJTJ) y `snail-agent` (JJKN86AJCY). `ibold-supervisor-agent` pendiente por bug del provider AWS (segfault en `aws_bedrockagent_agent` al refrescar); reintentar con versión futura.

## Recursos detectados
- S3 buckets: `ahh-audio-bucket`, `ahh-healthscribe-output`, `ahh-transcribe-demo`, `amazon-sagemaker-471112687668-us-east-1-49dadeb59b4a`, `amplify-backend-dev-98473-deployment`, `aws-glue-assets-471112687668-us-east-1`, `dycom-poc`, `glue-snail-bucket`, `knowledge-base-snail`, `s3-snail-landing`, `snail-athena-output`, `snail-bedrock-dev-chromadb-backup`, `snail-bedrock-dev-processed-documents`, `snail-bedrock-dev-raw-documents`, `snail-lambda-layers-1763961583`, `snail-rds-snapshots`.
- Red: VPC `vpc-02c36d47d8c7216f3` (172.31.0.0/16) con subnets públicas `subnet-0fac62568c4102bff` (us-east-1a, 172.31.80.0/20), `subnet-04aa9a75c98e1c53d` (1d, 172.31.0.0/20), `subnet-02ada0315d78d31f5` (1b, 172.31.16.0/20), `subnet-097527ec7ada3dbe2` (1c, 172.31.32.0/20), `subnet-021311941cf3dd79d` (1f, 172.31.64.0/20), `subnet-0141054d8c979351e` (1e, 172.31.48.0/20). Route table `rtb-06ab9a1153e1184aa`.
- Security groups: `sg-025175389718d9e9d` (default), `sg-07f810fbfa7082ebb` (EMR master), `sg-0788f4d055d291699` (EMR slave), `sg-0c019bcf557e6c712`/`sg-026f70d083cadee67` (SageMaker NFS), `sg-000bae9b88eb5ab27` (Aurora Bedrock Quick Create), `sg-0828d54864499e74b` (sqless-sg-poc-test), `sg-05e039398aef25553` (datazone...), etc.
- Lambdas (nombre/runtime): see `aws lambda list-functions` output; incluye `snail-bedrock-dev-slack-handler`, `snail-bedrock-dev-query-handler`, `snail-bedrock-dev-pdf-processor`, `AHH_*`, `ibold-*`, `NLQ-Lambda`, `TriggerGlueJobFromS3`, etc.
- API Gateway REST: `208hokbs1g` (AHH_GET_MP3), `2wvwse9yvb` (AHH_PROCESS_MP3), `45popfs293` (AHH_NOTES_API), `hwb5xmz2a1` (IPOC-SNAIL), `pi7aucalk6` (AHH_API), `ppaxiqr0n7` (iphone-store).
- Step Functions: `snail-bedrock-dev-document-processing`.
- Glue jobs: `CDC`, `csv-to-tabla`.
- IAM roles (relacionados): `snail-bedrock-dev-*`, `AHH_*`, `ibold-*` (ver `aws iam list-roles` filtro).

Notas:
- Bucket `amplify-backend-dev-98473-deployment` no se encontró en us-east-1; no se importó ni se mantiene en `main.tf` para evitar creación accidental.

## Sugerencia de nombres Terraform
- Prefijos: `s3_` para buckets (`aws_s3_bucket.s3_snail_bedrock_dev_raw_documents`), `vpc_main`, `subnet_public_a`...`f`, `rtb_main`, `sg_emr_master`, etc.
- Para Lambdas, usa `aws_lambda_function.<function_name_normalizado>` (ej. `aws_lambda_function.snail_bedrock_dev_pdf_processor`).

## Comandos de importación (ejemplos)
Declara primero los recursos mínimos en `main.tf` (ej., S3 con `bucket = "<nombre>"`, VPC con `cidr_block`). Luego importa:
```bash
# S3 (ejemplos)
terraform import aws_s3_bucket.s3_snail_bedrock_dev_raw_documents snail-bedrock-dev-raw-documents
terraform import aws_s3_bucket.s3_snail_bedrock_dev_processed_documents snail-bedrock-dev-processed-documents
terraform import aws_s3_bucket.s3_snail_bedrock_dev_chromadb_backup snail-bedrock-dev-chromadb-backup
terraform import aws_s3_bucket.s3_snail_athena_output snail-athena-output

# Red
terraform import aws_vpc.vpc_main vpc-02c36d47d8c7216f3
terraform import aws_subnet.subnet_public_a subnet-0fac62568c4102bff
terraform import aws_subnet.subnet_public_b subnet-02ada0315d78d31f5
terraform import aws_subnet.subnet_public_c subnet-097527ec7ada3dbe2
terraform import aws_subnet.subnet_public_d subnet-04aa9a75c98e1c53d
terraform import aws_subnet.subnet_public_e subnet-0141054d8c979351e
terraform import aws_subnet.subnet_public_f subnet-021311941cf3dd79d
terraform import aws_route_table.rtb_main rtb-06ab9a1153e1184aa

# Security groups (ejemplo)
terraform import aws_security_group.sg_default sg-025175389718d9e9d

# Step Functions
terraform import aws_sfn_state_machine.snail_bedrock_dev_document_processing arn:aws:states:us-east-1:471112687668:stateMachine:snail-bedrock-dev-document-processing

# API Gateway REST
terraform import aws_api_gateway_rest_api.ipoc_snail hwb5xmz2a1

# Lambdas (importa una por una)
terraform import aws_lambda_function.snail_bedrock_dev_query_handler arn:aws:lambda:us-east-1:471112687668:function:snail-bedrock-dev-query-handler
terraform import aws_lambda_function.snail_bedrock_dev_pdf_processor arn:aws:lambda:us-east-1:471112687668:function:snail-bedrock-dev-pdf-processor
terraform import aws_lambda_function.snail_bedrock_dev_slack_handler arn:aws:lambda:us-east-1:471112687668:function:snail-bedrock-dev-slack-handler

# Step Functions
terraform import aws_sfn_state_machine.snail_bedrock_dev_document_processing arn:aws:states:us-east-1:471112687668:stateMachine:snail-bedrock-dev-document-processing
```

Tras cada import:
```bash
terraform state show <addr> > snapshots/<addr>.txt
```
Usa esas salidas para poblar atributos en `main.tf` (handler, role, runtime, policies, etc.). Mantén `lifecycle { prevent_destroy = true }` mientras migras.

## Pendientes/decisiones
- Crear backend remoto (S3 + DynamoDB) y hacer `terraform init` con esos nombres.
- Definir qué Lambdas y APIs siguen vigentes para incluirlas; evita importar recursos obsoletos.
- Añadir SG rules, asociaciones de route tables y roles/policies una vez que los `state show` estén capturados.
