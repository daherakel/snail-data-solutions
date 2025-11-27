'use client';

import { useState, useEffect } from 'react';

interface AdminProps {
  tenantId: string;
  setTenantId: (id: string) => void;
}

interface ModelOption {
  id: string;
  name: string;
  category: 'economico' | 'moderado' | 'bueno';
  description: string;
  cost: string;
}

const MODELS: ModelOption[] = [
  {
    id: 'anthropic.claude-3-haiku-20240307-v1:0',
    name: 'Claude 3 Haiku',
    category: 'economico',
    description: 'Modelo económico ideal para POC y desarrollo',
    cost: '$0.25/$1.25 por 1M tokens'
  },
  {
    id: 'anthropic.claude-3-sonnet-20240229-v1:0',
    name: 'Claude 3 Sonnet',
    category: 'moderado',
    description: 'Balance perfecto entre calidad y costo',
    cost: '$3/$15 por 1M tokens'
  },
  {
    id: 'anthropic.claude-3-5-sonnet-20241022-v2:0',
    name: 'Claude 3.5 Sonnet',
    category: 'moderado',
    description: 'Mejor calidad con costo razonable',
    cost: '$3/$15 por 1M tokens'
  },
  {
    id: 'anthropic.claude-opus-4-5-20251101-v1:0',
    name: 'Claude Opus 4.5',
    category: 'bueno',
    description: 'Máxima calidad para producción avanzada',
    cost: '$15/$75 por 1M tokens'
  }
];

export default function Admin({ tenantId, setTenantId }: AdminProps) {
  const [tempId, setTempId] = useState(tenantId);
  // Valor por defecto: Claude 3 Haiku (económico)
  const defaultModel = 'anthropic.claude-3-haiku-20240307-v1:0';
  const [currentModel, setCurrentModel] = useState<string>(defaultModel);
  const [selectedModel, setSelectedModel] = useState<string>(defaultModel);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadCurrentModel();
  }, [tenantId]);

  const loadCurrentModel = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/model?tenant_id=${tenantId}`);
      if (response.ok) {
        const data = await response.json();
        const modelId = data.model_id || defaultModel;
        setCurrentModel(modelId);
        setSelectedModel(modelId);
      } else {
        // Si falla, usar el modelo por defecto
        setCurrentModel(defaultModel);
        setSelectedModel(defaultModel);
      }
    } catch (error) {
      console.error('Error loading model:', error);
      // Si hay error, usar el modelo por defecto
      setCurrentModel(defaultModel);
      setSelectedModel(defaultModel);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveTenant = () => {
    setTenantId(tempId);
    alert(`Tenant ID switched to: ${tempId}`);
    loadCurrentModel();
  };

  const handleSaveModel = async () => {
    if (!selectedModel) {
      setMessage({ type: 'error', text: 'Por favor selecciona un modelo' });
      return;
    }

    setIsSaving(true);
    setMessage(null);
    
    try {
      const response = await fetch('/api/model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tenant_id: tenantId,
          model_id: selectedModel,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentModel(data.model_id);
        setMessage({ type: 'success', text: 'Modelo actualizado correctamente' });
      } else {
        const error = await response.json();
        setMessage({ type: 'error', text: error.error || 'Error al actualizar modelo' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Error al actualizar modelo' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="p-8 space-y-8 animate-fadeIn">
      <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg border border-gray-200 dark:border-gray-700">
        <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-white flex items-center gap-3">
          <span className="text-3xl">⚙️</span> Configuración del Agente
        </h2>

        <div className="space-y-6 max-w-xl">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Tenant ID (Identificador del Cliente)
            </label>
            <div className="flex gap-3">
              <input
                type="text"
                value={tempId}
                onChange={(e) => setTempId(e.target.value)}
                className="flex-1 p-3 border border-gray-300 dark:border-gray-600 rounded-xl dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none"
                placeholder="default"
              />
              <button
                onClick={handleSaveTenant}
                className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium"
              >
                Guardar
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Cambiar el Tenant ID cargará la configuración específica (personalidad, tono, modelos) definida en el backend.
            </p>
          </div>

          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Modelo LLM</h3>
            
            <div className="space-y-4">
              {isLoading && (
                <div className="text-center py-2">
                  <p className="text-sm text-gray-500">Cargando modelo actual...</p>
                </div>
              )}
              <div className="grid grid-cols-1 gap-3">
                {MODELS.map((model) => {
                    const isSelected = selectedModel === model.id;
                    const isCurrent = currentModel === model.id;
                    const categoryColors = {
                      economico: 'border-green-500 bg-green-50 dark:bg-green-900/20',
                      moderado: 'border-blue-500 bg-blue-50 dark:bg-blue-900/20',
                      bueno: 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                    };
                    
                    return (
                      <label
                        key={model.id}
                        className={`p-4 border-2 rounded-xl cursor-pointer transition-all ${
                          isSelected
                            ? `${categoryColors[model.category]} border-opacity-100`
                            : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <input
                            type="radio"
                            name="model"
                            value={model.id}
                            checked={isSelected}
                            onChange={(e) => setSelectedModel(e.target.value)}
                            className="mt-1"
                          />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold text-gray-900 dark:text-white">
                                {model.name}
                              </span>
                              {isCurrent && (
                                <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-full">
                                  Actual
                                </span>
                              )}
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                model.category === 'economico' ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300' :
                                model.category === 'moderado' ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300' :
                                'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300'
                              }`}>
                                {model.category === 'economico' ? '💰 Económico' :
                                 model.category === 'moderado' ? '⚖️ Moderado' :
                                 '✨ Bueno'}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                              {model.description}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-500">
                              {model.cost}
                            </p>
                          </div>
                        </div>
                      </label>
                    );
                  })}
              </div>
              
              {message && (
                <div className={`p-3 rounded-lg ${
                  message.type === 'success'
                    ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300'
                    : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
                }`}>
                  {message.text}
                </div>
              )}
              
              <button
                onClick={handleSaveModel}
                disabled={isSaving || selectedModel === currentModel || !selectedModel}
                className="w-full px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? 'Guardando...' : 'Guardar Modelo'}
              </button>
            </div>
          </div>

          <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Integraciones Activas</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl flex items-center gap-3">
                <span className="text-2xl">🌐</span>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Web Chat</p>
                  <p className="text-xs text-green-600 dark:text-green-400">● Activo</p>
                </div>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl flex items-center gap-3 opacity-60">
                <span className="text-2xl">💬</span>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">WhatsApp</p>
                  <p className="text-xs text-gray-500">○ No configurado</p>
                </div>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl flex items-center gap-3 opacity-60">
                <span className="text-2xl">📸</span>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Instagram</p>
                  <p className="text-xs text-gray-500">○ No configurado</p>
                </div>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl flex items-center gap-3 opacity-60">
                <span className="text-2xl">👥</span>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Teams</p>
                  <p className="text-xs text-gray-500">○ No configurado</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

