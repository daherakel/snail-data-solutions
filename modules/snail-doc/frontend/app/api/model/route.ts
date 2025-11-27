import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const tenantId = searchParams.get('tenant_id') || 'default';

    const lambdaUrl = process.env.LAMBDA_QUERY_URL;

    if (!lambdaUrl) {
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
        action: 'get_model',
        tenant_id: tenantId,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
      return NextResponse.json(
        { error: errorData.error || 'Failed to get model' },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Model API error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { tenant_id = 'default', model_id } = body;

    if (!model_id) {
      return NextResponse.json(
        { error: 'model_id is required' },
        { status: 400 }
      );
    }

    const lambdaUrl = process.env.LAMBDA_QUERY_URL;

    if (!lambdaUrl) {
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
        action: 'update_model',
        tenant_id,
        model_id,
      }),
    });

    // El Function URL devuelve directamente el body parseado como JSON
    const responseData = await response.json();
    
    // Si el Lambda devuelve un objeto con statusCode (invocación directa)
    if (responseData.statusCode) {
      const bodyData = typeof responseData.body === 'string' 
        ? JSON.parse(responseData.body) 
        : responseData.body;
      
      if (responseData.statusCode >= 400 || !bodyData.success) {
        return NextResponse.json(
          { error: bodyData.message || bodyData.error || 'Failed to update model' },
          { status: responseData.statusCode }
        );
      }
      
      return NextResponse.json(bodyData);
    }

    // Si viene directamente del Function URL (respuesta directa)
    // El Function URL parsea automáticamente el body del Lambda
    if (!response.ok) {
      return NextResponse.json(
        { error: responseData.message || responseData.error || 'Failed to update model' },
        { status: response.status }
      );
    }

    // Verificar si success es false en la respuesta directa
    if (responseData.success === false) {
      return NextResponse.json(
        { error: responseData.message || responseData.error || 'Failed to update model' },
        { status: 400 }
      );
    }

    return NextResponse.json(responseData);
  } catch (error) {
    console.error('Model API error:', error);
    return NextResponse.json(
      { error: 'Internal server error', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

