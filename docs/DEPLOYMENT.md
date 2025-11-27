# Deployment Guide - Snail Doc AI Assistant

Guía completa para desplegar Snail Doc (asistente AI de documentos) en todos los ambientes.

**Última actualización**: 2025-11-26

---

## 📋 Prerequisites

### Required Tools
- **AWS CLI** configured with appropriate credentials
- **Terraform** >= 1.0
- **Node.js** >= 18 (for frontend)
- **Python** >= 3.9 (for Lambda development)

### AWS Account Requirements
- Bedrock access enabled in your AWS account
- Appropriate IAM permissions for creating resources

### Verify Prerequisites

```bash
# AWS CLI
aws --version
aws sts get-caller-identity

# Terraform
terraform --version

# Node.js
node --version
npm --version
```

---

## 🚀 Quick Start (Development Environment)

### Step 1: Clone and Navigate

```bash
cd /Users/daherakel/Projects/snail-data-solutions
cd modules/snail-doc/infrastructure/terraform/environments/dev
```

### Step 2: Initialize Terraform

```bash
terraform init
```

### Step 3: Review the Plan

```bash
terraform plan
```

### Step 4: Deploy Infrastructure

```bash
terraform apply
```

Review the changes and type `yes` to confirm.

### Step 5: Save Outputs

```bash
# Save important outputs
terraform output -json > outputs.json

# Or view individual outputs
terraform output raw_documents_bucket
terraform output query_handler_url
```

---

## 🏗️ Architecture Overview

### Current Implementation

The deployed system uses **FAISS** for vector storage, **not** OpenSearch or ChromaDB. This is a cost-optimized, Lambda-based implementation.

```
┌─────────────┐
│   User/App  │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│  Lambda: query-handler   │  ← Handles chat queries
│  - FAISS index (layer)   │  ← Vector search
│  - Bedrock Titan/Claude  │  ← LLM inference
│  - DynamoDB cache        │  ← Query caching
└──────────────────────────┘
       ▲
       │
┌──────┴───────┐
│              │
│  S3 → Lambda │  ← Automatic PDF processing
│  pdf-proc    │  ← Generates embeddings
│  DynamoDB    │  ← Conversation storage
└──────────────┘
```

### Key Components

1. **S3 Buckets**:
   - `raw-documents`: Original PDFs uploaded here
   - `processed-documents`: Processed document metadata
   - `faiss-backup`: FAISS index backups

2. **Lambda Functions**:
   - `pdf-processor`: Processes PDFs, generates embeddings, updates FAISS
   - `query-handler`: Handles chat queries using RAG with FAISS

3. **DynamoDB Tables**:
   - `query-cache`: Caches query results
   - `rate-limiting`: API rate limiting
   - `conversations`: Conversation history

4. **EventBridge**:
   - Triggers `pdf-processor` when files uploaded to S3

---

## ⚙️ Environment Configurations

### Development Environment

**Recommended for**: Testing, playground, POC

**Configuration** (`terraform.tfvars`):

```hcl
project_name = "snail-bedrock"
environment  = "dev"

# Use cheaper model for dev
bedrock_llm_model_id = "meta.llama3-3-70b-instruct-v1:0"  # Cost-effective
bedrock_embedding_model_id = "amazon.titan-embed-text-v1"

# Lambda settings
pdf_processor_timeout = 300   # 5 minutes
query_handler_timeout = 60    # 1 minute
lambda_log_level = "DEBUG"    # Verbose logging for dev
```

**Estimated Cost**: ~$0.78/month (see [COST_AND_SCALING.md](COST_AND_SCALING.md))

---

### Production Environment

**Recommended for**: Live customer-facing applications

**Configuration** (`terraform.tfvars`):

```hcl
project_name = "snail-bedrock"
environment  = "prod"

# Use more powerful model for production
bedrock_llm_model_id = "anthropic.claude-3-5-sonnet-20241022-v2:0"  # Better quality
bedrock_embedding_model_id = "amazon.titan-embed-text-v1"

# Lambda settings
pdf_processor_timeout = 300
query_handler_timeout = 30    # Shorter timeout for better UX
lambda_log_level = "INFO"     # Less verbose in prod

# Enable additional prod features
enable_monitoring = true
enable_alarms = true
```

**Estimated Cost**: $15-120/month depending on usage (see [COST_AND_SCALING.md](COST_AND_SCALING.md))

---

## 📦 Deployed Resources

After deployment, you'll have these resources:

### S3 Buckets
```
snail-bedrock-{env}-raw-documents          # Original PDFs
snail-bedrock-{env}-processed-documents    # Processing metadata
snail-bedrock-{env}-faiss-backup           # FAISS index backups
```

### Lambda Functions
```
snail-bedrock-{env}-pdf-processor   # PDF → FAISS embeddings
snail-bedrock-{env}-query-handler   # RAG query endpoint
```

### DynamoDB Tables
```
snail-bedrock-{env}-query-cache       # Query result cache
snail-bedrock-{env}-rate-limiting     # API rate limits
snail-bedrock-{env}-conversations     # Chat history
```

### EventBridge Rules
```
snail-bedrock-{env}-s3-object-created  # Auto-triggers PDF processing
```

---

## 🧪 Testing the Deployment

### 1. Upload a Test Document

```bash
# Get bucket name from Terraform output
export RAW_BUCKET=$(terraform output -raw raw_documents_bucket)

# Upload a test PDF
aws s3 cp test-document.pdf s3://$RAW_BUCKET/

# Check processing logs
aws logs tail /aws/lambda/snail-bedrock-dev-pdf-processor --follow
```

### 2. Verify Processing

```bash
# Check processed bucket
aws s3 ls s3://snail-bedrock-dev-processed-documents/

# Check FAISS backup
aws s3 ls s3://snail-bedrock-dev-faiss-backup/
```

### 3. Test Query Handler

```bash
# Get query handler URL
export QUERY_URL=$(terraform output -raw query_handler_url)

# Make a test query
curl -X POST $QUERY_URL \
  -H "Content-Type: application/json" \
  -d '{
    "action": "query",
    "query": "¿De qué trata el documento?",
    "user_id": "test-user"
  }' | jq
```

Expected response:
```json
{
  "answer": "El documento trata sobre...",
  "sources": ["test-document"],
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 56,
    "total_tokens": 1290
  }
}
```

---

## 🎨 Frontend Deployment

### 1. Navigate to Frontend

```bash
cd /Users/daherakel/Projects/snail-data-solutions/modules/snail-doc/frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

Create `.env.local`:

```bash
# Get query handler URL from Terraform
export QUERY_URL=$(cd ../infrastructure/terraform/environments/dev && terraform output -raw query_handler_url)

# Create .env.local
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=$QUERY_URL
NEXT_PUBLIC_ENVIRONMENT=development
EOF
```

### 4. Run Development Server

```bash
npm run dev
```

Visit http://localhost:3000

### 5. Build for Production

```bash
npm run build
npm run start
```

---

## 🔄 Updates and Redeployment

### Update Lambda Functions

When you modify Lambda code:

```bash
# Rebuild Lambda deployment packages
cd modules/snail-doc/lambda-functions/query-handler
zip -r ../query-handler.zip handler.py

# Redeploy via Terraform
cd ../../infrastructure/terraform/environments/dev
terraform apply
```

### Update Infrastructure

When you change Terraform configuration:

```bash
cd modules/snail-doc/infrastructure/terraform/environments/dev

# Review changes
terraform plan

# Apply changes
terraform apply
```

---

## 🐛 Troubleshooting

### Issue: PDF Not Processing Automatically

**Check**:
1. EventBridge rule is enabled:
   ```bash
   aws events describe-rule --name snail-bedrock-dev-s3-object-created
   ```

2. Lambda has S3 permissions:
   ```bash
   aws lambda get-policy --function-name snail-bedrock-dev-pdf-processor
   ```

3. Check Lambda logs:
   ```bash
   aws logs tail /aws/lambda/snail-bedrock-dev-pdf-processor --follow
   ```

---

### Issue: Query Handler Returns 500 Error

**Check**:
1. FAISS index exists in S3:
   ```bash
   aws s3 ls s3://snail-bedrock-dev-faiss-backup/
   ```

2. Lambda can access Bedrock:
   ```bash
   aws bedrock list-foundation-models --region us-east-1
   ```

3. Check Lambda logs:
   ```bash
   aws logs tail /aws/lambda/snail-bedrock-dev-query-handler --follow
   ```

---

### Issue: High Costs

**Check**:
1. Review cost breakdown:
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2025-11-01,End=2025-11-30 \
     --granularity MONTHLY \
     --metrics BlendedCost \
     --group-by Type=SERVICE
   ```

2. Verify you're using cost-optimized models (Llama 3.3 or Titan Express)

3. See [COST_AND_SCALING.md](COST_AND_SCALING.md) for optimization strategies

---

## 🧹 Cleanup

### Partial Cleanup (Keep Some Resources)

```bash
# Delete only Lambda functions
terraform destroy -target=module.lambda

# Delete only S3 buckets (must be empty first)
aws s3 rm s3://snail-bedrock-dev-raw-documents --recursive
terraform destroy -target=module.s3
```

### Complete Cleanup

```bash
# Empty all S3 buckets first
export ENV="dev"
aws s3 rm s3://snail-bedrock-${ENV}-raw-documents --recursive
aws s3 rm s3://snail-bedrock-${ENV}-processed-documents --recursive
aws s3 rm s3://snail-bedrock-${ENV}-faiss-backup --recursive

# Destroy all infrastructure
cd modules/snail-doc/infrastructure/terraform/environments/${ENV}
terraform destroy
```

Type `yes` to confirm.

---

## 📊 Monitoring

### CloudWatch Dashboards

After deployment, view metrics at:
- Lambda invocations: AWS Console → CloudWatch → Lambda metrics
- Bedrock usage: AWS Console → CloudWatch → Bedrock metrics
- Cost tracking: AWS Console → Cost Explorer

### Set Up Alerts

```bash
# Create budget alert (optional)
aws budgets create-budget \
  --account-id $(aws sts get-caller-identity --query Account --output text) \
  --budget file://budget.json
```

Example `budget.json`:
```json
{
  "BudgetName": "BedrockMonthlyBudget",
  "BudgetLimit": {
    "Amount": "50",
    "Unit": "USD"
  },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST"
}
```

---

## 🔐 Security Best Practices

1. **Rotate IAM Credentials Regularly**
2. **Enable CloudTrail Logging**
3. **Use AWS Secrets Manager** for sensitive data
4. **Enable S3 Versioning** for important buckets
5. **Review IAM Policies** regularly

---

## 📚 Next Steps

After successful deployment:

1. **Test with Real Documents**: Upload your actual PDFs
2. **Customize Prompts**: Modify Lambda code to adjust LLM behavior
3. **Tune Performance**: Adjust chunk sizes, top_k values
4. **Monitor Costs**: Set up billing alerts
5. **Scale Up**: Review [COST_AND_SCALING.md](COST_AND_SCALING.md) for production optimization

---

## 📖 Related Documentation

- [Cost & Scaling Guide](COST_AND_SCALING.md) - Detailed cost analysis
- [Module README](../modules/snail-doc/README.md) - Architecture and features
- [Archived Docs](archive/) - Historical alternatives (ChromaDB, OpenSearch)

---

## 🆘 Support

For issues or questions:
- Check [CLAUDE.md](../CLAUDE.md) for development guidelines
- Review [Terraform docs](https://www.terraform.io/docs)
- Check AWS documentation for specific services

---

**Last Updated**: 2025-11-26
**Module Version**: 1.0.0 (FAISS-based implementation)
