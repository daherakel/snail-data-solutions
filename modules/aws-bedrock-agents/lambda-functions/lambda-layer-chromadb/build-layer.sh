#!/bin/bash
# Script para crear Lambda Layer de ChromaDB

set -e

echo "🔨 Creando Lambda Layer de ChromaDB..."

# Limpiar directorio anterior
rm -rf python/ chromadb-layer.zip

# Crear directorio python/ (requerido por Lambda)
mkdir -p python

# Instalar dependencias usando Docker (para compatibilidad con Lambda runtime)
docker run --rm \
  -v "$(pwd)":/var/task \
  public.ecr.aws/lambda/python:3.11 \
  pip install -r requirements.txt -t python/

# Comprimir
echo "📦 Comprimiendo layer..."
zip -r chromadb-layer.zip python/

# Limpiar
rm -rf python/

echo "✅ Layer creado: chromadb-layer.zip"
echo "📊 Tamaño: $(du -h chromadb-layer.zip | cut -f1)"
echo ""
echo "Para subir a AWS Lambda:"
echo "  aws lambda publish-layer-version \\"
echo "    --layer-name snail-bedrock-chromadb \\"
echo "    --zip-file fileb://chromadb-layer.zip \\"
echo "    --compatible-runtimes python3.11 python3.12"
