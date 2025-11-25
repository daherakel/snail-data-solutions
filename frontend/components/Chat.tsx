'use client';

import { useState, useRef, useEffect } from 'react';

interface Excerpt {
  source: string;
  text: string;
  relevance: number;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  excerpts?: Excerpt[];
  follow_up_questions?: string[];
  user_intent?: string;
  timestamp: Date;
  usage?: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
}

// Límites
const MAX_MESSAGES_DISPLAY = 50; // Máximo de mensajes en pantalla
const MAX_CONVERSATION_HISTORY = 10; // Máximo a enviar al backend

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [totalTokensUsed, setTotalTokensUsed] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Cargar tokens del localStorage al iniciar
  useEffect(() => {
    const savedTokens = localStorage.getItem('snail_total_tokens');
    if (savedTokens) {
      setTotalTokensUsed(parseInt(savedTokens, 10));
    }
  }, []);

  // Guardar tokens en localStorage cuando cambien
  useEffect(() => {
    localStorage.setItem('snail_total_tokens', totalTokensUsed.toString());
  }, [totalTokensUsed]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Calcular mensajes en contexto
  const contextMessagesCount = Math.min(messages.length, MAX_CONVERSATION_HISTORY);

  // Calcular porcentaje de uso de tokens (asumiendo un presupuesto mensual)
  const MONTHLY_TOKEN_BUDGET = 100000; // ~$0.30 con Claude Haiku
  const tokenUsagePercent = (totalTokensUsed / MONTHLY_TOKEN_BUDGET) * 100;

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const queryText = input;
    setInput('');
    setIsLoading(true);

    const startTime = Date.now();

    try {
      // Preparar historial conversacional (últimos 10 mensajes, excluyendo el actual)
      const conversationHistory = messages
        .slice(-MAX_CONVERSATION_HISTORY)
        .map(msg => ({
          role: msg.role,
          content: msg.content
        }));

      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: queryText,
          conversation_history: conversationHistory
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      const responseTime = (Date.now() - startTime) / 1000; // en segundos

      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer || 'No response received',
        sources: data.sources || [],
        excerpts: data.excerpts || [],
        follow_up_questions: data.follow_up_questions || [],
        user_intent: data.user_intent,
        timestamp: new Date(),
        usage: data.usage
      };

      setMessages(prev => {
        const newMessages = [...prev, assistantMessage];
        // Limitar mensajes en pantalla
        if (newMessages.length > MAX_MESSAGES_DISPLAY) {
          return newMessages.slice(-MAX_MESSAGES_DISPLAY);
        }
        return newMessages;
      });

      // Actualizar contador total de tokens
      if (data.usage) {
        setTotalTokensUsed(prev => prev + data.usage.total_tokens);
      }

      // Guardar log de query para analytics
      const queryLog = {
        query: queryText,
        timestamp: new Date().toISOString(),
        tokens: data.usage?.total_tokens || 0,
        responseTime,
        sources: data.sources || []
      };

      const existingLogs = localStorage.getItem('snail_query_logs');
      const logs = existingLogs ? JSON.parse(existingLogs) : [];
      logs.push(queryLog);

      // Mantener solo los últimos 100 logs
      if (logs.length > 100) {
        logs.shift();
      }

      localStorage.setItem('snail_query_logs', JSON.stringify(logs));

    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    if (confirm('¿Estás seguro de que quieres limpiar la conversación?')) {
      setMessages([]);
      setTotalTokensUsed(0);
      localStorage.setItem('snail_total_tokens', '0');
    }
  };

  return (
    <div className="flex flex-col h-[700px]">
      {/* Header con estadísticas mejoradas */}
      {messages.length > 0 && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 border-b border-gray-200 dark:border-gray-600 px-6 py-4">
          <div className="flex flex-col gap-4">
            {/* Primera fila: Stats y botón */}
            <div className="flex justify-between items-center">
              <div className="flex gap-6 items-center">
                {/* Contador de mensajes */}
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                    <span className="text-white text-sm font-bold">{messages.length}</span>
                  </div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    mensaje{messages.length !== 1 ? 's' : ''}
                  </span>
                </div>

                {/* Contexto conversacional */}
                <div className="flex items-center gap-2 px-3 py-1 bg-indigo-100 dark:bg-indigo-900/30 rounded-lg border border-indigo-300 dark:border-indigo-700">
                  <span className="text-indigo-600 dark:text-indigo-400 text-xs font-medium">
                    Contexto: {contextMessagesCount}/{MAX_CONVERSATION_HISTORY}
                  </span>
                  {contextMessagesCount >= MAX_CONVERSATION_HISTORY && (
                    <span className="text-xs" title="Usando máximo contexto conversacional">⚡</span>
                  )}
                </div>

                {/* Contador de tokens */}
                <div className="flex items-center gap-2">
                  <span className="text-2xl">💰</span>
                  <div className="flex flex-col">
                    <span className="text-xs text-gray-500 dark:text-gray-400">Tokens</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">
                      {totalTokensUsed.toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={clearConversation}
                className="text-xs px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors font-medium"
              >
                🗑️ Limpiar conversación
              </button>
            </div>

            {/* Segunda fila: Barra de progreso de tokens */}
            <div className="space-y-1">
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-600 dark:text-gray-400">
                  Uso de presupuesto mensual ({MONTHLY_TOKEN_BUDGET.toLocaleString()} tokens)
                </span>
                <span className={`font-semibold ${
                  tokenUsagePercent >= 80 ? 'text-red-600 dark:text-red-400' :
                  tokenUsagePercent >= 50 ? 'text-yellow-600 dark:text-yellow-400' :
                  'text-green-600 dark:text-green-400'
                }`}>
                  {tokenUsagePercent.toFixed(1)}%
                </span>
              </div>
              <div className="w-full h-2 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 rounded-full ${
                    tokenUsagePercent >= 80 ? 'bg-gradient-to-r from-red-500 to-red-600' :
                    tokenUsagePercent >= 50 ? 'bg-gradient-to-r from-yellow-500 to-yellow-600' :
                    'bg-gradient-to-r from-green-500 to-green-600'
                  }`}
                  style={{ width: `${Math.min(tokenUsagePercent, 100)}%` }}
                ></div>
              </div>
              {tokenUsagePercent >= 80 && (
                <p className="text-xs text-red-600 dark:text-red-400 flex items-center gap-1">
                  <span>⚠️</span>
                  Advertencia: Has usado {tokenUsagePercent.toFixed(0)}% del presupuesto mensual
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-20 space-y-6">
            <div className="flex justify-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
                <span className="text-4xl">💬</span>
              </div>
            </div>
            <div>
              <p className="text-2xl font-bold mb-2 text-gray-700 dark:text-gray-300">¡Hola! Soy tu asistente de documentos con IA</p>
              <p className="text-lg">Pregúntame cualquier cosa sobre los documentos que hayas subido.</p>
              <p className="text-sm text-gray-500 dark:text-gray-500 mt-3">
                💡 Mantengo contexto de la conversación para respuestas más precisas
              </p>
            </div>
            <div className="mt-8 space-y-3 text-left max-w-md mx-auto">
              <p className="font-semibold text-gray-700 dark:text-gray-300 text-center mb-4">Ejemplos de preguntas:</p>
              <div className="space-y-2">
                <button
                  onClick={() => setInput("¿Cuáles son las tecnologías utilizadas?")}
                  className="w-full text-left p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600 rounded-xl hover:shadow-md transition-all duration-200 border border-blue-200 dark:border-gray-600"
                >
                  <span className="text-blue-600 dark:text-blue-400 font-medium">💡</span> "¿Cuáles son las tecnologías utilizadas?"
                </button>
                <button
                  onClick={() => setInput("¿Cuánto cuesta el sistema?")}
                  className="w-full text-left p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600 rounded-xl hover:shadow-md transition-all duration-200 border border-blue-200 dark:border-gray-600"
                >
                  <span className="text-indigo-600 dark:text-indigo-400 font-medium">💰</span> "¿Cuánto cuesta el sistema?"
                </button>
                <button
                  onClick={() => setInput("Resume el documento en 3 puntos")}
                  className="w-full text-left p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-gray-700 dark:to-gray-600 rounded-xl hover:shadow-md transition-all duration-200 border border-blue-200 dark:border-gray-600"
                >
                  <span className="text-purple-600 dark:text-purple-400 font-medium">📝</span> "Resume el documento en 3 puntos"
                </button>
              </div>
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-5 shadow-lg ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white'
                  : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-600'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mr-2">
                      <span className="text-lg">🤖</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Snail AI Assistant</span>
                  </div>
                  {message.user_intent && message.user_intent !== 'question' && (
                    <span className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded-lg font-medium">
                      {message.user_intent === 'summarize' && '📝 Resumen'}
                      {message.user_intent === 'explain' && '💡 Explicación'}
                      {message.user_intent === 'list' && '📋 Lista'}
                      {message.user_intent === 'compare' && '⚖️ Comparación'}
                      {message.user_intent === 'search' && '🔍 Búsqueda'}
                    </span>
                  )}
                </div>
              )}
              <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>

              {/* Extractos relevantes */}
              {message.role === 'assistant' && message.excerpts && message.excerpts.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
                  <p className="font-semibold text-sm mb-2 flex items-center">
                    <span className="mr-2">📄</span>
                    Extractos relevantes:
                  </p>
                  <div className="space-y-2">
                    {message.excerpts.map((excerpt, i) => (
                      <div key={i} className="text-xs bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-semibold text-blue-700 dark:text-blue-300">{excerpt.source}</span>
                          <span className="text-blue-600 dark:text-blue-400">
                            Relevancia: {(excerpt.relevance * 100).toFixed(0)}%
                          </span>
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 italic">"{excerpt.text}"</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Mostrar uso de tokens para respuestas del asistente */}
              {message.role === 'assistant' && message.usage && (
                <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
                  <div className="flex gap-4 text-xs text-gray-600 dark:text-gray-400">
                    <span title="Tokens de entrada (contexto + pregunta)">
                      📥 {message.usage.input_tokens}
                    </span>
                    <span title="Tokens de salida (respuesta)">
                      📤 {message.usage.output_tokens}
                    </span>
                    <span title="Total de tokens para esta respuesta" className="font-semibold">
                      💰 {message.usage.total_tokens} tokens
                    </span>
                  </div>
                </div>
              )}

              {message.sources && message.sources.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
                  <p className="font-semibold text-sm mb-2 flex items-center">
                    <span className="mr-2">📚</span>
                    Fuentes:
                  </p>
                  <div className="space-y-1">
                    {message.sources.map((source, i) => (
                      <div key={i} className="text-xs bg-gray-100 dark:bg-gray-800 rounded-lg px-3 py-1 inline-block mr-2 mb-1">
                        {source}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Preguntas de follow-up */}
              {message.role === 'assistant' && message.follow_up_questions && message.follow_up_questions.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-300 dark:border-gray-600">
                  <p className="font-semibold text-sm mb-3 flex items-center">
                    <span className="mr-2">💭</span>
                    También podrías preguntar:
                  </p>
                  <div className="space-y-2">
                    {message.follow_up_questions.map((question, i) => (
                      <button
                        key={i}
                        onClick={() => setInput(question)}
                        className="w-full text-left p-3 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-xl hover:shadow-md transition-all duration-200 border border-indigo-200 dark:border-indigo-800 text-sm text-gray-700 dark:text-gray-300 hover:border-indigo-400 dark:hover:border-indigo-600"
                      >
                        <span className="text-indigo-600 dark:text-indigo-400 font-medium mr-2">•</span>
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <p className="text-xs mt-3 opacity-60">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start animate-fadeIn">
            <div className="bg-white dark:bg-gray-700 rounded-2xl p-5 shadow-lg border border-gray-200 dark:border-gray-600 max-w-[80%]">
              <div className="flex items-center mb-3">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center mr-2">
                  <span className="text-lg">🤖</span>
                </div>
                <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Snail AI Assistant</span>
              </div>
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-3 h-3 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={sendMessage} className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900/50">
        <div className="flex space-x-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Escribe tu pregunta... (máx. 500 caracteres)"
            maxLength={500}
            className="flex-1 p-4 border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all duration-200 text-base"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
          >
            {isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Enviando...
              </span>
            ) : (
              '✈️ Enviar'
            )}
          </button>
        </div>
        {/* Contador de caracteres e info */}
        <div className="flex justify-between items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
          <div className="flex gap-4">
            <span>💡 Hasta {MAX_CONVERSATION_HISTORY} mensajes como contexto</span>
            <span>📊 Presupuesto: {MONTHLY_TOKEN_BUDGET.toLocaleString()} tokens/mes</span>
          </div>
          <span>{input.length}/500 caracteres</span>
        </div>
      </form>
    </div>
  );
}
