'use client';

import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface QueryLog {
  query: string;
  timestamp: string;
  tokens: number;
  responseTime: number;
  sources?: string[];
}

interface DailyStats {
  date: string;
  queries: number;
  tokens: number;
  avgResponseTime: number;
}

interface TopQuery {
  query: string;
  count: number;
  avgTokens: number;
}

const COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef'];

export default function Analytics() {
  const [queryLogs, setQueryLogs] = useState<QueryLog[]>([]);
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [topQueries, setTopQueries] = useState<TopQuery[]>([]);
  const [totalTokens, setTotalTokens] = useState(0);
  const [totalQueries, setTotalQueries] = useState(0);
  const [avgResponseTime, setAvgResponseTime] = useState(0);
  const [estimatedCost, setEstimatedCost] = useState(0);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = () => {
    // Cargar logs de queries desde localStorage
    const logs = localStorage.getItem('snail_query_logs');
    const parsedLogs: QueryLog[] = logs ? JSON.parse(logs) : [];
    setQueryLogs(parsedLogs);

    // Cargar total de tokens
    const tokens = localStorage.getItem('snail_total_tokens');
    const totalTokensUsed = tokens ? parseInt(tokens, 10) : 0;
    setTotalTokens(totalTokensUsed);

    // Calcular estadísticas
    if (parsedLogs.length > 0) {
      setTotalQueries(parsedLogs.length);

      // Calcular promedio de tiempo de respuesta
      const avgTime = parsedLogs.reduce((sum, log) => sum + log.responseTime, 0) / parsedLogs.length;
      setAvgResponseTime(avgTime);

      // Calcular estadísticas diarias
      const dailyStatsMap = new Map<string, { queries: number; tokens: number; responseTimes: number[] }>();

      parsedLogs.forEach(log => {
        const date = new Date(log.timestamp).toLocaleDateString('es-ES', {
          month: 'short',
          day: 'numeric'
        });

        if (!dailyStatsMap.has(date)) {
          dailyStatsMap.set(date, { queries: 0, tokens: 0, responseTimes: [] });
        }

        const stats = dailyStatsMap.get(date)!;
        stats.queries++;
        stats.tokens += log.tokens;
        stats.responseTimes.push(log.responseTime);
      });

      const dailyData: DailyStats[] = Array.from(dailyStatsMap.entries()).map(([date, stats]) => ({
        date,
        queries: stats.queries,
        tokens: stats.tokens,
        avgResponseTime: stats.responseTimes.reduce((a, b) => a + b, 0) / stats.responseTimes.length,
      }));

      setDailyStats(dailyData.slice(-7)); // Últimos 7 días

      // Calcular top queries
      const queryFrequency = new Map<string, { count: number; totalTokens: number }>();

      parsedLogs.forEach(log => {
        const normalizedQuery = log.query.toLowerCase().trim();
        if (!queryFrequency.has(normalizedQuery)) {
          queryFrequency.set(normalizedQuery, { count: 0, totalTokens: 0 });
        }
        const freq = queryFrequency.get(normalizedQuery)!;
        freq.count++;
        freq.totalTokens += log.tokens;
      });

      const topQueriesData: TopQuery[] = Array.from(queryFrequency.entries())
        .map(([query, { count, totalTokens }]) => ({
          query: query.substring(0, 50) + (query.length > 50 ? '...' : ''),
          count,
          avgTokens: Math.round(totalTokens / count),
        }))
        .sort((a, b) => b.count - a.count)
        .slice(0, 5);

      setTopQueries(topQueriesData);

      // Calcular costo estimado (Claude Haiku: $0.25 por 1M input tokens, $1.25 por 1M output tokens)
      // Asumimos 60% input, 40% output
      const inputTokens = totalTokensUsed * 0.6;
      const outputTokens = totalTokensUsed * 0.4;
      const cost = (inputTokens / 1000000 * 0.25) + (outputTokens / 1000000 * 1.25);
      setEstimatedCost(cost);
    }
  };

  const clearAnalytics = () => {
    if (confirm('¿Estás seguro de que quieres limpiar todos los datos de analytics?')) {
      localStorage.removeItem('snail_query_logs');
      localStorage.removeItem('snail_total_tokens');
      loadAnalytics();
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            📊 Analytics Dashboard
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            Estadísticas de uso y rendimiento del asistente AI
          </p>
        </div>
        <button
          onClick={clearAnalytics}
          className="px-4 py-2 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-900/50 transition-colors text-sm font-medium"
        >
          🗑️ Limpiar datos
        </button>
      </div>

      {queryLogs.length === 0 ? (
        <div className="text-center py-20 text-gray-500 dark:text-gray-400">
          <div className="text-6xl mb-4">📊</div>
          <p className="text-xl font-semibold">No hay datos de analytics aún</p>
          <p className="text-sm mt-2">Comienza a usar el chat para ver estadísticas aquí</p>
        </div>
      ) : (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total Queries */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border-2 border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-blue-600 dark:text-blue-400">Total Consultas</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{totalQueries}</p>
                </div>
                <div className="text-4xl">💬</div>
              </div>
            </div>

            {/* Total Tokens */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6 border-2 border-purple-200 dark:border-purple-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-purple-600 dark:text-purple-400">Total Tokens</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{totalTokens.toLocaleString()}</p>
                </div>
                <div className="text-4xl">💰</div>
              </div>
            </div>

            {/* Avg Response Time */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-xl p-6 border-2 border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-green-600 dark:text-green-400">Tiempo Promedio</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">{avgResponseTime.toFixed(1)}s</p>
                </div>
                <div className="text-4xl">⚡</div>
              </div>
            </div>

            {/* Estimated Cost */}
            <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 rounded-xl p-6 border-2 border-orange-200 dark:border-orange-800">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-orange-600 dark:text-orange-400">Costo Estimado</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">${estimatedCost.toFixed(4)}</p>
                </div>
                <div className="text-4xl">💵</div>
              </div>
            </div>
          </div>

          {/* Charts Row 1 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Token Usage Over Time */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📈 Uso de Tokens por Día
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="tokens"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    name="Tokens"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Queries Per Day */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                📊 Consultas por Día
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="queries" fill="#6366f1" name="Consultas" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Charts Row 2 */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Response Time Trend */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                ⚡ Tiempo de Respuesta Promedio
              </h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyStats}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="date" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#1f2937',
                      border: '1px solid #374151',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="avgResponseTime"
                    stroke="#10b981"
                    strokeWidth={2}
                    name="Tiempo Promedio (s)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Top Queries */}
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                🔥 Consultas Más Frecuentes
              </h3>
              <div className="space-y-3">
                {topQueries.map((item, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                        <span className="text-white font-bold text-sm">#{index + 1}</span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {item.query}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {item.avgTokens} tokens promedio
                        </p>
                      </div>
                    </div>
                    <div className="flex-shrink-0 ml-4">
                      <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-bold">
                        {item.count}x
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Cost Breakdown */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border-2 border-blue-200 dark:border-blue-800">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              💵 Desglose de Costos (Claude Haiku)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Input Tokens (60%)</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(totalTokens * 0.6).toLocaleString()}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  ${((totalTokens * 0.6) / 1000000 * 0.25).toFixed(4)}
                </p>
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Output Tokens (40%)</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {Math.round(totalTokens * 0.4).toLocaleString()}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  ${((totalTokens * 0.4) / 1000000 * 1.25).toFixed(4)}
                </p>
              </div>
              <div className="bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-900/30 dark:to-emerald-900/30 rounded-lg p-4 border-2 border-green-300 dark:border-green-700">
                <p className="text-sm text-green-700 dark:text-green-400 font-semibold">Costo Total Estimado</p>
                <p className="text-3xl font-bold text-green-900 dark:text-green-300">
                  ${estimatedCost.toFixed(4)}
                </p>
                <p className="text-xs text-green-600 dark:text-green-500 mt-1">
                  ~${(estimatedCost * 30).toFixed(2)}/mes al ritmo actual
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
