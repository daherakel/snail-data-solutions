# GitHub Actions Setup Instructions

## Overview
This document provides instructions to complete the CI/CD setup for the Snail Data Solutions repository.

## Issues Fixed

### ✅ Fixed: Invalid workflow file errors
- **Problem**: `secrets.LAMBDA_URL_PROD` was used in `environment.url` field, which is not allowed
- **Solution**: Commented out the `environment` blocks until they are properly created in GitHub
- **Files modified**: `.github/workflows/snail-doc-deploy-prod.yml`

## Required GitHub Configuration

### 1. Create GitHub Environments

You need to create the following environments in GitHub:

**Repository Settings > Environments > New Environment**

#### Production Environment
1. Go to: `https://github.com/YOUR_ORG/snail-data-solutions/settings/environments`
2. Click "New environment"
3. Name: `production`
4. Configure protection rules (recommended):
   - ✅ Required reviewers (at least 1)
   - ✅ Wait timer (e.g., 5 minutes)
   - ✅ Deployment branches: Only `main` branch

### 2. Configure GitHub Secrets

Add the following secrets in **Settings > Secrets and variables > Actions > New repository secret**

#### Development Secrets (already configured)
- `AWS_DEPLOY_ROLE_ARN` - IAM role ARN for dev deployments
- `FAISS_LAYER_ARN` - Lambda layer ARN for FAISS (dev)
- `LAMBDA_URL_DEV` - Lambda function URL for dev environment

#### Production Secrets (need to be added)
- `AWS_DEPLOY_ROLE_ARN_PROD` - IAM role ARN for production deployments
- `FAISS_LAYER_ARN_PROD` - Lambda layer ARN for FAISS (production)
- `LAMBDA_URL_PROD` - Lambda function URL for production environment

### 3. Uncomment Environment Blocks

After creating the `production` environment in GitHub, uncomment these lines:

**File**: `.github/workflows/snail-doc-deploy-prod.yml`

**Lines 93-95** (deploy-lambda job):
```yaml
# Uncomment environment below after creating 'production' environment in GitHub Settings > Environments
# environment:
#   name: production
```

**Lines 250-252** (deploy-infrastructure job):
```yaml
# Uncomment environment below after creating 'production' environment in GitHub Settings > Environments
# environment:
#   name: production
```

Change to:
```yaml
environment:
  name: production
```

## Verification

### Check Workflow Status
After making these changes:

1. Go to **Actions** tab in GitHub
2. Workflows should show no validation errors
3. You can manually trigger workflows using "Run workflow" button

### Test Deployment (Dev)
```bash
# Push to develop branch to trigger dev deployment
git checkout develop
git push origin develop
```

### Test Deployment (Prod)
```bash
# Push to main branch (or manual trigger) for production
git checkout main
git push origin main
```

Or use manual workflow dispatch:
1. Go to Actions > Snail Doc - Deploy to Production
2. Click "Run workflow"
3. Type "CONFIRM" in the confirmation field
4. Click "Run workflow"

## Current Workflow Status

| Workflow | Status | Notes |
|----------|--------|-------|
| `snail-doc-test.yml` | ✅ Ready | Runs on PR and push to main/develop |
| `snail-doc-deploy-dev.yml` | ✅ Ready | Auto-deploys to dev on push to develop |
| `snail-doc-deploy-prod.yml` | ⚠️ Needs setup | Requires production environment + secrets |
| `snail-doc-rollback.yml` | ✅ Ready | Manual rollback workflow |

## Warnings in IDE

You may see warnings in your IDE for these secrets:
- ⚠️ `AWS_DEPLOY_ROLE_ARN_PROD` - Context access might be invalid
- ⚠️ `FAISS_LAYER_ARN_PROD` - Context access might be invalid
- ⚠️ `LAMBDA_URL_PROD` - Context access might be invalid

**These are expected** and will resolve once you:
1. Create the secrets in GitHub (step 2 above)
2. Run the workflow at least once

## Next Steps

1. ✅ Create `production` environment in GitHub
2. ✅ Add production secrets (`AWS_DEPLOY_ROLE_ARN_PROD`, `FAISS_LAYER_ARN_PROD`, `LAMBDA_URL_PROD`)
3. ✅ Uncomment environment blocks in `snail-doc-deploy-prod.yml`
4. ✅ Test production deployment workflow
5. ✅ Configure notifications (optional - Slack/Discord/Email)

## Reference

- **GitHub Environments**: https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment
- **GitHub Secrets**: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **CI/CD Setup Guide**: `.github/CICD_SETUP.md`

---

**Last Updated**: 2025-12-01
**Maintainer**: Snail Data Solutions
