# GitHub Actions Workflows

Automated CI/CD pipelines for Snail Data Solutions projects.

## 📁 Structure

```
.github/
├── workflows/
│   ├── snail-doc-test.yml           # Testing workflow (PR & push)
│   ├── snail-doc-deploy-dev.yml     # Dev deployment (auto on develop)
│   ├── snail-doc-deploy-prod.yml    # Prod deployment (manual/main)
│   └── snail-doc-rollback.yml       # Emergency rollback
├── CICD_SETUP.md                    # Complete setup guide
└── README.md                         # This file
```

## 🚀 Quick Start

### First Time Setup

1. **Read the complete guide**: [CICD_SETUP.md](CICD_SETUP.md)

2. **Configure AWS**:
   - Create IAM roles with OIDC
   - Get FAISS layer ARNs
   - Note Lambda URLs

3. **Set GitHub Secrets**:
   ```bash
   gh secret set AWS_DEPLOY_ROLE_ARN --body "arn:aws:iam::..."
   gh secret set FAISS_LAYER_ARN --body "arn:aws:lambda:..."
   gh secret set LAMBDA_URL_DEV --body "https://..."
   ```

4. **Test the pipeline**:
   - Create a PR → Triggers tests
   - Merge to `develop` → Deploys to Dev
   - Merge to `main` → Requires approval → Deploys to Prod

## 🔄 Workflows

### Testing (`snail-doc-test.yml`)

**Runs on**: Every PR, push to `main`/`develop`

```yaml
Jobs:
  ✓ Test query-handler (unit tests, coverage)
  ✓ Test pdf-processor (unit tests, coverage)
  ✓ Lint Python code (flake8, black, isort)
  ✓ Validate Terraform
```

### Dev Deployment (`snail-doc-deploy-dev.yml`)

**Runs on**: Push to `develop`, manual trigger

```yaml
Jobs:
  1. Run tests
  2. Build Lambda packages
  3. Deploy Lambda functions
  4. Deploy Terraform infrastructure
  5. Run smoke tests
  6. Notify status
```

### Production Deployment (`snail-doc-deploy-prod.yml`)

**Runs on**: Push to `main`, manual trigger (requires "CONFIRM")

```yaml
Jobs:
  1. Verify confirmation
  2. Run comprehensive tests
  3. Build production packages
  4. Deploy with Blue-Green strategy
  5. Run extensive smoke tests
  6. Monitor for errors (5 min)
  7. Update infrastructure
  8. Notify status
```

### Rollback (`snail-doc-rollback.yml`)

**Runs on**: Manual trigger only (requires "ROLLBACK")

```yaml
Options:
  - Environment: dev | prod
  - Type: lambda-only | infrastructure-only | full
  - Confirmation: "ROLLBACK"
```

## 🔐 Required Secrets

### Dev Environment
- `AWS_DEPLOY_ROLE_ARN`
- `FAISS_LAYER_ARN`
- `LAMBDA_URL_DEV`

### Production Environment
- `AWS_DEPLOY_ROLE_ARN_PROD`
- `FAISS_LAYER_ARN_PROD`
- `LAMBDA_URL_PROD`

See [CICD_SETUP.md](CICD_SETUP.md) for detailed setup instructions.

## 📊 Workflow Triggers

| Workflow | Trigger | When |
|----------|---------|------|
| Test | PR, push to main/develop | Automatic |
| Deploy Dev | Push to `develop` | Automatic |
| Deploy Prod | Push to `main` | Requires approval |
| Deploy Prod (manual) | Workflow dispatch | Type "CONFIRM" |
| Rollback | Workflow dispatch | Type "ROLLBACK" |

## 🎯 Deployment Flow

```
Feature Branch → PR (Tests) → Merge to develop (Deploy Dev)
                                         ↓
                            Verify in Dev environment
                                         ↓
                         Merge to main (Deploy Prod with approval)
                                         ↓
                           Monitor production metrics
```

## 🐛 Troubleshooting

**Tests failing?**
- Check Python version (3.11)
- Verify dependencies in requirements.txt
- Ensure shared/ directory is copied

**Deployment failing?**
- Verify IAM role permissions
- Check GitHub secrets are set correctly
- Review CloudWatch logs

**Need to rollback?**
- Use `snail-doc-rollback.yml` workflow
- Type "ROLLBACK" to confirm
- Select rollback type (lambda/infrastructure/full)

## 📚 Documentation

- **[Complete CI/CD Setup Guide](CICD_SETUP.md)** - Step-by-step setup
- **[Main README](../README.md)** - Project overview
- **[CLAUDE.md](../CLAUDE.md)** - Development guidelines

## 🎉 Benefits

✅ **Automated Testing** - Every PR is tested
✅ **Zero-Downtime Deployments** - Blue-Green strategy
✅ **Quick Rollbacks** - One-click rollback capability
✅ **Environment Parity** - Same process for Dev/Prod
✅ **Audit Trail** - All deployments tracked in GitHub
✅ **Smoke Tests** - Automated verification
✅ **Error Monitoring** - Automatic error detection

---

**Version**: 1.0.0
**Maintained by**: Snail Data Solutions
