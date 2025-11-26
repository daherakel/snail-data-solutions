import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, query, conversation_id, user_id, new_title } = body;

    // Validar según la acción
    if (action === 'query' && (!query || typeof query !== 'string')) {
      return NextResponse.json(
        { error: 'Query is required and must be a string for query action' },
        { status: 400 }
      );
    }

    if (action === 'load_conversation' && !conversation_id) {
      return NextResponse.json(
        { error: 'conversation_id is required for load_conversation action' },
        { status: 400 }
      );
    }

    if (action === 'delete_conversation' && !conversation_id) {
      return NextResponse.json(
        { error: 'conversation_id is required for delete_conversation action' },
        { status: 400 }
      );
    }

    if (action === 'update_title' && (!conversation_id || !new_title)) {
      return NextResponse.json(
        { error: 'conversation_id and new_title are required for update_title action' },
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

    // Preparar request body para Lambda
    const lambdaBody: any = {
      action: action || 'query',
      user_id: user_id || 'anonymous'
    };

    // Agregar parámetros según la acción
    if (action === 'query' || !action) {
      lambdaBody.query = query;
      if (conversation_id) {
        lambdaBody.conversation_id = conversation_id;
      }
    } else if (action === 'load_conversation') {
      lambdaBody.conversation_id = conversation_id;
    } else if (action === 'delete_conversation') {
      lambdaBody.conversation_id = conversation_id;
    } else if (action === 'update_title') {
      lambdaBody.conversation_id = conversation_id;
      lambdaBody.new_title = new_title;
    }

    console.log('Sending to Lambda:', JSON.stringify(lambdaBody, null, 2));

    const response = await fetch(lambdaUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(lambdaBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Lambda error:', response.status, errorText);
      return NextResponse.json(
        { error: 'Failed to process request', details: errorText },
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
