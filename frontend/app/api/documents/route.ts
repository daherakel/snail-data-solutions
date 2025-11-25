import { NextResponse } from 'next/server';
import { S3Client, ListObjectsV2Command } from '@aws-sdk/client-s3';

const s3Client = new S3Client({
  region: process.env.AWS_REGION || 'us-east-1',
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID || '',
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || '',
  },
});

const BUCKET_NAME = 'snail-bedrock-dev-raw-documents';

export async function GET() {
  try {
    const command = new ListObjectsV2Command({
      Bucket: BUCKET_NAME,
    });

    const response = await s3Client.send(command);

    const documents = (response.Contents || [])
      .filter((item) => item.Key && item.Key.endsWith('.pdf'))
      .map((item) => ({
        name: item.Key!.split('/').pop() || item.Key!,
        key: item.Key!,
        size: item.Size || 0,
        lastModified: item.LastModified?.toISOString() || '',
      }));

    return NextResponse.json({ documents });
  } catch (error) {
    console.error('Error fetching documents:', error);
    return NextResponse.json(
      { error: 'Failed to fetch documents' },
      { status: 500 }
    );
  }
}
