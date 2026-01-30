import { NextResponse } from 'next/server';
import { S3Client, ListObjectsV2Command } from '@aws-sdk/client-s3';

const getS3Client = () => {
  const region = process.env.AWS_REGION || 'us-east-1';
  const accessKeyId = process.env.AWS_ACCESS_KEY_ID?.trim();
  const secretAccessKey = process.env.AWS_SECRET_ACCESS_KEY?.trim();

  // Si hay credenciales explícitas en variables de entorno, usarlas
  if (accessKeyId && secretAccessKey) {
    console.log('Using credentials from environment variables');
    return new S3Client({
      region,
      credentials: {
        accessKeyId,
        secretAccessKey,
      },
    });
  }

  // Si no, dejar que AWS SDK use el default credential provider automáticamente
  // Esto usará: 1) Variables de entorno AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY
  //             2) ~/.aws/credentials (perfil default)
  //             3) IAM role (si está en EC2/Lambda)
  console.log('Using AWS default credential provider chain');
  return new S3Client({
    region,
  });
};

const BUCKET_NAME = process.env.RAW_DOCUMENTS_BUCKET || 'snail-bedrock-dev-raw-documents';

export async function GET() {
  try {
    // Debug: Ver qué credenciales están disponibles
    const hasAccessKey = !!process.env.AWS_ACCESS_KEY_ID?.trim();
    const hasSecretKey = !!process.env.AWS_SECRET_ACCESS_KEY?.trim();
    console.log(`[Documents API] Credentials check - AccessKey: ${hasAccessKey}, SecretKey: ${hasSecretKey}`);
    console.log(`[Documents API] Region: ${process.env.AWS_REGION || 'us-east-1'}`);
    console.log(`[Documents API] Bucket: ${BUCKET_NAME}`);
    
    const s3Client = getS3Client();
    
    console.log(`[Documents API] Fetching documents from bucket: ${BUCKET_NAME}`);
    
    const command = new ListObjectsV2Command({
      Bucket: BUCKET_NAME,
    });

    const response = await s3Client.send(command);
    console.log(`[Documents API] Found ${response.Contents?.length || 0} objects in bucket`);

    const documents = (response.Contents || [])
      .filter((item) => item.Key && item.Key.endsWith('.pdf'))
      .map((item) => ({
        name: item.Key!.split('/').pop() || item.Key!,
        key: item.Key!,
        size: item.Size || 0,
        lastModified: item.LastModified?.toISOString() || '',
      }));

    console.log(`Returning ${documents.length} PDF documents`);
    return NextResponse.json({ documents });
  } catch (error: any) {
    console.error('Error fetching documents:', error);
    
    // Proporcionar información más detallada del error
    const errorMessage = error.message || 'Unknown error';
    const errorCode = error.Code || error.$metadata?.httpStatusCode || 500;
    
    // Determinar si es un error de credenciales
    if (errorMessage.includes('credentials') || errorMessage.includes('Access Denied') || errorMessage.includes('InvalidAccessKeyId') || errorMessage.includes('SignatureDoesNotMatch') || errorCode === 401 || errorCode === 403) {
      console.error('[Documents API] Credential error detected:', {
        message: errorMessage,
        code: errorCode,
        hasEnvAccessKey: !!process.env.AWS_ACCESS_KEY_ID,
        hasEnvSecretKey: !!process.env.AWS_SECRET_ACCESS_KEY
      });
      
      return NextResponse.json(
        { 
          error: 'Error de credenciales AWS',
          details: 'Verifica que AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY estén configuradas en .env.local. Si el servidor estaba corriendo antes de configurar .env.local, reinícialo.',
          code: errorCode,
          debug: {
            hasAccessKey: !!process.env.AWS_ACCESS_KEY_ID,
            hasSecretKey: !!process.env.AWS_SECRET_ACCESS_KEY,
            region: process.env.AWS_REGION || 'us-east-1'
          }
        },
        { status: 401 }
      );
    }
    
    // Determinar si es un error de bucket
    if (errorMessage.includes('bucket') || errorMessage.includes('NoSuchBucket')) {
      return NextResponse.json(
        { 
          error: 'Bucket no encontrado',
          details: `El bucket "${BUCKET_NAME}" no existe o no tienes acceso`,
          code: errorCode
        },
        { status: 404 }
      );
    }
    
    return NextResponse.json(
      { 
        error: 'Error al obtener documentos',
        details: errorMessage,
        code: errorCode
      },
      { status: 500 }
    );
  }
}
