# GitHub Secrets - Valores de Configuración

## 🔑 Account Info
- **AWS Account ID**: `471112687668`
- **Region**: `us-east-1`

---

## 📋 Secrets Actuales (DEV) - ✅ Ya Configurados

Estos secrets ya deberían estar configurados en GitHub para el ambiente de desarrollo:

### `AWS_DEPLOY_ROLE_ARN`
```
arn:aws:iam::471112687668:role/GitHubActions-SnailDoc-Deploy
```

### `FAISS_LAYER_ARN`
```
arn:aws:lambda:us-east-1:471112687668:layer:snail-bedrock-dev-faiss-layer:1
```

### `LAMBDA_URL_DEV`
```
https://whqi5eevnmoygdjyaep5fdsmma0wqgne.lambda-url.us-east-1.on.aws/
```

---

## 🚀 Secrets Requeridos para PRODUCCIÓN - ⚠️ Faltan Configurar

### Opción 1: Usar mismo AWS Account (Recomendado para empezar)

Si vas a usar la misma cuenta de AWS pero con recursos de producción separados, necesitas:

#### `AWS_DEPLOY_ROLE_ARN_PROD`

**Opción A**: Usar el mismo rol (menos seguro pero más simple):
```
arn:aws:iam::471112687668:role/GitHubActions-SnailDoc-Deploy
```

**Opción B**: Crear rol separado para producción (recomendado):
```bash
# 1. Crear trust policy (github-actions-trust-policy-prod.json)
cat > /tmp/github-actions-trust-policy-prod.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::471112687668:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:daherakel/snail-data-solutions:ref:refs/heads/main"
        }
      }
    }
  ]
}
EOF

# 2. Crear el rol
aws iam create-role \
  --role-name GitHubActions-SnailDoc-Deploy-Prod \
  --assume-role-policy-document file:///tmp/github-actions-trust-policy-prod.json \
  --description "Role for GitHub Actions to deploy Snail Doc to Production"

# 3. Attach la misma policy del rol de dev (o crear una nueva)
POLICY_ARN=$(aws iam list-policies --scope Local --query 'Policies[?contains(PolicyName, `SnailDoc`)].Arn' --output text)
aws iam attach-role-policy \
  --role-name GitHubActions-SnailDoc-Deploy-Prod \
  --policy-arn $POLICY_ARN
```

Luego usar:
```
arn:aws:iam::471112687668:role/GitHubActions-SnailDoc-Deploy-Prod
```

---

#### `FAISS_LAYER_ARN_PROD`

**Opción A**: Usar el mismo layer de dev (simple):
```
arn:aws:lambda:us-east-1:471112687668:layer:snail-bedrock-dev-faiss-layer:1
```

**Opción B**: Crear layer separado para producción (recomendado):

Primero desplegar la infraestructura de producción con Terraform:
```bash
cd modules/snail-doc/infrastructure/terraform/environments/prod
terraform init
terraform apply
```

Luego buscar el ARN del layer:
```bash
aws lambda list-layers --region us-east-1 \
  --query 'Layers[?contains(LayerName, `prod-faiss`)].LatestMatchingVersion.LayerVersionArn' \
  --output text
```

El resultado será algo como:
```
arn:aws:lambda:us-east-1:471112687668:layer:snail-bedrock-prod-faiss-layer:1
```

---

#### `LAMBDA_URL_PROD`

Este valor se obtiene **después** de desplegar la infraestructura de producción con Terraform.

```bash
# Desplegar producción primero
cd modules/snail-doc/infrastructure/terraform/environments/prod
terraform init
terraform apply

# Obtener la URL
terraform output -raw query_handler_url
```

El resultado será algo como:
```
https://XXXXXXXXXX.lambda-url.us-east-1.on.aws/
```

---

## 📝 Pasos para Configurar Secrets en GitHub

### Método 1: GitHub UI (Interfaz Web)

1. Ve a tu repositorio en GitHub
2. Settings > Secrets and variables > Actions
3. Click en "New repository secret"
4. Ingresa:
   - **Name**: (ej: `AWS_DEPLOY_ROLE_ARN_PROD`)
   - **Value**: (copia el valor de arriba)
5. Click "Add secret"

### Método 2: GitHub CLI (Terminal)

```bash
# Configurar secrets de producción
gh secret set AWS_DEPLOY_ROLE_ARN_PROD -b "arn:aws:iam::471112687668:role/GitHubActions-SnailDoc-Deploy"
gh secret set FAISS_LAYER_ARN_PROD -b "arn:aws:lambda:us-east-1:471112687668:layer:snail-bedrock-dev-faiss-layer:1"

# Este lo configuras después de desplegar prod
# gh secret set LAMBDA_URL_PROD -b "https://XXXXXXXXXX.lambda-url.us-east-1.on.aws/"
```

---

## ✅ Verificar Secrets Configurados

```bash
# Listar todos los secrets
gh secret list

# Debería mostrar:
# AWS_DEPLOY_ROLE_ARN
# AWS_DEPLOY_ROLE_ARN_PROD
# FAISS_LAYER_ARN
# FAISS_LAYER_ARN_PROD
# LAMBDA_URL_DEV
# LAMBDA_URL_PROD (después de desplegar prod)
```

---

## 🚦 Orden Recomendado de Setup

1. ✅ **Verificar secrets de DEV** (ya deberían estar)
   ```bash
   gh secret list | grep -E "(AWS_DEPLOY_ROLE_ARN|FAISS_LAYER_ARN|LAMBDA_URL_DEV)"
   ```

2. ✅ **Configurar secrets básicos de PROD** (usar valores de dev temporalmente):
   ```bash
   gh secret set AWS_DEPLOY_ROLE_ARN_PROD -b "arn:aws:iam::471112687668:role/GitHubActions-SnailDoc-Deploy"
   gh secret set FAISS_LAYER_ARN_PROD -b "arn:aws:lambda:us-east-1:471112687668:layer:snail-bedrock-dev-faiss-layer:1"
   ```

3. ✅ **Crear environment 'production' en GitHub**:
   - Settings > Environments > New environment
   - Name: `production`
   - Protection rules:
     - ✅ Required reviewers (tú mismo)
     - ✅ Wait timer: 5 minutes

4. ✅ **Descomentar environments en workflow**:
   ```bash
   # Editar .github/workflows/snail-doc-deploy-prod.yml
   # Descomentar líneas 93-95 y 250-252
   ```

5. ✅ **Desplegar infraestructura de producción**:
   ```bash
   cd modules/snail-doc/infrastructure/terraform/environments/prod
   terraform init
   terraform apply
   ```

6. ✅ **Obtener y configurar LAMBDA_URL_PROD**:
   ```bash
   LAMBDA_URL=$(terraform output -raw query_handler_url)
   gh secret set LAMBDA_URL_PROD -b "$LAMBDA_URL"
   ```

7. ✅ **Probar deployment a producción**:
   - Ve a Actions > Snail Doc - Deploy to Production
   - Run workflow
   - Type "CONFIRM"

---

## 🔍 Troubleshooting

### Error: "Context access might be invalid"
- Es solo un warning del IDE
- Se resolverá una vez que configures los secrets en GitHub

### Error: "Unable to find reusable workflow"
- Ya está arreglado ✅
- El workflow de test tiene `workflow_call` configurado

### Error: "Environment 'production' not found"
- Necesitas crear el environment en GitHub Settings > Environments

---

**Last Updated**: 2025-12-01
**Maintainer**: Snail Data Solutions
