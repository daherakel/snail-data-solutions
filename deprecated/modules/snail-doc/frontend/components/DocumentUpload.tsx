'use client';

import { useState, useCallback } from 'react';

export default function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
      setUploadStatus('idle');
    } else {
      setMessage('Por favor sube un archivo PDF válido');
      setUploadStatus('error');
    }
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setUploadStatus('idle');
    } else {
      setMessage('Por favor sube un archivo PDF válido');
      setUploadStatus('error');
    }
  };

  const uploadFile = async () => {
    if (!file) return;

    setUploading(true);
    setUploadStatus('idle');
    setMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();

      setUploadStatus('success');
      setMessage(`✅ ${file.name} subido exitosamente! Se procesará automáticamente.`);
      setFile(null);

      setTimeout(() => {
        setUploadStatus('idle');
        setMessage('');
      }, 5000);
    } catch (error) {
      console.error('Error uploading:', error);
      setUploadStatus('error');
      setMessage('❌ Error al subir el archivo. Por favor intenta de nuevo.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-8 p-6">
      {/* Header */}
      <div className="text-center space-y-3">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
            <span className="text-3xl">📤</span>
          </div>
        </div>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
          Subir Documento PDF
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
          Los documentos se procesarán automáticamente usando IA y estarán disponibles para consultas en segundos
        </p>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative border-2 border-dashed rounded-2xl p-16 text-center transition-all duration-300 ${
          isDragging
            ? 'border-blue-500 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/30 dark:to-indigo-900/30 scale-105'
            : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-gray-50 dark:hover:bg-gray-700/30'
        }`}
      >
        {isDragging && (
          <div className="absolute inset-0 bg-blue-500/10 dark:bg-blue-500/20 rounded-2xl animate-pulse"></div>
        )}
        <div className="relative space-y-6">
          <div className="text-7xl animate-bounce">
            {isDragging ? '🎯' : '📄'}
          </div>
          <div>
            <p className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {isDragging ? '¡Suelta el archivo aquí!' : 'Arrastra y suelta tu PDF aquí'}
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              o haz click en el botón para seleccionar
            </p>
          </div>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="inline-block px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 cursor-pointer transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            📁 Seleccionar Archivo
          </label>

          {/* File format indicator */}
          <div className="flex justify-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">PDF</span>
            <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full">Max 10MB</span>
          </div>
        </div>
      </div>

      {/* Selected File Card */}
      {file && (
        <div className="bg-gradient-to-br from-white to-gray-50 dark:from-gray-700 dark:to-gray-800 rounded-2xl p-6 shadow-xl border border-gray-200 dark:border-gray-600 animate-fadeIn">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 flex-1">
              <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl flex items-center justify-center shadow-md">
                <span className="text-2xl">📄</span>
              </div>
              <div className="flex-1">
                <p className="font-semibold text-gray-900 dark:text-white text-lg">{file.name}</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={uploadFile}
              disabled={uploading}
              className="px-8 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
            >
              {uploading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Subiendo...
                </span>
              ) : (
                '🚀 Subir Documento'
              )}
            </button>
          </div>
        </div>
      )}

      {/* Status Message */}
      {message && (
        <div
          className={`p-5 rounded-2xl shadow-lg animate-fadeIn ${
            uploadStatus === 'success'
              ? 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/30 dark:to-emerald-900/30 border-2 border-green-200 dark:border-green-700'
              : 'bg-gradient-to-r from-red-50 to-pink-50 dark:from-red-900/30 dark:to-pink-900/30 border-2 border-red-200 dark:border-red-700'
          }`}
        >
          <p className={`font-medium ${
            uploadStatus === 'success'
              ? 'text-green-800 dark:text-green-200'
              : 'text-red-800 dark:text-red-200'
          }`}>
            {message}
          </p>
        </div>
      )}

      {/* Info Cards */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-2xl p-6 border border-blue-200 dark:border-blue-800">
          <h3 className="font-bold text-blue-900 dark:text-blue-200 mb-3 flex items-center text-lg">
            <span className="mr-2">⚡</span>
            Proceso Automático
          </h3>
          <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-2">
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Procesamiento con IA en ~4-10 segundos</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Extracción de texto y vectorización</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Indexación en base de datos vectorial</span>
            </li>
          </ul>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-2xl p-6 border border-purple-200 dark:border-purple-800">
          <h3 className="font-bold text-purple-900 dark:text-purple-200 mb-3 flex items-center text-lg">
            <span className="mr-2">📋</span>
            Especificaciones
          </h3>
          <ul className="text-sm text-purple-800 dark:text-purple-300 space-y-2">
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Formato: PDF</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Tamaño máximo: 10 MB</span>
            </li>
            <li className="flex items-start">
              <span className="mr-2">•</span>
              <span>Disponible inmediatamente para consultas</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
