# Lambda Functions - Development Guide

This directory contains AWS Lambda functions for the Snail Doc module.

## 📁 Structure

```
lambda-functions/
├── query-handler/           # RAG query processing with NLP
│   ├── handler.py          # Main Lambda handler (refactored v2.0.0)
│   ├── requirements.txt    # Python dependencies
│   ├── shared/             # Copied during deployment
│   ├── test_local.py       # Local testing script
│   ├── local_server.py     # HTTP server for frontend testing
│   └── .gitignore          # Excludes dependencies
│
├── pdf-processor/          # PDF processing and embeddings
│   ├── handler.py          # Main Lambda handler
│   ├── requirements.txt    # Python dependencies
│   ├── shared/             # Copied during deployment
│   └── .gitignore          # Excludes dependencies
│
└── slack-handler/          # Slack integration (optional)
```

## ⚠️ IMPORTANT: Dependencies Management

### What Should NOT Be in Git

The following are **EXCLUDED from Git** via `.gitignore`:

```
# Python dependencies (installed locally via pip)
boto3/
botocore/
urllib3/
yaml/
dateutil/
jmespath/
s3transfer/
PyPDF2/
*.dist-info/

# Python cache
__pycache__/
*.pyc

# Deployment packages
*.zip
```

### Why?

These dependencies:
- ✅ **Are installed during CI/CD** automatically
- ✅ **Are packaged by Terraform** for deployment
- ❌ **Should NOT be committed to Git** (bloats repository)
- ❌ **Are environment-specific** (different OS/Python versions)

### Clean Repository Size

**Before cleanup:**
```
query-handler/: ~27 MB (with dependencies)
```

**After cleanup:**
```
query-handler/: ~250 KB (without dependencies)
```

**100x smaller repository!**

---

## 🚀 Development Workflow

### Local Development

1. **Install dependencies locally** (for testing):
   ```bash
   cd lambda-functions/query-handler
   pip install -r requirements.txt -t .
   ```

2. **Copy shared directory**:
   ```bash
   cp -r ../../shared .
   ```

3. **Run local tests**:
   ```bash
   python test_local.py --suite
   ```

4. **Test with frontend**:
   ```bash
   python local_server.py
   ```

5. **Clean up before committing**:
   ```bash
   # Dependencies are auto-ignored by .gitignore
   git status  # Should NOT show boto3, botocore, etc.
   ```

### CI/CD Deployment

Dependencies are installed automatically during GitHub Actions:

```yaml
# .github/workflows/snail-doc-deploy-dev.yml
steps:
  - name: Copy shared directory
    run: cp -r ../../shared .

  - name: Install dependencies
    run: pip install -r requirements.txt -t .

  - name: Create deployment package
    run: zip -r function.zip .
```

### Manual Deployment

If deploying manually (not recommended):

```bash
# 1. Copy shared
cp -r ../../shared .

# 2. Install dependencies
pip install -r requirements.txt -t .

# 3. Create package
zip -r query-handler.zip . -x "*.git*" "tests/*"

# 4. Deploy
aws lambda update-function-code \
  --function-name snail-bedrock-dev-query-handler \
  --zip-file fileb://query-handler.zip

# 5. Clean up (optional)
rm -rf boto3 botocore urllib3 yaml dateutil jmespath s3transfer *.dist-info
```

---

## 📂 Shared Directory

The `shared/` directory contains code shared across Lambda functions:

```
shared/
├── nlp/                    # NLP components (v2.0.0)
│   ├── intent_classifier.py
│   ├── response_generator.py
│   └── guardrails.py
├── prompts/               # Modular prompts
│   └── base_prompts.py
├── config/                # Configuration
│   └── nlp-config.yaml
└── utils/                 # Utilities
    └── nlp_config_loader.py
```

**Important:**
- `shared/` is kept in Git at module root: `modules/snail-doc/shared/`
- During deployment, it's **copied** into each Lambda directory
- The copied version in Lambda directories can be gitignored (optional)

---

## 🧪 Testing

### Unit Tests

```bash
cd query-handler
python test_local.py --suite
```

**Tests include:**
- ✅ Greeting detection
- ✅ Document list
- ✅ RAG queries
- ✅ Multi-language
- ✅ Typo tolerance

### Integration Tests

```bash
# Start local server
python local_server.py

# In another terminal, start frontend
cd ../../frontend
npm run dev

# Test in browser: http://localhost:3000
```

### Smoke Tests (Post-Deployment)

```bash
# Test deployed Lambda
curl -X POST "https://xxxxx.lambda-url.us-east-1.on.aws/" \
  -H "Content-Type: application/json" \
  -d '{"action":"query","query":"Hello","user_id":"test"}'
```

---

## 📦 Dependencies

### query-handler/requirements.txt

```
boto3==1.34.0
PyYAML==6.0.1
```

**Why so minimal?**
- `faiss`, `numpy`: Provided by Lambda Layer (40 MB)
- `boto3`: Available in Lambda runtime (but we pin version)
- `PyYAML`: For configuration loading

### pdf-processor/requirements.txt

```
boto3==1.34.0
PyPDF2==3.0.1
```

---

## 🔧 Troubleshooting

### "No module named 'shared'"

**Cause**: `shared/` directory not copied

**Fix**:
```bash
cp -r ../../shared .
```

### "No module named 'yaml'"

**Cause**: Dependencies not installed

**Fix**:
```bash
pip install -r requirements.txt -t .
```

### "No module named 'faiss'"

**Cause**: FAISS layer not attached to Lambda

**Fix**:
```bash
aws lambda update-function-configuration \
  --function-name snail-bedrock-dev-query-handler \
  --layers arn:aws:lambda:us-east-1:ACCOUNT:layer:snail-bedrock-dev-faiss-layer:1
```

### Repository Too Large

**Cause**: Dependencies committed to Git

**Fix**:
```bash
# Remove from working directory
rm -rf boto3 botocore urllib3 yaml dateutil jmespath s3transfer *.dist-info

# Remove from Git history (if already committed)
git rm -r --cached boto3 botocore urllib3 yaml dateutil jmespath s3transfer
git commit -m "chore: remove Python dependencies from Git"
```

---

## 🎯 Best Practices

### DO ✅

- ✅ Use `.gitignore` to exclude dependencies
- ✅ Install dependencies during CI/CD
- ✅ Pin dependency versions in `requirements.txt`
- ✅ Test locally before deploying
- ✅ Use Lambda layers for large dependencies (FAISS)
- ✅ Keep `shared/` at module root
- ✅ Copy `shared/` during deployment only

### DON'T ❌

- ❌ Commit dependencies to Git
- ❌ Use `pip install` without `-t .` for Lambda
- ❌ Deploy without testing
- ❌ Hardcode values (use environment variables)
- ❌ Include test files in deployment package
- ❌ Forget to attach Lambda layers

---

## 📊 Deployment Package Sizes

| Component | Size | Included |
|-----------|------|----------|
| handler.py | 25 KB | ✅ Always |
| requirements (boto3, PyYAML) | ~14 MB | ✅ In package |
| shared/ | 250 KB | ✅ Copied during deploy |
| FAISS layer | 40 MB | ✅ Attached separately |
| **Total package** | **~14.3 MB** | Zipped |
| **Total with layer** | **~54.3 MB** | Deployed |

Lambda limit: 250 MB unzipped, 50 MB zipped (without layers)

---

## 🚀 Quick Reference

```bash
# Local development
pip install -r requirements.txt -t .
cp -r ../../shared .
python test_local.py --suite
python local_server.py

# Deploy via CI/CD
git push origin develop  # Auto-deploys to Dev

# Manual deploy (emergency)
zip -r function.zip . -x "*.git*"
aws lambda update-function-code --function-name NAME --zip-file fileb://function.zip

# Clean up
rm -rf boto3 botocore urllib3 yaml dateutil jmespath s3transfer *.dist-info __pycache__
```

---

**Version**: 1.0.0
**Last Updated**: 2025-11-27
**Maintained by**: Snail Data Solutions
