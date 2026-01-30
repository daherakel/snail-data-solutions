# Testing Local del Query Handler Refactorizado

Guía completa para testear el nuevo query handler localmente antes de deployar a AWS.

## 🎯 Opciones de Testing

### Opción 1: Test Unitario (Rápido)
Testea el handler sin servidor HTTP.

### Opción 2: Test con Frontend (Completo)
Corre un servidor local y conecta el frontend.

---

## ⚙️ Prerequisitos

1. **Python 3.11** instalado
2. **Dependencias instaladas**:
   ```bash
   cd /Users/daherakel/Projects/snail-data-solutions/modules/snail-doc/lambda-functions/query-handler
   pip install -r requirements.txt
   pip install PyYAML  # Si no está en requirements.txt
   ```

3. **AWS Credentials configuradas** (para acceder a S3, Bedrock, DynamoDB)
   ```bash
   aws configure
   ```

4. **Variables de entorno** (ya configuradas en los scripts de testing)

---

## 🧪 Opción 1: Test Unitario

### 1.1 Test Simple
```bash
cd /Users/daherakel/Projects/snail-data-solutions/modules/snail-doc/lambda-functions/query-handler

# Test de un query específico
python test_local.py --query "hola"
```

**Salida esperada:**
```
================================================================================
TESTING QUERY: hola
================================================================================

Status Code: 200

Response:
{
  "conversation_id": "conv_abc123",
  "query": "hola",
  "answer": "¡Hola! 👋 ¿En qué puedo ayudarte hoy?",
  "sources": [],
  "intent": "greeting",
  "usage": {...}
}

================================================================================
ANSWER: ¡Hola! 👋 ¿En qué puedo ayudarte hoy?
INTENT: greeting
SOURCES:
FROM CACHE: False
================================================================================
```

### 1.2 Test Suite Completo
```bash
# Ejecuta todos los tests
python test_local.py --suite
```

**Tests incluidos:**
1. ✅ Saludo simple - `"hola"`
2. ✅ Saludo con typo - `"holaa como estas"`
3. ✅ Agradecimiento - `"gracias"`
4. ✅ Agradecimiento con typo - `"garcias perfecto"`
5. ✅ Lista de documentos - `"que documentos tenes"`
6. ✅ Query sobre documentos - `"¿Qué dice el documento sobre AWS Bedrock?"`
7. ✅ Multi-idioma - `"thank you"`

**Salida esperada:**
```
================================================================================
TEST SUMMARY
================================================================================
Total tests: 7
✅ Passed: 7
❌ Failed: 0
Success rate: 100.0%
================================================================================
```

### 1.3 Test con Conversación
```bash
# Primera query
python test_local.py --query "hola" --conversation-id conv_123

# Segunda query en la misma conversación
python test_local.py --query "que documentos hay" --conversation-id conv_123
```

---

## 🌐 Opción 2: Test con Frontend

### 2.1 Iniciar Servidor Local

```bash
cd /Users/daherakel/Projects/snail-data-solutions/modules/snail-doc/lambda-functions/query-handler

# Iniciar servidor en puerto 8000 (default)
python local_server.py

# O en otro puerto
python local_server.py --port 3001
```

**Salida:**
```
================================================================================
🚀 LOCAL LAMBDA SERVER RUNNING
================================================================================
Listening on: http://localhost:8000

Para conectar el frontend, actualiza .env.local:
  LAMBDA_QUERY_URL=http://localhost:8000

Presiona Ctrl+C para detener
================================================================================
```

### 2.2 Configurar Frontend

En otra terminal:

```bash
cd /Users/daherakel/Projects/snail-data-solutions/modules/snail-doc/frontend

# Editar .env.local
nano .env.local
```

**Cambiar:**
```bash
# ANTES
LAMBDA_QUERY_URL=https://whqi5eevnmoygdjyaep5fdsmma0wqgne.lambda-url.us-east-1.on.aws/

# DESPUÉS
LAMBDA_QUERY_URL=http://localhost:8000
```

### 2.3 Iniciar Frontend

```bash
cd /Users/daherakel/Projects/snail-data-solutions/modules/snail-doc/frontend

# Si no está instalado
npm install

# Iniciar
npm run dev
```

### 2.4 Probar en el Navegador

1. Abrir: `http://localhost:3000`
2. Ir al tab "Chat"
3. Probar queries:
   - `"hola"` → Debe responder con saludo
   - `"gracias"` → Debe responder con agradecimiento
   - `"que documentos tenes"` → Debe listar documentos
   - `"¿qué dice el documento sobre...?"` → Debe buscar en FAISS y responder

**Ventajas:**
- ✅ Ver la UI real
- ✅ Testear flujo completo
- ✅ Debug en tiempo real (los logs aparecen en la terminal del servidor)

---

## 🔍 Verificar Nuevo Sistema NLP

### Test 1: Clasificación de Intenciones

**Objetivo**: Verificar que usa LLM en lugar de regex.

```bash
# Test con typo (antes fallaba, ahora debe funcionar)
python test_local.py --query "garcias"
```

**Esperado**: Debe detectar intent `thanks` aunque tenga typo.

### Test 2: Multi-idioma

```bash
# Inglés
python test_local.py --query "thank you"

# Francés (bonus)
python test_local.py --query "merci"
```

**Esperado**: Ambos deben detectar intent `thanks`.

### Test 3: Variaciones Naturales

```bash
# Variaciones de saludo
python test_local.py --query "hey que tal como andas"
python test_local.py --query "buenas tardes"
python test_local.py --query "ola k ase"
```

**Esperado**: Todos deben detectar intent `greeting`.

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError

```bash
# Si falla al importar shared/
cd /Users/daherakel/Projects/snail-data-solutions/modules/snail-doc/lambda-functions/query-handler

# Verificar que existe shared/
ls ../../shared/nlp/

# Si no existe, verificar la estructura
```

### Error: boto3.exceptions

```bash
# Verificar AWS credentials
aws sts get-caller-identity

# Si falla, configurar
aws configure
```

### Error: No module named 'yaml'

```bash
# Instalar PyYAML
pip install PyYAML
```

### Server no responde

```bash
# Verificar que el servidor esté corriendo
curl http://localhost:8000 -X POST -H "Content-Type: application/json" -d '{"query":"hola"}'

# Verificar logs en la terminal del servidor
```

### Frontend no conecta

```bash
# Verificar .env.local
cat frontend/.env.local | grep LAMBDA_QUERY_URL

# Debe mostrar: LAMBDA_QUERY_URL=http://localhost:8000
```

---

## 📊 Comparar con Sistema Viejo

### Test Side-by-Side

1. **Hacer backup del handler nuevo:**
   ```bash
   cp handler.py handler_new.py
   ```

2. **Restaurar handler viejo:**
   ```bash
   cp handler_old_backup.py handler.py
   ```

3. **Testear sistema viejo:**
   ```bash
   python test_local.py --query "garcias"  # ❌ Debe fallar
   ```

4. **Restaurar handler nuevo:**
   ```bash
   cp handler_new.py handler.py
   ```

5. **Testear sistema nuevo:**
   ```bash
   python test_local.py --query "garcias"  # ✅ Debe funcionar
   ```

---

## ✅ Checklist de Testing

Antes de deployar a AWS, verificar:

- [ ] `python test_local.py --suite` pasa 100%
- [ ] Saludos con typos funcionan
- [ ] Agradecimientos con typos funcionan
- [ ] Multi-idioma funciona (inglés mínimo)
- [ ] Lista de documentos funciona
- [ ] Queries sobre documentos funcionan
- [ ] Cache funciona (segunda query más rápida)
- [ ] Frontend local conecta correctamente
- [ ] Conversaciones se guardan en DynamoDB
- [ ] No hay errores en logs

---

## 🚀 Próximo Paso: Deploy a AWS

Una vez que todos los tests pasen:

```bash
cd ../../infrastructure/terraform/environments/dev

# Deploy
terraform apply
```

---

## 📝 Notas

- **Costo de testing local**: $0 (solo usa AWS cuando conecta a S3/Bedrock/DynamoDB)
- **Velocidad**: Local server ~100ms, AWS Lambda ~300ms
- **Logs**: Más fáciles de leer localmente que en CloudWatch
- **Iteración**: Cambios instantáneos sin necesidad de redeploy

---

**Fecha**: 2025-11-27
**Versión**: 2.0.0 (Sistema NLP con LLM)
