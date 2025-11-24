# AWS Bedrock AI Agents - Snail Data Solutions

Módulo modular y replicable para crear agentes de AI usando AWS Bedrock que pueden procesar y responder consultas sobre diversos tipos de archivos.

## Descripción

Este módulo implementa una solución completa de agentes de AI que:
- ✅ Procesa múltiples tipos de archivos (PDFs, documentos, CSVs, código, imágenes)
- ✅ Utiliza AWS Bedrock para modelos de lenguaje (Claude, Titan, etc.)
- ✅ Implementa RAG (Retrieval Augmented Generation) con Knowledge Bases
- ✅ Orquesta workflows complejos con Step Functions
- ✅ Es completamente replicable usando Terraform (IaC)
- ✅ Soporta múltiples ambientes (dev/staging/prod)

## Casos de Uso

- **Análisis de documentos**: Responder preguntas sobre contratos, reportes, documentación técnica
- **Code assistant**: Ayuda con bases de código, documentación de APIs
- **Data analysis**: Consultas sobre datasets, generación de insights
- **Document processing**: Extracción y análisis de información de múltiples fuentes

## Arquitectura

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                    Document Ingestion Pipeline                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────┐    ┌──────────────┐    ┌────────────────┐
│ S3 Raw   │───▶│ EventBridge  │───▶│ Step Function  │
│ Bucket   │    │   Trigger    │    │  Orchestrator  │
└──────────┘    └──────────────┘    └────────────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
            ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
            │ Lambda PDF   │       │ Lambda CSV   │       │ Lambda Image │
            │  Processor   │       │  Processor   │       │  (Textract)  │
            └──────────────┘       └──────────────┘       └──────────────┘
                    │                       │                       │
                    └───────────────────────┼───────────────────────┘
                                            ▼
                                    ┌──────────────┐
                                    │ S3 Processed │
                                    │   Bucket     │
                                    └──────────────┘
                                            │
                                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AI Agent Layer                             │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌──────────────────┐            ┌──────────────────┐
    │ Bedrock Agent    │◀───────────│ Knowledge Base   │
    │ (Claude/Titan)   │            │  (Vector Store)  │
    └──────────────────┘            └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │ Lambda Actions   │
    │  (Custom Logic)  │
    └──────────────────┘
```

### Servicios AWS Utilizados

- **Amazon Bedrock**: Modelos de lenguaje (Claude, Titan)
- **Knowledge Bases for Amazon Bedrock**: RAG con embeddings
- **AWS Lambda**: Procesamiento serverless de documentos
- **AWS Step Functions**: Orquestación de workflows
- **Amazon S3**: Almacenamiento de documentos (raw y processed)
- **Amazon Textract**: OCR para imágenes y documentos escaneados
- **Amazon EventBridge**: Triggers y eventos
- **AWS IAM**: Roles y políticas de seguridad

## Estructura del Módulo

```
snail-data-solutions/
├── infrastructure/
│   └── terraform/
│       ├── modules/                    # Módulos reutilizables
│       │   ├── bedrock-agent/         # Configuración del agente Bedrock
│       │   ├── bedrock-knowledge-base/ # Knowledge Base con vector store
│       │   ├── lambda/                # Lambda functions
│       │   ├── step-functions/        # Definición de workflows
│       │   ├── s3-storage/           # Buckets S3 por ambiente
│       │   └── iam/                  # Roles y políticas
│       ├── environments/              # Configuración por ambiente
│       │   ├── dev/
│       │   │   ├── main.tf
│       │   │   ├── variables.tf
│       │   │   └── terraform.tfvars
│       │   ├── staging/
│       │   └── prod/
│       ├── backend.tf                 # Backend de Terraform (S3)
│       └── versions.tf                # Versiones de providers
├── lambda-functions/                  # Código de las Lambdas
│   ├── pdf-processor/
│   │   ├── handler.py
│   │   ├── requirements.txt
│   │   └── tests/
│   ├── csv-processor/
│   ├── image-processor/
│   ├── code-processor/
│   └── query-handler/                 # Lambda para queries al agente
├── step-functions/                    # Definiciones de workflows
│   ├── document-ingestion.asl.json
│   └── batch-processing.asl.json
└── docs/
    └── aws-bedrock-agents/
        ├── README.md                  # Este archivo
        ├── ARCHITECTURE.md            # Arquitectura detallada
        └── DEPLOYMENT.md              # Guía de deployment
```

## Principios de Diseño

### 1. Modularidad
- Cada componente es independiente y reutilizable
- Módulos de Terraform separados por funcionalidad
- Lambdas especializadas por tipo de archivo

### 2. Escalabilidad
- Serverless (Lambda, Bedrock) para escalar automáticamente
- S3 para almacenamiento ilimitado
- Step Functions para workflows paralelos

### 3. Seguridad
- Principio de privilegios mínimos en IAM
- Encriptación en reposo (S3, Knowledge Base)
- Encriptación en tránsito (TLS)
- Secrets en AWS Secrets Manager

### 4. Replicabilidad
- Todo definido como código (Terraform)
- Variables por ambiente (dev/staging/prod)
- Fácil de replicar para diferentes clientes

### 5. Costo-Eficiencia
- Serverless: paga solo por uso
- S3 Intelligent Tiering para archivos
- Lifecycle policies para limpiar datos antiguos

## Ambientes

### Dev
- Para desarrollo y pruebas
- Modelos más pequeños de Bedrock (cost-effective)
- Retención corta de datos

### Staging
- Replica producción
- Para testing pre-release
- Mismos modelos que prod

### Prod
- Ambiente de producción
- Modelos optimizados para performance
- Retención según compliance

## Workflow de Ingesta de Documentos

1. **Upload**: Usuario sube archivo a S3 bucket raw
2. **Trigger**: EventBridge detecta nuevo objeto en S3
3. **Orchestration**: Step Function inicia workflow
4. **Processing**:
   - Identifica tipo de archivo
   - Ejecuta Lambda apropiada (PDF/CSV/Image/Code)
   - Extrae texto y metadata
5. **Storage**: Guarda resultado en S3 processed
6. **Indexing**: Knowledge Base indexa el contenido
7. **Ready**: Documento disponible para queries

## Workflow de Query

1. **Request**: Usuario hace pregunta al agente
2. **Retrieval**: Knowledge Base busca contexto relevante
3. **Augmentation**: Agente recibe pregunta + contexto
4. **Generation**: Bedrock genera respuesta
5. **Actions**: (Opcional) Ejecuta Lambda custom si necesita
6. **Response**: Retorna respuesta al usuario

## Próximos Pasos

1. ✅ Estructura base creada
2. ⏳ Implementar módulos de Terraform
3. ⏳ Desarrollar Lambda functions
4. ⏳ Definir Step Functions workflows
5. ⏳ Configurar Bedrock Agent y Knowledge Base
6. ⏳ Testing en ambiente dev
7. ⏳ Documentar guía de deployment

## Referencias

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Knowledge Bases for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [AWS Step Functions](https://docs.aws.amazon.com/step-functions/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
