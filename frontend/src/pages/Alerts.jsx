import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, TrendingDown } from 'lucide-react';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/alerts');
      if (!response.ok) throw new Error('Failed to fetch alerts');
      const data = await response.json();
      setAlerts(Array.isArray(data.data) ? data.data : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading alerts...</div>;

  const getAlertIcon = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <CheckCircle className="w-5 h-5 text-blue-500" />;
    }
  };

  const getAlertColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-red-50 border-l-4 border-red-500';
      case 'warning':
        return 'bg-yellow-50 border-l-4 border-yellow-500';
      default:
        return 'bg-blue-50 border-l-4 border-blue-500';
    }
  };

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-80 h-80 bg-red-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 right-10 w-80 h-80 bg-orange-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10">
        <div className="mb-12 group">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-red-600 to-orange-600 rounded-full"></div>
            <h1 className="text-5xl font-black bg-gradient-to-r from-red-700 via-orange-600 to-red-800 bg-clip-text text-transparent group-hover:from-red-800 group-hover:via-orange-700 group-hover:to-red-900 transition-all duration-300">
              Alerts & Opportunities
            </h1>
          </div>
          <p className="text-gray-600 mt-3 group-hover:text-gray-800 transition-colors text-lg font-medium ml-4">⚡ Critical alerts and important action items</p>
        </div>

        {error && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-2xl text-red-700 mb-8 border-2 border-red-300/60 animate-in shake duration-500 font-semibold flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="space-y-5">
          {alerts.length > 0 ? (
            alerts.map((alert, i) => {
              const severityColors = {
                'critical': {
                  bg: 'from-red-50 via-orange-50 to-red-50',
                  border: 'border-red-400/80 hover:border-red-500',
                  accent: 'bg-red-600'
                },
                'warning': {
                  bg: 'from-yellow-50 via-amber-50 to-yellow-50',
                  border: 'border-yellow-400/80 hover:border-yellow-500',
                  accent: 'bg-yellow-600'
                },
                default: {
                  bg: 'from-blue-50 via-cyan-50 to-blue-50',
                  border: 'border-blue-400/80 hover:border-blue-500',
                  accent: 'bg-blue-600'
                }
              };

              const colors = severityColors[alert.severity?.toLowerCase()] || severityColors.default;

              return (
                <div
                  key={i}
                  className={`p-6 rounded-2xl flex items-start gap-4 border-l-4 border-t-2 bg-gradient-to-br ${colors.bg} hover:shadow-2xl hover:shadow-red-300/40 transition-all duration-400 transform hover:scale-105 hover:-translate-x-2 cursor-pointer group relative overflow-hidden backdrop-blur-sm ${colors.border}`}
                  style={{
                    animation: `slideInRight ${0.4 + i * 0.1}s cubic-bezier(0.34, 1.56, 0.64, 1) both`
                  }}
                >
                  {/* Animated background glow */}
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 animate-shimmer"></div>

                  <div className="flex-shrink-0 mt-1 transform group-hover:scale-150 group-hover:rotate-12 transition-all duration-400 relative z-10">
                    <div className={`${colors.accent} rounded-lg p-2 text-white`}>
                      {getAlertIcon(alert.severity)}
                    </div>
                  </div>
                  <div className="flex-1 relative z-10">
                    <h3 className="font-bold text-lg text-gray-900 group-hover:text-gray-800 transition-colors">
                      {alert.alert_type || 'Alert'}
                    </h3>
                    <p className="text-sm text-gray-700 mt-3 group-hover:text-gray-800 transition-colors leading-relaxed">
                      {alert.message || alert.description || 'No details available'}
                    </p>
                    {alert.entity && (
                      <p className="text-xs text-gray-600 mt-3 group-hover:text-gray-700 transition-colors font-semibold">
                        <span className="opacity-60">Entity:</span> <span className="text-blue-600 font-bold">{alert.entity}</span>
                      </p>
                    )}
                  </div>
                  <div className="text-xs text-gray-600 flex-shrink-0 group-hover:text-gray-800 transition-colors font-bold bg-white/60 px-3 py-2 rounded-lg backdrop-blur-sm relative z-10">
                    {alert.created_at ? new Date(alert.created_at).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="bg-gradient-to-br from-green-50 via-emerald-50 to-green-50 p-12 rounded-3xl shadow-2xl shadow-green-300/30 border-2 border-green-300/60 text-center text-green-700 hover:shadow-3xl hover:shadow-green-400/40 transition-all duration-500 group relative overflow-hidden backdrop-blur-sm"
              style={{ animation: 'fadeInUp 0.6s ease-out' }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-green-400/5 to-emerald-400/5 opacity-0 group-hover:opacity-100 rounded-3xl"></div>
              <div className="text-7xl mb-5 group-hover:scale-125 group-hover:-rotate-12 transition-all duration-500">✨</div>
              <p className="font-black text-2xl text-green-800 group-hover:text-green-900">No alerts at this time</p>
              <p className="text-sm mt-4 opacity-80 text-green-700">Everything looks great! All systems operating normally.</p>
              <div className="mt-6 flex justify-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse"></span>
                <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse animation-delay-200"></span>
                <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse animation-delay-400"></span>
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(-40px) rotateY(10deg);
          }
          to {
            opacity: 1;
            transform: translateX(0) rotateY(0);
          }
        }
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-200 {
          animation-delay: 0.2s;
        }
        .animation-delay-400 {
          animation-delay: 0.4s;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
      `}</style>
    </div>
  );
};

export default Alerts;
