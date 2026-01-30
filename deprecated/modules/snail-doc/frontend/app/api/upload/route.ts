import { NextRequest, NextResponse } from 'next/server';
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';

// Configurar cliente S3 con credenciales opcionales
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
  console.log('Using AWS default credential provider chain');
  return new S3Client({
    region,
  });
};

const BUCKET_NAME = process.env.RAW_DOCUMENTS_BUCKET || 'snail-bedrock-dev-raw-documents';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Validate PDF
    if (file.type !== 'application/pdf') {
      return NextResponse.json(
        { error: 'Only PDF files are allowed' },
        { status: 400 }
      );
    }

    // Convert file to buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Upload to S3
    const s3Client = getS3Client();
    const command = new PutObjectCommand({
      Bucket: BUCKET_NAME,
      Key: file.name,
      Body: buffer,
      ContentType: 'application/pdf',
    });

    console.log(`Uploading ${file.name} to bucket: ${BUCKET_NAME}`);
    await s3Client.send(command);
    console.log(`Successfully uploaded ${file.name}`);

    return NextResponse.json({
      success: true,
      message: 'File uploaded successfully',
      fileName: file.name,
    });
  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Failed to upload file' },
      { status: 500 }
    );
  }
}
