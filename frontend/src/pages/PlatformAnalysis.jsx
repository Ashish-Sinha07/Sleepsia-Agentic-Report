import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { TrendingUp } from 'lucide-react';

const PlatformAnalysis = () => {
  const [platforms, setPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dateRange, setDateRange] = useState({ start: '2026-07-25', end: '2026-08-24' });

  useEffect(() => {
    fetchPlatforms();
  }, [dateRange]);

  const fetchPlatforms = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/api/platforms?start_date=${dateRange.start}&end_date=${dateRange.end}`
      );
      if (!response.ok) throw new Error('Failed to fetch platform data');
      const data = await response.json();
      setPlatforms(Array.isArray(data.data) ? data.data : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setPlatforms([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading platform analysis...</div>;

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 left-10 w-80 h-80 bg-pink-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="mb-12 group">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-purple-600 to-pink-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-purple-700 via-pink-600 to-purple-800 bg-clip-text text-transparent group-hover:from-purple-800 group-hover:via-pink-700 group-hover:to-purple-900 transition-all duration-300">
              Platform Analysis
            </h1>
          </div>
          <p className="text-gray-600 mt-3 group-hover:text-gray-800 transition-colors text-sm ml-4">📊 Performance by e-commerce platform</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-2xl text-red-700 mb-8 border-2 border-red-300/60 animate-in shake duration-500 font-semibold flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {platforms.length > 0 ? (
          <div className="space-y-8">
            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Sales Chart */}
              <div className="bg-gradient-to-br from-white via-purple-50/30 to-white rounded-3xl shadow-2xl shadow-purple-300/30 hover:shadow-3xl hover:shadow-purple-400/40 border-2 border-purple-200/50 p-8 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 backdrop-blur-sm group"
                style={{ animation: 'fadeInUp 0.8s ease-out 0.2s both' }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-1 h-6 bg-gradient-to-b from-purple-600 to-pink-600 rounded-full"></div>
                  <h2 className="text-lg font-bold bg-gradient-to-r from-purple-700 to-pink-700 bg-clip-text text-transparent">📈 Sales by Platform</h2>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={platforms}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="platform_name" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '2px solid #a855f7',
                        borderRadius: '12px',
                        boxShadow: '0 20px 25px -5px rgba(168, 85, 247, 0.3)',
                        backdropFilter: 'blur(10px)'
                      }}
                      labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                    />
                    <Legend />
                    <Bar dataKey="total_sales" fill="url(#platformGradient)" radius={[12, 12, 0, 0]} />
                    <defs>
                      <linearGradient id="platformGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#a855f7" stopOpacity={0.8}/>
                        <stop offset="100%" stopColor="#ec4899" stopOpacity={0.5}/>
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Orders Chart */}
              <div className="bg-gradient-to-br from-white via-blue-50/30 to-white rounded-3xl shadow-2xl shadow-blue-300/30 hover:shadow-3xl hover:shadow-blue-400/40 border-2 border-blue-200/50 p-8 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 backdrop-blur-sm group"
                style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-1 h-6 bg-gradient-to-b from-blue-600 to-cyan-600 rounded-full"></div>
                  <h2 className="text-lg font-bold bg-gradient-to-r from-blue-700 to-cyan-700 bg-clip-text text-transparent">📊 Orders by Platform</h2>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={platforms}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="platform_name" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '2px solid #3b82f6',
                        borderRadius: '12px',
                        boxShadow: '0 20px 25px -5px rgba(59, 130, 246, 0.3)',
                        backdropFilter: 'blur(10px)'
                      }}
                      labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                    />
                    <Legend />
                    <Bar dataKey="total_orders" fill="url(#orderGradient)" radius={[12, 12, 0, 0]} />
                    <defs>
                      <linearGradient id="orderGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.8}/>
                        <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.5}/>
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Metrics Cards */}
            <div className="bg-gradient-to-br from-white via-green-50/30 to-white rounded-3xl shadow-2xl shadow-green-300/30 hover:shadow-3xl hover:shadow-green-400/40 border-2 border-green-200/50 p-8 transition-all duration-500 backdrop-blur-sm group"
              style={{ animation: 'fadeInUp 0.8s ease-out 0.4s both' }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-1 h-6 bg-gradient-to-b from-green-600 to-emerald-600 rounded-full"></div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-green-700 to-emerald-700 bg-clip-text text-transparent">💰 Platform Metrics</h2>
              </div>
              <div className="space-y-4">
                {platforms.map((p, i) => (
                  <div
                    key={i}
                    className={`p-6 rounded-2xl border-l-4 bg-gradient-to-br from-emerald-50 via-green-50/50 to-emerald-50 border-l-green-600 hover:shadow-xl transition-all duration-300 transform hover:scale-105 group relative overflow-hidden backdrop-blur-sm`}
                    style={{
                      animation: `slideInRight ${0.4 + i * 0.1}s cubic-bezier(0.34, 1.56, 0.64, 1) both`
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 animate-shimmer"></div>
                    <div className="relative z-10">
                      <p className="font-bold text-gray-900 text-lg group-hover:text-gray-800">{p.platform_name}</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                        <div className="bg-white/70 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-gray-600 text-xs font-semibold">Orders</p>
                          <p className="font-bold text-green-700 text-lg mt-1">{p.total_orders || 0}</p>
                        </div>
                        <div className="bg-white/70 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-gray-600 text-xs font-semibold">Units</p>
                          <p className="font-bold text-green-700 text-lg mt-1">{p.total_units || 0}</p>
                        </div>
                        <div className="bg-white/70 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-gray-600 text-xs font-semibold">Revenue</p>
                          <p className="font-bold text-green-700 text-lg mt-1">₹{(p.total_sales || 0).toFixed(0)}</p>
                        </div>
                        <div className="bg-white/70 rounded-lg p-3 backdrop-blur-sm">
                          <p className="text-gray-600 text-xs font-semibold">Profit</p>
                          <p className="font-bold text-green-700 text-lg mt-1">₹{(p.profit || 0).toFixed(0)}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100 p-12 rounded-3xl shadow-xl border-2 border-gray-200/60 text-center text-gray-600 hover:shadow-2xl transition-all duration-300 group"
            style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
          >
            <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">📭</div>
            <p className="text-xl font-bold text-gray-700 group-hover:text-gray-800">No platform data available</p>
            <p className="text-sm text-gray-600 mt-2">Data will appear once your analytics are processed</p>
          </div>
        )}
      </div>

      <style>{`
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

export default PlatformAnalysis;
