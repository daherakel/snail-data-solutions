# CI/CD Setup Guide - Snail Data Solutions

Complete guide to setting up GitHub Actions CI/CD for the Snail Doc module.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [AWS Setup](#aws-setup)
- [GitHub Secrets Configuration](#github-secrets-configuration)
- [Workflows Overview](#workflows-overview)
- [Deployment Process](#deployment-process)
- [Rollback Procedure](#rollback-procedure)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The CI/CD pipeline automates:
- ✅ Testing (linting, unit tests, integration tests)
- ✅ Building Lambda deployment packages
- ✅ Deploying to Dev environment (automatic on `develop` branch)
- ✅ Deploying to Production (manual approval on `main` branch)
- ✅ Terraform infrastructure updates
- ✅ Blue-Green deployments for zero-downtime
- ✅ Automated rollback capabilities

---

## 📦 Prerequisites

### 1. GitHub Repository Setup

Ensure you have:
- Admin access to the repository
- Ability to create GitHub Actions secrets
- Protected branches configured:
  - `main` - Production deployments
  - `develop` - Dev deployments

### 2. AWS Accounts

You need:
- AWS account for Dev environment
- AWS account for Production environment (can be same account, different region/naming)
- IAM permissions to create roles

### 3. Tools Required

- AWS CLI configured locally
- Terraform CLI (v1.6.0+)
- GitHub CLI (optional, for easier secret management)

---

## ☁️ AWS Setup

### Step 1: Create IAM Role for GitHub Actions (Dev)

Create a role that GitHub Actions can assume using OIDC.

**1.1. Create Trust Policy** (`github-actions-trust-policy-dev.json`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::YOUR_AWS_ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_ORG/YOUR_REPO:ref:refs/heads/develop"
        }
      }
    }
  ]
}
```

**1.2. Create the role:**

```bash
aws iam create-role \
  --role-name GitHubActionsSnailDocDev \
  --assume-role-policy-document file://github-actions-trust-policy-dev.json \
  --description "Role for GitHub Actions to deploy Snail Doc to Dev"
```

**1.3. Attach permissions policy** (`github-actions-permissions-dev.json`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:UpdateFunctionConfiguration",
        "lambda:GetFunction",
        "lambda:PublishVersion",
        "lambda:UpdateAlias",
        "lambda:GetAlias",
        "lambda:CreateAlias"
      ],
      "Resource": [
        "arn:aws:lambda:us-east-1:*:function:snail-bedrock-dev-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::snail-bedrock-dev-*",
        "arn:aws:s3:::snail-bedrock-dev-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:DescribeTable",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan",
        "dynamodb:Query"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-east-1:*:table/snail-bedrock-dev-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "states:DescribeStateMachine",
        "states:UpdateStateMachine"
      ],
      "Resource": [
        "arn:aws:states:us-east-1:*:stateMachine:snail-bedrock-dev-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:DescribeRule",
        "events:PutRule",
        "events:PutTargets"
      ],
      "Resource": [
        "arn:aws:events:us-east-1:*:rule/snail-bedrock-dev-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:GetRole",
        "iam:PassRole"
      ],
      "Resource": [
        "arn:aws:iam::*:role/snail-bedrock-dev-*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricStatistics"
      ],
      "Resource": "*"
    }
  ]
}
```

```bash
aws iam put-role-policy \
  --role-name GitHubActionsSnailDocDev \
  --policy-name DeploymentPermissions \
  --policy-document file://github-actions-permissions-dev.json
```

**1.4. Get the Role ARN:**

```bash
aws iam get-role \
  --role-name GitHubActionsSnailDocDev \
  --query 'Role.Arn' \
  --output text
```

Save this ARN - you'll need it for GitHub secrets.

### Step 2: Create IAM Role for Production

Repeat Step 1 for production, but:
- Change role name to `GitHubActionsSnailDocProd`
- Update trust policy to allow `refs/heads/main`
- Update resource ARNs to use `snail-bedrock-prod-*`

### Step 3: Create OIDC Provider (if not exists)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### Step 4: Get FAISS Layer ARN

```bash
# Dev
aws lambda list-layers \
  --query 'Layers[?LayerName==`snail-bedrock-dev-faiss-layer`].LatestMatchingVersion.LayerVersionArn' \
  --output text

# Prod
aws lambda list-layers \
  --query 'Layers[?LayerName==`snail-bedrock-prod-faiss-layer`].LatestMatchingVersion.LayerVersionArn' \
  --output text
```

---

## 🔐 GitHub Secrets Configuration

Go to your GitHub repository → Settings → Secrets and variables → Actions

### Required Secrets

#### For DEV Environment:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `AWS_DEPLOY_ROLE_ARN` | `arn:aws:iam::ACCOUNT:role/GitHubActionsSnailDocDev` | From Step 1.4 above |
| `FAISS_LAYER_ARN` | `arn:aws:lambda:us-east-1:ACCOUNT:layer:snail-bedrock-dev-faiss-layer:1` | From Step 4 above |
| `LAMBDA_URL_DEV` | `https://xxxxx.lambda-url.us-east-1.on.aws/` | Terraform output: `query_handler_url` |

#### For PROD Environment:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `AWS_DEPLOY_ROLE_ARN_PROD` | `arn:aws:iam::ACCOUNT:role/GitHubActionsSnailDocProd` | From Step 2 above |
| `FAISS_LAYER_ARN_PROD` | `arn:aws:lambda:us-east-1:ACCOUNT:layer:snail-bedrock-prod-faiss-layer:1` | From Step 4 above |
| `LAMBDA_URL_PROD` | `https://yyyyy.lambda-url.us-east-1.on.aws/` | Terraform output: `query_handler_url` |

### Setting Secrets via GitHub CLI

```bash
# Dev secrets
gh secret set AWS_DEPLOY_ROLE_ARN --body "arn:aws:iam::ACCOUNT:role/GitHubActionsSnailDocDev"
gh secret set FAISS_LAYER_ARN --body "arn:aws:lambda:us-east-1:ACCOUNT:layer:snail-bedrock-dev-faiss-layer:1"
gh secret set LAMBDA_URL_DEV --body "https://xxxxx.lambda-url.us-east-1.on.aws/"

# Prod secrets
gh secret set AWS_DEPLOY_ROLE_ARN_PROD --body "arn:aws:iam::ACCOUNT:role/GitHubActionsSnailDocProd"
gh secret set FAISS_LAYER_ARN_PROD --body "arn:aws:lambda:us-east-1:ACCOUNT:layer:snail-bedrock-prod-faiss-layer:1"
gh secret set LAMBDA_URL_PROD --body "https://yyyyy.lambda-url.us-east-1.on.aws/"
```

---

## 🔄 Workflows Overview

### 1. `snail-doc-test.yml`

**Trigger**: Pull requests and pushes to `main`/`develop`

**What it does**:
- Runs unit tests for query-handler and pdf-processor
- Lints Python code (flake8, black, isort)
- Validates Terraform configuration
- Uploads code coverage to Codecov

**When to use**: Automatic on every PR

### 2. `snail-doc-deploy-dev.yml`

**Trigger**: Push to `develop` branch or manual workflow dispatch

**What it does**:
1. Runs tests (can be skipped)
2. Builds Lambda deployment packages
3. Deploys to Dev environment
4. Runs smoke tests
5. Updates Terraform infrastructure

**When to use**: Automatic on merge to `develop`

### 3. `snail-doc-deploy-prod.yml`

**Trigger**:
- Push to `main` branch (with human approval)
- Manual workflow dispatch with confirmation

**What it does**:
1. Requires typing "CONFIRM" for manual deployments
2. Runs comprehensive tests
3. Builds production Lambda packages
4. Creates Blue-Green deployment
5. Deploys Lambda functions with new version
6. Runs extensive smoke tests
7. Monitors for errors (5 min)
8. Updates Terraform infrastructure
9. Notifies deployment status

**When to use**: Production releases only

### 4. `snail-doc-rollback.yml`

**Trigger**: Manual workflow dispatch only

**What it does**:
- Rolls back Lambda functions to previous (BLUE) version
- Optionally rolls back Terraform infrastructure
- Verifies rollback was successful

**When to use**: Emergency rollback scenarios

---

## 🚀 Deployment Process

### Development Deployment

1. **Create feature branch:**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/my-feature
   ```

4. **Wait for tests to pass** (automatic via `snail-doc-test.yml`)

5. **Merge to `develop`:**
   - Triggers automatic deployment to Dev
   - Monitor GitHub Actions for deployment status

6. **Verify in Dev:**
   ```bash
   curl -X POST "https://xxxxx.lambda-url.us-east-1.on.aws/" \
     -H "Content-Type: application/json" \
     -d '{"action":"query","query":"Test","user_id":"manual-test"}'
   ```

### Production Deployment

#### Option 1: Automatic (Push to main)

1. **Merge `develop` to `main`:**
   ```bash
   git checkout main
   git merge develop
   git push origin main
   ```

2. **Deployment starts automatically**

3. **Monitor deployment** in GitHub Actions

#### Option 2: Manual Workflow Dispatch

1. Go to GitHub Actions → `Snail Doc - Deploy to Production`

2. Click "Run workflow"

3. **Type "CONFIRM"** in the confirmation field

4. Select options:
   - Skip tests: ☑️ or ☐
   - Confirm production: `CONFIRM`

5. Click "Run workflow"

6. **Monitor deployment**:
   - Watch the workflow progress
   - Check smoke tests
   - Verify error monitoring

### Post-Deployment Verification

```bash
# Test greeting
curl -X POST "$LAMBDA_URL" \
  -H "Content-Type: application/json" \
  -d '{"action":"query","query":"Hello","user_id":"test"}'

# Test document list
curl -X POST "$LAMBDA_URL" \
  -H "Content-Type: application/json" \
  -d '{"action":"query","query":"List documents","user_id":"test"}'

# Test RAG query
curl -X POST "$LAMBDA_URL" \
  -H "Content-Type: application/json" \
  -d '{"action":"query","query":"What is in document X?","user_id":"test"}'
```

---

## ⏮️ Rollback Procedure

### When to Rollback

- High error rate detected
- Critical bug in production
- Performance degradation
- Failed smoke tests

### How to Rollback

1. **Go to GitHub Actions** → `Snail Doc - Rollback Production`

2. **Click "Run workflow"**

3. **Configure rollback:**
   - Environment: `dev` or `prod`
   - Rollback type:
     - `lambda-only` - Only Lambda functions
     - `infrastructure-only` - Only Terraform changes
     - `full` - Both Lambda and infrastructure
   - Confirmation: Type `ROLLBACK`

4. **Click "Run workflow"**

5. **Monitor rollback progress**

6. **Verify rollback:**
   ```bash
   curl -X POST "$LAMBDA_URL" \
     -H "Content-Type: application/json" \
     -d '{"action":"query","query":"Test after rollback","user_id":"rollback-verify"}'
   ```

### Manual Rollback (Emergency)

If GitHub Actions is down:

```bash
# Configure AWS CLI
export AWS_PROFILE=production

# Get BLUE version
BLUE_VERSION=$(aws lambda get-alias \
  --function-name snail-bedrock-prod-query-handler \
  --name BLUE \
  --query 'FunctionVersion' \
  --output text)

# Update GREEN to BLUE
aws lambda update-alias \
  --function-name snail-bedrock-prod-query-handler \
  --name GREEN \
  --function-version "$BLUE_VERSION"

# Verify
curl -X POST "$LAMBDA_URL" \
  -H "Content-Type: application/json" \
  -d '{"action":"query","query":"Test","user_id":"emergency"}'
```

---

## 🐛 Troubleshooting

### Deployment Fails: "Access Denied"

**Cause**: IAM role doesn't have permissions

**Fix**:
1. Verify IAM role ARN in GitHub secrets
2. Check trust policy allows the repository
3. Verify permissions policy includes required actions

```bash
# Check role
aws iam get-role --role-name GitHubActionsSnailDocDev

# Check attached policies
aws iam list-attached-role-policies --role-name GitHubActionsSnailDocDev
aws iam list-role-policies --role-name GitHubActionsSnailDocDev
```

### Tests Failing on CI but Pass Locally

**Cause**: Environment differences

**Fix**:
1. Check Python version (must be 3.11)
2. Verify all dependencies in `requirements.txt`
3. Ensure `shared/` directory is copied

```yaml
# Workflow should include:
- name: Copy shared directory
  run: |
    cp -r ../../shared .
```

### Smoke Tests Fail After Deployment

**Cause**: Lambda cold start or configuration issue

**Fix**:
1. Check Lambda logs:
   ```bash
   aws logs tail /aws/lambda/snail-bedrock-dev-query-handler --follow
   ```

2. Verify FAISS layer is attached:
   ```bash
   aws lambda get-function --function-name snail-bedrock-dev-query-handler
   ```

3. Test Lambda directly:
   ```bash
   aws lambda invoke \
     --function-name snail-bedrock-dev-query-handler \
     --payload '{"body":"{\"action\":\"query\",\"query\":\"test\",\"user_id\":\"ci\"}"}' \
     response.json
   cat response.json
   ```

### Terraform State Lock

**Cause**: Previous deployment didn't finish

**Fix**:
```bash
cd modules/snail-doc/infrastructure/terraform/environments/dev

# Check lock
terraform force-unlock LOCK_ID

# Or manually via DynamoDB if using remote state
aws dynamodb delete-item \
  --table-name terraform-state-lock \
  --key '{"LockID":{"S":"LOCK_ID"}}'
```

### Rollback Doesn't Work

**Cause**: BLUE alias not set

**Fix**:
```bash
# Create BLUE alias pointing to current working version
WORKING_VERSION=$(aws lambda get-alias \
  --function-name snail-bedrock-prod-query-handler \
  --name GREEN \
  --query 'FunctionVersion' \
  --output text)

aws lambda create-alias \
  --function-name snail-bedrock-prod-query-handler \
  --name BLUE \
  --function-version "$WORKING_VERSION" \
  --description "Working version before deployment"
```

---

## 📊 Monitoring Deployments

### CloudWatch Metrics to Watch

```bash
# Error rate
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=snail-bedrock-prod-query-handler \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Duration (performance)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=snail-bedrock-prod-query-handler \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum

# Invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=snail-bedrock-prod-query-handler \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### Setting up Alarms

```bash
# Create alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name snail-doc-prod-high-errors \
  --alarm-description "Alert on high error rate" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=FunctionName,Value=snail-bedrock-prod-query-handler
```

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] All tests passing in CI
- [ ] Code reviewed and approved
- [ ] Changes tested in Dev environment
- [ ] Documentation updated
- [ ] Breaking changes communicated
- [ ] Rollback plan identified
- [ ] Monitoring dashboard ready
- [ ] Team notified of deployment window

---

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS IAM OIDC](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_oidc.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Lambda Deployment Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-27
**Maintained by**: Snail Data Solutions
