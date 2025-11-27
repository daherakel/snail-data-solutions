'use client';

import { useState, useEffect } from 'react';
import Chat from '@/components/Chat';
import DocumentUpload from '@/components/DocumentUpload';
import DocumentList from '@/components/DocumentList';
import Analytics from '@/components/Analytics';
import Admin from '@/components/Admin';

// Definir tipo para Conversation
interface Conversation {
  conversation_id: string;
  title: string;
  updated_at: number;
  message_count: number;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'upload' | 'documents' | 'analytics' | 'admin'>('chat');
  const [tenantId, setTenantId] = useState('default');
  
  // State para conversaciones (movido desde Chat.tsx)
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [editingConvId, setEditingConvId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  const [openMenuId, setOpenMenuId] = useState<string | null>(null);

  const menuItems = [
    { id: 'chat', label: 'Chat' },
    { id: 'upload', label: 'Subir' },
    { id: 'documents', label: 'Documentos' },
    { id: 'analytics', label: 'Analytics' },
    { id: 'admin', label: 'Admin' },
  ];

  // Cargar conversaciones al montar
  useEffect(() => {
    loadConversations();
  }, []);

  // Cerrar menú cuando se hace click fuera
  useEffect(() => {
    const handleClickOutside = () => {
      if (openMenuId) setOpenMenuId(null);
    };
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [openMenuId]);

  const loadConversations = async () => {
    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'list_conversations',
          user_id: 'anonymous'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const createNewConversation = async () => {
    setActiveTab('chat'); // Asegurar que vamos al chat
    setCurrentConversationId(null); // Limpiar selección para indicar "nueva"
    // Nota: No creamos la conversación en backend hasta enviar el primer mensaje,
    // pero visualmente limpiamos el chat.
  };

  const handleConversationCreated = (newId: string) => {
    setCurrentConversationId(newId);
    loadConversations();
  };

  const switchConversation = (id: string) => {
    setCurrentConversationId(id);
    setActiveTab('chat');
  };

  // Funciones de gestión de conversaciones
  const deleteConversation = async (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('¿Estás seguro de que quieres eliminar esta conversación?')) return;

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'delete_conversation',
          conversation_id: conversationId,
          user_id: 'anonymous'
        }),
      });

      if (response.ok) {
        if (conversationId === currentConversationId) {
          setCurrentConversationId(null);
        }
        await loadConversations();
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const startEditTitle = (conv: Conversation, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingConvId(conv.conversation_id);
    setEditingTitle(conv.title);
  };

  const saveTitle = async (conversationId: string) => {
    if (!editingTitle.trim()) {
      setEditingConvId(null);
      return;
    }

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'update_title',
          conversation_id: conversationId,
          new_title: editingTitle.trim(),
          user_id: 'anonymous'
        }),
      });

      if (response.ok) {
        setEditingConvId(null);
        await loadConversations();
      }
    } catch (error) {
      console.error('Error updating title:', error);
    }
  };

  const toggleMenu = (conversationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setOpenMenuId(openMenuId === conversationId ? null : conversationId);
  };

  return (
    <main className="h-screen w-screen flex bg-gray-50 dark:bg-gray-950 overflow-hidden">
      {/* Unified Sidebar */}
      <div className={`w-64 bg-gray-900 text-gray-300 flex flex-col flex-shrink-0 transition-all duration-300 border-r border-gray-800`}>
        {/* Logo Area */}
        <div className="h-16 flex items-center px-6 border-b border-gray-800">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg flex-shrink-0 mr-3">
            <span className="text-xl">🐌</span>
          </div>
          <h1 className="font-bold text-white tracking-wide">Snail Data</h1>
        </div>

        {/* Menu Navigation (Text Only) */}
        <div className="py-4 px-3 space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id as any)}
              className={`w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === item.id
                  ? 'bg-gray-800 text-white'
                  : 'hover:bg-gray-800/50 hover:text-white'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Divider */}
        <div className="mx-4 my-2 border-t border-gray-800/50"></div>

        {/* Conversations Header */}
        <div className="px-4 py-2 flex items-center justify-between group">
          <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">Conversaciones</span>
          <button 
            onClick={createNewConversation}
            className="text-gray-400 hover:text-white p-1 rounded hover:bg-gray-800 transition-colors"
            title="Nueva conversación"
          >
            +
          </button>
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 scrollbar-thin scrollbar-thumb-gray-700">
          {conversations.map((conv) => (
            <div
              key={conv.conversation_id}
              className={`group relative w-full text-left px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                currentConversationId === conv.conversation_id
                  ? 'bg-gray-800 text-white'
                  : 'text-gray-400 hover:bg-gray-800/30 hover:text-gray-200'
              }`}
              onClick={() => switchConversation(conv.conversation_id)}
            >
              {editingConvId === conv.conversation_id ? (
                <div className="flex items-center gap-1">
                  <input
                    type="text"
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') saveTitle(conv.conversation_id);
                      if (e.key === 'Escape') setEditingConvId(null);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="w-full bg-gray-900 border border-blue-500 rounded px-1 py-0.5 text-xs text-white focus:outline-none"
                    autoFocus
                  />
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <span className="truncate text-sm flex-1 pr-2">
                    {conv.title || 'Nueva conversación'}
                  </span>
                  
                  {/* Menu Trigger (Visible on hover or active) */}
                  <button
                    onClick={(e) => toggleMenu(conv.conversation_id, e)}
                    className={`opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-700 rounded ${
                      openMenuId === conv.conversation_id ? 'opacity-100 bg-gray-700' : ''
                    }`}
                  >
                    <span className="block text-xs leading-none">⋮</span>
                  </button>

                  {/* Dropdown Menu */}
                  {openMenuId === conv.conversation_id && (
                    <div className="absolute right-2 top-8 w-32 bg-gray-800 rounded-md shadow-xl border border-gray-700 z-50 py-1">
                      <button
                        onClick={(e) => startEditTitle(conv, e)}
                        className="w-full text-left px-3 py-2 text-xs text-gray-300 hover:bg-gray-700 flex items-center gap-2"
                      >
                        ✏️ Editar
                      </button>
                      <button
                        onClick={(e) => deleteConversation(conv.conversation_id, e)}
                        className="w-full text-left px-3 py-2 text-xs text-red-400 hover:bg-gray-700 flex items-center gap-2"
                      >
                        🗑️ Eliminar
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* User Profile */}
        <div className="p-4 border-t border-gray-800 bg-gray-900">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center text-xs font-bold text-white">
              {tenantId.slice(0, 2).toUpperCase()}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium text-white truncate">
                {tenantId === 'default' ? 'Default Tenant' : tenantId}
              </p>
              <p className="text-xs text-green-400 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                Online
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-hidden relative bg-white dark:bg-gray-950">
        {/* Active Component Container */}
        <div className="flex-1 overflow-hidden relative">
          {activeTab === 'chat' ? (
             <div className="absolute inset-0">
               <Chat 
                 tenantId={tenantId} 
                 currentConversationId={currentConversationId}
                 onConversationCreated={handleConversationCreated}
               />
             </div>
          ) : (
            <div className="h-full w-full overflow-y-auto p-4 lg:p-8 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700">
              <div className="max-w-5xl mx-auto animate-fadeIn">
                {activeTab === 'upload' && <DocumentUpload />}
                {activeTab === 'documents' && <DocumentList />}
                {activeTab === 'analytics' && <Analytics />}
                {activeTab === 'admin' && <Admin tenantId={tenantId} setTenantId={setTenantId} />}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
