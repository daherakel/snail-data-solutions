/**
 * Gemini Service
 * Servicio para interactuar con Google Gemini API
 * 
 * NOTA: Este servicio es SOLO para debugging y resolver problemas.
 * NO debe usarse en producción para ahorrar costos.
 * Solo habilitar cuando se necesite debugging avanzado.
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

// Configuración
const GEMINI_API_KEY = process.env.NEXT_PUBLIC_GEMINI_API_KEY || process.env.GEMINI_API_KEY;
const GEMINI_ENABLED = process.env.NEXT_PUBLIC_GEMINI_ENABLED === 'true' || !!GEMINI_API_KEY;
const GEMINI_MODEL = 'gemini-2.0-flash-exp'; // Usar Gemini 3 Pro cuando esté disponible, por ahora Flash

let genAI: GoogleGenerativeAI | null = null;
let model: any = null;

// Inicializar Gemini solo si está habilitado y hay API key
if (GEMINI_ENABLED && GEMINI_API_KEY) {
  try {
    genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
    model = genAI.getGenerativeModel({ model: GEMINI_MODEL });
  } catch (error) {
    console.error('Error inicializando Gemini:', error);
  }
}

export interface SuggestionOptions {
  conversationHistory?: Array<{ role: 'user' | 'assistant'; content: string }>;
  currentQuery?: string;
  context?: string;
  maxSuggestions?: number;
}

export interface FormattedResponse {
  formatted: string;
  suggestions?: string[];
}

/**
 * Genera sugerencias de preguntas de seguimiento basadas en el contexto de la conversación
 */
export async function generateFollowUpSuggestions(
  options: SuggestionOptions
): Promise<string[]> {
  if (!GEMINI_ENABLED || !model) {
    return [];
  }

  try {
    const { conversationHistory = [], currentQuery, context, maxSuggestions = 3 } = options;

    // Construir contexto de la conversación
    let conversationContext = '';
    if (conversationHistory.length > 0) {
      conversationContext = conversationHistory
        .slice(-5) // Últimas 5 interacciones
        .map((msg) => `${msg.role === 'user' ? 'Usuario' : 'Asistente'}: ${msg.content}`)
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

    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    // Parsear sugerencias (una por línea)
    const suggestions = text
      .split('\n')
      .map((s) => s.trim())
      .filter((s) => s.length > 0 && !s.match(/^\d+[\.\)]/)) // Filtrar numeración
      .slice(0, maxSuggestions);

    return suggestions;
  } catch (error) {
    console.error('Error generando sugerencias con Gemini:', error);
    return [];
  }
}

/**
 * Mejora y formatea una respuesta del backend antes de mostrarla al usuario
 */
export async function enhanceResponse(
  response: string,
  options?: { conversationContext?: string }
): Promise<FormattedResponse> {
  if (!GEMINI_ENABLED || !model) {
    return { formatted: response };
  }

  try {
    const prompt = `Eres un asistente que mejora y formatea respuestas para hacerlas más claras y profesionales.

Respuesta original:
${response}

${options?.conversationContext ? `Contexto de la conversación: ${options.conversationContext}` : ''}

Mejora la respuesta manteniendo:
1. El contenido original y la información técnica
2. Un tono cálido y profesional
3. Formato claro con párrafos bien estructurados
4. Lenguaje natural en español

Responde SOLO con la respuesta mejorada, sin comentarios adicionales.`;

    const result = await model.generateContent(prompt);
    const formatted = (await result.response).text();

    return { formatted };
  } catch (error) {
    console.error('Error mejorando respuesta con Gemini:', error);
    // Fallback: retornar respuesta original si falla
    return { formatted: response };
  }
}

/**
 * Genera sugerencias contextuales mientras el usuario escribe
 */
export async function generateContextualSuggestions(
  partialQuery: string,
  conversationHistory?: Array<{ role: 'user' | 'assistant'; content: string }>
): Promise<string[]> {
  if (!GEMINI_ENABLED || !model || partialQuery.length < 3) {
    return [];
  }

  try {
    const context = conversationHistory
      ?.slice(-3)
      .map((msg) => `${msg.role === 'user' ? 'Usuario' : 'Asistente'}: ${msg.content}`)
      .join('\n') || '';

    const prompt = `El usuario está escribiendo una pregunta. Basándote en el contexto y lo que ha escrito hasta ahora, sugiere cómo podría completar su pregunta.

Contexto:
${context}

Texto escrito hasta ahora: "${partialQuery}"

Genera 2-3 sugerencias cortas de cómo podría completar la pregunta. Responde SOLO con las sugerencias, una por línea, sin numeración.`;

    const result = await model.generateContent(prompt);
    const suggestions = (await result.response)
      .text()
      .split('\n')
      .map((s) => s.trim())
      .filter((s) => s.length > 0)
      .slice(0, 3);

    return suggestions;
  } catch (error) {
    console.error('Error generando sugerencias contextuales:', error);
    return [];
  }
}

/**
 * Verifica si Gemini está disponible y configurado
 */
export function isGeminiAvailable(): boolean {
  return GEMINI_ENABLED && !!GEMINI_API_KEY && !!model;
}

