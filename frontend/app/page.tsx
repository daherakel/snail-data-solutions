'use client';

import { useState } from 'react';
import Chat from '@/components/Chat';
import DocumentUpload from '@/components/DocumentUpload';
import DocumentList from '@/components/DocumentList';
import Analytics from '@/components/Analytics';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'documents' | 'analytics'>('chat');

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-gray-900 dark:via-slate-900 dark:to-indigo-950">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-2xl">🐌</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                  Snail Data Solutions
                </h1>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  AI Document Assistant powered by AWS Bedrock
                </p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-2 text-sm">
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full font-medium">
                ✓ Active
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Hero Section */}
        <div className="text-center mb-8 space-y-4">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-3">
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600">
              Asistente de IA
            </span>
            {' '}para Documentos
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            Conversa con tus documentos usando inteligencia artificial avanzada.
            Sube PDFs, haz preguntas y obtén respuestas precisas al instante.
          </p>

          {/* Stats */}
          <div className="flex flex-wrap justify-center gap-8 mt-6 text-sm">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">Claude AI</div>
              <div className="text-gray-600 dark:text-gray-400">Powered by Anthropic</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">FAISS</div>
              <div className="text-gray-600 dark:text-gray-400">Vector Search</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">AWS</div>
              <div className="text-gray-600 dark:text-gray-400">Bedrock & Lambda</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-white dark:bg-gray-800 rounded-xl p-1 shadow-xl border border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 ${
                activeTab === 'chat'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/50'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              💬 Chat
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 ${
                activeTab === 'upload'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/50'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              📤 Subir
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 ${
                activeTab === 'documents'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/50'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              📚 Documentos
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 ${
                activeTab === 'analytics'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg shadow-blue-500/50'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              📊 Analytics
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 overflow-hidden backdrop-blur-sm">
          <div className="transition-all duration-300">
            {activeTab === 'chat' && <Chat />}
            {activeTab === 'upload' && <DocumentUpload />}
            {activeTab === 'documents' && <DocumentList />}
            {activeTab === 'analytics' && <Analytics />}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center space-y-2">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p className="font-semibold">Powered by Snail Data Solutions</p>
            <p className="text-xs">AWS Bedrock • Claude AI • FAISS Vector Search</p>
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-500">
            <p>Cost-Efficient: ~$0.78/month (POC) | ~$19/month (Production)</p>
          </div>
        </div>
      </div>
    </main>
  );
}
