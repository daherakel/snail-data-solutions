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

interface Conversation {
  conversation_id: string;
  title: string;
  updated_at: number;
  message_count: number;
}

// Límites
const MAX_MESSAGES_DISPLAY = 50; // Máximo de mensajes en pantalla
const MAX_CONVERSATION_HISTORY = 30; // Máximo a enviar al backend (aumentado con Llama 3.3)

interface ChatProps {
  tenantId?: string;
  currentConversationId: string | null;
  onConversationCreated: (id: string) => void;
}

export default function Chat({ tenantId: propTenantId = 'default', currentConversationId, onConversationCreated }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [totalTokensUsed, setTotalTokensUsed] = useState(0);
  const [lastLoadedConversationId, setLastLoadedConversationId] = useState<string | null>(null);
  
  const tenantId = propTenantId;
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

  // Efecto para cargar mensajes cuando cambia la conversación
  useEffect(() => {
    if (currentConversationId && currentConversationId !== lastLoadedConversationId) {
      loadConversationMessages(currentConversationId);
    } else if (!currentConversationId) {
      // Si no hay conversación seleccionada (nueva conversación), limpiar mensajes
      setMessages([]);
      setLastLoadedConversationId(null);
    }
  }, [currentConversationId, lastLoadedConversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Cargar mensajes de una conversación específica
  const loadConversationMessages = async (conversationId: string) => {
    setMessages([]);
    setIsLoading(true);
    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'load_conversation',
          conversation_id: conversationId
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const loadedMessages: Message[] = (data.messages || []).map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          sources: msg.sources || [],
          excerpts: msg.excerpts || [],
          follow_up_questions: msg.follow_up_questions || [],
          user_intent: msg.user_intent,
          timestamp: new Date(msg.timestamp),
          usage: msg.usage
        }));
        setMessages(loadedMessages);
        setLastLoadedConversationId(conversationId);

        // Calcular tokens totales de esta conversación
        const totalTokens = loadedMessages.reduce((sum, msg) => {
          return sum + (msg.usage?.total_tokens || 0);
        }, 0);
        setTotalTokensUsed(totalTokens);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Calcular porcentaje de uso de tokens (asumiendo un presupuesto mensual)
  const MONTHLY_TOKEN_BUDGET = 200000; 
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
      // Preparar el request body con conversation_id
      const requestBody: any = {
        action: 'query',
        query: queryText,
        user_id: 'anonymous',
        tenant_id: tenantId
      };

      // Incluir conversation_id si existe
      if (currentConversationId) {
        requestBody.conversation_id = currentConversationId;
      }

      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      const responseTime = (Date.now() - startTime) / 1000; // en segundos

      // Notificar al padre si es una nueva conversación
      if (data.conversation_id && !currentConversationId) {
        onConversationCreated(data.conversation_id);
        setLastLoadedConversationId(data.conversation_id);
      }

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

  const clearCurrentConversation = () => {
    if (confirm('¿Estás seguro de que quieres limpiar la conversación visualmente?')) {
      setMessages([]);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900 relative">
      {/* Header - Simplified */}
      <div className="h-16 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-6 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md z-10 absolute top-0 w-full">
        <div className="flex items-center gap-3">
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              {currentConversationId ? 'Chat Activo' : 'Nueva Conversación'}
            </h3>
            <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-2">
              <span>{messages.length} mensajes</span>
              {totalTokensUsed > 0 && (
                <>
                  <span>•</span>
                  <span>{totalTokensUsed.toLocaleString()} tokens</span>
                </>
              )}
            </p>
          </div>
        </div>
        
        {messages.length > 0 && (
          <button
            onClick={clearCurrentConversation}
            className="text-xs px-3 py-1.5 text-gray-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
            title="Limpiar vista actual"
          >
            Limpiar Vista
          </button>
        )}
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-8 pt-24 space-y-6 scroll-smooth scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center p-8 max-w-2xl mx-auto animate-fadeIn">
            <div className="w-20 h-20 bg-gradient-to-tr from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-xl mb-6 rotate-3 hover:rotate-0 transition-transform duration-500">
              <span className="text-4xl">👋</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">
              ¿En qué puedo ayudarte hoy?
            </h2>
            <p className="text-base text-gray-600 dark:text-gray-400 mb-8 leading-relaxed max-w-md">
              Soy tu asistente inteligente. Puedo analizar documentos, responder preguntas técnicas y ayudarte a encontrar información rápidamente.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
              {[
                { icon: '📄', text: 'Resume este documento', desc: 'Puntos clave' },
                { icon: '🔍', text: 'Busca información', desc: 'Datos exactos' },
                { icon: '💡', text: 'Explica un concepto', desc: 'Definiciones' },
                { icon: '📊', text: 'Analiza datos', desc: 'Insights' }
              ].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => setInput(suggestion.text)}
                  className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-800 border border-gray-100 dark:border-gray-800 hover:border-blue-200 dark:hover:border-blue-900 hover:shadow-md rounded-xl transition-all duration-200 text-left group"
                >
                  <span className="text-xl group-hover:scale-110 transition-transform duration-200">{suggestion.icon}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{suggestion.text}</p>
                    <p className="text-[10px] text-gray-500 dark:text-gray-500">{suggestion.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-slideIn`}
          >
            <div
              className={`max-w-[85%] lg:max-w-[75%] rounded-2xl p-5 shadow-sm ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-tr-sm'
                  : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 border border-gray-100 dark:border-gray-700 rounded-tl-sm'
              }`}
            >
              {message.role === 'assistant' && (
                <div className="flex items-center gap-2 mb-3 opacity-70">
                  <div className="w-6 h-6 bg-indigo-100 dark:bg-indigo-900/50 rounded-md flex items-center justify-center">
                    <span className="text-xs">🤖</span>
                  </div>
                  <span className="text-xs font-medium">Snail AI</span>
                  {message.timestamp && (
                    <span className="text-xs text-gray-400">• {message.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  )}
                </div>
              )}

              <div className="prose prose-sm dark:prose-invert max-w-none">
                <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
              </div>

              {/* Sources & Metadata */}
              {message.role === 'assistant' && (
                <div className="mt-4 space-y-3 pt-3 border-t border-gray-100 dark:border-gray-700/50">
                  {message.sources && message.sources.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {message.sources.map((source, i) => (
                        <span key={i} className="inline-flex items-center px-2 py-1 rounded-md bg-gray-100 dark:bg-gray-700/50 text-xs text-gray-600 dark:text-gray-300 border border-gray-200 dark:border-gray-600">
                          📄 {source}
                        </span>
                      ))}
                    </div>
                  )}
                  
                  {/* Stats row */}
                  {message.usage && (
                    <div className="flex items-center gap-4 text-[10px] text-gray-400 uppercase tracking-wider font-medium">
                      <span>In: {message.usage.input_tokens}</span>
                      <span>Out: {message.usage.output_tokens}</span>
                      <span>Total: {message.usage.total_tokens}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Follow-up suggestions */}
              {message.follow_up_questions && message.follow_up_questions.length > 0 && (
                <div className="mt-4 flex flex-col gap-2">
                  {message.follow_up_questions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => setInput(q)}
                      className="text-left text-sm px-3 py-2 bg-indigo-50 dark:bg-indigo-900/20 text-indigo-700 dark:text-indigo-300 rounded-lg hover:bg-indigo-100 dark:hover:bg-indigo-900/40 transition-colors flex items-center gap-2 w-fit"
                    >
                      <span>↳</span> {q}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start animate-fadeIn">
            <div className="bg-white dark:bg-gray-800 rounded-2xl rounded-tl-sm p-4 shadow-sm border border-gray-100 dark:border-gray-700 flex items-center gap-3">
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              <span className="text-xs text-gray-400 font-medium ml-2">Pensando...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area - Fixed at bottom */}
      <div className="p-6 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800">
        <form onSubmit={sendMessage} className="max-w-4xl mx-auto relative">
          <div className="relative flex items-center gap-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl px-4 py-3 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all shadow-sm">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu mensaje aquí..."
              className="flex-1 bg-transparent border-none focus:ring-0 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-base"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className={`p-2 rounded-xl transition-all duration-200 ${
                isLoading || !input.trim()
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg transform hover:scale-105 active:scale-95'
              }`}
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19V5M5 12l7-7 7 7" />
                </svg>
              )}
            </button>
          </div>
          <div className="text-center mt-2">
            <p className="text-[10px] text-gray-400 dark:text-gray-500">
              Snail AI puede cometer errores. Verifica la información importante.
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
