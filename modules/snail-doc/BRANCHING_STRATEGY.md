# Branching Strategy - Snail Doc

## Git Flow

Este proyecto usa Git Flow simplificado para gestionar deployments:

```
feature/* → develop → main
            ↓          ↓
          Dev Env   Prod Env
          (auto)    (manual)
```

## Branches

### `develop`
- **Propósito**: Development environment
- **Deploy**: Automático en cada push
- **Ambiente**: Dev (AWS)
- **Testing**: Automático via GitHub Actions

### `main`
- **Propósito**: Production environment
- **Deploy**: Manual via workflow_dispatch
- **Ambiente**: Prod (AWS)
- **Protección**: Requiere confirmación "CONFIRM"

### `feature/*`
- **Propósito**: Desarrollo de nuevas features
- **Base**: develop
- **Merge**: Via PR a develop
- **Testing**: Automático en cada PR

## Workflow

### Development
```bash
# 1. Crear feature branch desde develop
git checkout develop
git pull
git checkout -b feature/mi-feature

# 2. Desarrollar y commit
git add .
git commit -m "feat: mi feature"

# 3. Push y crear PR
git push -u origin feature/mi-feature
gh pr create --base develop
```

### Deployment a Dev
```bash
# Automático al mergear PR a develop
gh pr merge PR_NUMBER --merge
# → Trigger automático de deploy-dev workflow
```

### Deployment a Prod
```bash
# 1. Mergear develop a main
git checkout main
git merge develop
git push

# 2. Deploy manual desde GitHub Actions
# Ir a: Actions → "Snail Doc - Deploy to Production"
# → Run workflow
# → Type "CONFIRM"
```

## CI/CD Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `snail-doc-test.yml` | PR, push to develop/main | Tests automáticos |
| `snail-doc-deploy-dev.yml` | Push to develop | Deploy a Dev |
| `snail-doc-deploy-prod.yml` | Manual (workflow_dispatch) | Deploy a Prod |
| `snail-doc-rollback.yml` | Manual (workflow_dispatch) | Rollback de emergencia |

## Protecciones

### Branch `main`
- ✅ Requiere PR review (recomendado)
- ✅ Requiere tests pasando
- ✅ Deploy manual solamente

### Branch `develop`
- ✅ Requiere tests pasando
- ✅ Deploy automático
- ✅ Environment: Dev

---

**Última actualización**: 2025-11-27

## Status

✅ CI/CD Pipeline completamente configurado y funcionando
✅ Deploy automático a Dev en push a develop
✅ Deploy automático a Prod en push a main
