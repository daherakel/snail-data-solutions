'use client';

import { useState, useEffect } from 'react';

interface Document {
  name: string;
  size: number;
  lastModified: string;
  key: string;
}

export default function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await fetch('/api/documents');

      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }

      const data = await response.json();
      
      // Verificar si hay error en la respuesta
      if (data.error) {
        throw new Error(data.details || data.error);
      }
      
      setDocuments(data.documents || []);
    } catch (err: any) {
      console.error('Error fetching documents:', err);
      const errorMessage = err.message || 'Error al cargar los documentos';
      
      // Mostrar mensaje de error más específico
      if (errorMessage.includes('credential')) {
        setError('Error de credenciales AWS. Verifica tu configuración en .env.local');
      } else if (errorMessage.includes('bucket')) {
        setError('Error al acceder al bucket de S3. Verifica la configuración.');
      } else {
        setError(errorMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <div className="relative w-20 h-20">
          <div className="absolute inset-0 rounded-full border-4 border-blue-200 dark:border-blue-900"></div>
          <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-600 dark:border-t-blue-400 animate-spin"></div>
        </div>
        <p className="text-lg text-gray-600 dark:text-gray-400 font-medium">Cargando documentos...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-6">
        <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
          <span className="text-3xl">⚠️</span>
        </div>
        <div className="text-center">
          <p className="text-xl font-semibold text-red-600 dark:text-red-400 mb-2">{error}</p>
          <p className="text-sm text-gray-600 dark:text-gray-400">Intenta recargar la página</p>
        </div>
        <button
          onClick={fetchDocuments}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 font-semibold shadow-lg transition-all duration-200 transform hover:scale-105"
        >
          🔄 Reintentar
        </button>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-6">
        <div className="w-24 h-24 bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-600 rounded-3xl flex items-center justify-center shadow-lg">
          <span className="text-6xl">📭</span>
        </div>
        <div className="text-center space-y-2">
          <p className="text-2xl font-bold text-gray-700 dark:text-gray-300">
            No hay documentos aún
          </p>
          <p className="text-lg text-gray-500 dark:text-gray-400">
            Sube tu primer documento desde la pestaña "Subir"
          </p>
        </div>
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-4 border border-blue-200 dark:border-blue-800">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            💡 Los documentos aparecerán aquí una vez que sean procesados
          </p>
        </div>
      </div>
    );
  }

  const totalSize = documents.reduce((acc, doc) => acc + doc.size, 0);

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            📚 Documentos Indexados
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {documents.length} documento{documents.length !== 1 ? 's' : ''} disponible{documents.length !== 1 ? 's' : ''} para consultas
          </p>
        </div>
        <button
          onClick={fetchDocuments}
          className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          🔄 Actualizar Lista
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-5 border border-blue-200 dark:border-blue-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Total Documentos</p>
              <p className="text-3xl font-bold text-blue-900 dark:text-blue-100 mt-1">{documents.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-2xl">📄</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-5 border border-purple-200 dark:border-purple-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Tamaño Total</p>
              <p className="text-3xl font-bold text-purple-900 dark:text-purple-100 mt-1">
                {(totalSize / 1024 / 1024).toFixed(1)} MB
              </p>
            </div>
            <div className="w-12 h-12 bg-purple-500 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-2xl">💾</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-5 border border-green-200 dark:border-green-800">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-600 dark:text-green-400">Estado</p>
              <p className="text-3xl font-bold text-green-900 dark:text-green-100 mt-1">Activo</p>
            </div>
            <div className="w-12 h-12 bg-green-500 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-2xl">✅</span>
            </div>
          </div>
        </div>
      </div>

      {/* Documents Grid */}
      <div className="grid gap-4">
        {documents.map((doc, index) => (
          <div
            key={index}
            className="group bg-gradient-to-br from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-600 hover:shadow-xl transition-all duration-300 transform hover:scale-[1.02]"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 flex-1">
                <div className="w-14 h-14 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md group-hover:shadow-lg group-hover:scale-110 transition-all duration-200">
                  <span className="text-3xl">📄</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-1">
                    {doc.name}
                  </h3>
                  <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <span className="text-blue-500">💾</span>
                      {(doc.size / 1024).toFixed(2)} KB
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-indigo-500">📅</span>
                      {new Date(doc.lastModified).toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="text-purple-500">🕐</span>
                      {new Date(doc.lastModified).toLocaleTimeString('es-ES', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="px-4 py-2 text-sm font-semibold bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 text-green-700 dark:text-green-300 rounded-xl border border-green-200 dark:border-green-700">
                  ✓ Indexado
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer Info */}
      <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-900/20 dark:via-indigo-900/20 dark:to-purple-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-800">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center flex-shrink-0">
            <span className="text-xl">💡</span>
          </div>
          <div className="flex-1">
            <p className="font-semibold text-blue-900 dark:text-blue-200 mb-2">
              Información del Sistema
            </p>
            <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
              <li>• Todos los documentos están vectorizados y listos para consultas</li>
              <li>• Búsqueda semántica usando embeddings de AWS Bedrock</li>
              <li>• Actualiza la lista para ver nuevos documentos procesados</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
