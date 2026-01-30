/**
 * API Route para Gemini (Server-side proxy)
 * Permite usar Gemini desde el servidor para evitar exponer API keys en el cliente
 */

import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_MODEL = 'gemini-2.0-flash-exp';

export async function POST(request: NextRequest) {
  try {
    if (!GEMINI_API_KEY) {
      return NextResponse.json(
        { error: 'Gemini API key not configured' },
        { status: 500 }
      );
    }

    const body = await request.json();
    const { action, ...options } = body;

    const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: GEMINI_MODEL });

    let result;

    switch (action) {
      case 'generate_suggestions':
        const { conversationHistory, currentQuery, context, maxSuggestions = 3 } = options;
        
        let conversationContext = '';
        if (conversationHistory?.length > 0) {
          conversationContext = conversationHistory
            .slice(-5)
            .map((msg: any) => `${msg.role === 'user' ? 'Usuario' : 'Asistente'}: ${msg.content}`)
            .join('\n');
        }

        const prompt = `Eres un asistente que ayuda a generar sugerencias de preguntas de seguimiento relevantes y útiles.

Contexto de la conversación:
${conversationContext}

${currentQuery ? `Pregunta actual del usuario: ${currentQuery}` : ''}
${context ? `Información adicional: ${context}` : ''}

Genera ${maxSuggestions} sugerencias de preguntas de seguimiento que sean:
1. Relevantes al contexto de la conversación
2. Útiles y específicas
3. Naturales y conversacionales
4. En español

Responde SOLO con las preguntas, una por línea, sin numeración ni viñetas.`;

        const genResult = await model.generateContent(prompt);
        const text = (await genResult.response).text();
        
        const suggestions = text
          .split('\n')
          .map((s) => s.trim())
          .filter((s) => s.length > 0 && !s.match(/^\d+[\.\)]/))
          .slice(0, maxSuggestions);

        result = { suggestions };
        break;

      case 'enhance_response':
        const { response, conversationContext: convContext } = options;
        
        const enhancePrompt = `Eres un asistente que mejora y formatea respuestas para hacerlas más claras y profesionales.

Respuesta original:
${response}

${convContext ? `Contexto de la conversación: ${convContext}` : ''}

Mejora la respuesta manteniendo:
1. El contenido original y la información técnica
2. Un tono cálido y profesional
3. Formato claro con párrafos bien estructurados
4. Lenguaje natural en español

Responde SOLO con la respuesta mejorada, sin comentarios adicionales.`;

        const enhanceResult = await model.generateContent(enhancePrompt);
        const formatted = (await enhanceResult.response).text();
        
        result = { formatted };
        break;

      default:
        return NextResponse.json(
          { error: 'Invalid action' },
          { status: 400 }
        );
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Gemini API error:', error);
    return NextResponse.json(
      { error: 'Failed to process Gemini request', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

