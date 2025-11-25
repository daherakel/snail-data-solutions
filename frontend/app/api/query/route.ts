import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { query, conversation_history } = await request.json();

    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required and must be a string' },
        { status: 400 }
      );
    }

    const lambdaUrl = process.env.LAMBDA_QUERY_URL;

    if (!lambdaUrl) {
      console.error('LAMBDA_QUERY_URL not configured');
      return NextResponse.json(
        { error: 'Lambda endpoint not configured' },
        { status: 500 }
      );
    }

    const response = await fetch(lambdaUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        conversation_history: conversation_history || []
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Lambda error:', response.status, errorText);
      return NextResponse.json(
        { error: 'Failed to process query', details: errorText },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Query API error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}
