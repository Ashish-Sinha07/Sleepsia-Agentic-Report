import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Advertising = () => {
  const [summary, setSummary] = useState(null);
  const [adData, setAdData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAdData();
  }, []);

  const fetchAdData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/advertising?start_date=2026-07-25&end_date=2026-08-24');
      if (!response.ok) throw new Error('Failed to fetch advertising data');
      const data = await response.json();
      setSummary(data.summary || null);
      setAdData(Array.isArray(data.platforms) ? data.platforms : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setSummary(null);
      setAdData([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading advertising data...</div>;

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-80 h-80 bg-indigo-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 right-20 w-80 h-80 bg-blue-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="mb-12 group">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-indigo-600 to-blue-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-indigo-700 via-blue-600 to-indigo-800 bg-clip-text text-transparent group-hover:from-indigo-800 group-hover:via-blue-700 group-hover:to-indigo-900 transition-all duration-300">
              Advertising Analysis
            </h1>
          </div>
          <p className="text-gray-600 mt-3 group-hover:text-gray-800 transition-colors text-sm ml-4">📢 Ad spend and ROI analysis</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-2xl text-red-700 mb-8 border-2 border-red-300/60 animate-in shake duration-500 font-semibold flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[
              { label: 'Impressions', value: (summary.impressions || 0).toLocaleString(), icon: '👁️', color: 'from-blue-50 via-cyan-50 to-blue-50' },
              { label: `Clicks (CTR ${(summary.ctr_pct || 0).toFixed(2)}%)`, value: (summary.clicks || 0).toLocaleString(), icon: '🖱️', color: 'from-purple-50 via-pink-50 to-purple-50' },
              { label: 'Attributed Orders', value: (summary.orders || 0).toLocaleString(), icon: '📦', color: 'from-green-50 via-emerald-50 to-green-50' },
              { label: 'ACOS', value: `${(summary.acos_pct || 0).toFixed(2)}%`, icon: '📊', color: 'from-orange-50 via-amber-50 to-orange-50' }
            ].map((card, i) => (
              <div
                key={i}
                className={`bg-gradient-to-br ${card.color} p-6 rounded-2xl border-2 border-gray-200/60 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 hover:-translate-y-2 group`}
                style={{ animation: `fadeInUp 0.6s ease-out ${0.1 * i}s both` }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-gray-600 text-xs font-semibold">{card.label}</p>
                    <p className="text-2xl font-black text-gray-900 mt-3">{card.value}</p>
                  </div>
                  <div className="text-3xl group-hover:scale-125 transition-transform">{card.icon}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {adData.length > 0 ? (
          <div className="space-y-8">
            {/* Chart Section */}
            <div className="bg-gradient-to-br from-white via-indigo-50/30 to-white rounded-3xl shadow-2xl shadow-indigo-300/30 hover:shadow-3xl hover:shadow-indigo-400/40 border-2 border-indigo-200/50 p-8 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 backdrop-blur-sm group"
              style={{ animation: 'fadeInUp 0.8s ease-out 0.2s both' }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-1 h-6 bg-gradient-to-b from-indigo-600 to-blue-600 rounded-full"></div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-indigo-700 to-blue-700 bg-clip-text text-transparent">💰 Ad Spend by Platform</h2>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={adData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="platform_name" stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '2px solid #4f46e5',
                      borderRadius: '12px',
                      boxShadow: '0 20px 25px -5px rgba(79, 70, 229, 0.3)',
                      backdropFilter: 'blur(10px)'
                    }}
                    labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                  />
                  <Legend />
                  <Bar dataKey="ad_spend" fill="url(#adGradient)" radius={[12, 12, 0, 0]} />
                  <defs>
                    <linearGradient id="adGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#4f46e5" stopOpacity={0.8}/>
                      <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.5}/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Ad Metrics Table */}
            <div className="bg-gradient-to-br from-white via-blue-50/30 to-white rounded-3xl shadow-2xl shadow-blue-300/30 hover:shadow-3xl hover:shadow-blue-400/40 border-2 border-blue-200/50 p-8 transition-all duration-500 backdrop-blur-sm group"
              style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-1 h-6 bg-gradient-to-b from-blue-600 to-cyan-600 rounded-full"></div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-blue-700 to-cyan-700 bg-clip-text text-transparent">📊 Ad Metrics</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-blue-300/60">
                      <th className="text-left p-4 font-bold text-gray-900">Platform</th>
                      <th className="text-right p-4 font-bold text-gray-900">Ad Spend</th>
                      <th className="text-right p-4 font-bold text-gray-900">Ad Sales</th>
                      <th className="text-right p-4 font-bold text-gray-900">ROAS</th>
                      <th className="text-right p-4 font-bold text-gray-900">ACOS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {adData.map((ad, i) => (
                      <tr
                        key={i}
                        className="border-b border-blue-200/60 hover:bg-gradient-to-r hover:from-blue-100/50 hover:via-cyan-100/50 hover:to-blue-100/50 transition-all duration-300 group"
                        style={{
                          animation: `slideInRight ${0.4 + i * 0.08}s cubic-bezier(0.34, 1.56, 0.64, 1) both`
                        }}
                      >
                        <td className="p-4 font-semibold text-gray-900">{ad.platform_name}</td>
                        <td className="text-right p-4 font-bold text-indigo-700">₹{(ad.ad_spend || 0).toFixed(2)}</td>
                        <td className="text-right p-4 font-bold text-blue-700">₹{(ad.attributed_sales || 0).toFixed(2)}</td>
                        <td className="text-right p-4 font-bold text-green-700">{(ad.roas || 0).toFixed(2)}x</td>
                        <td className="text-right p-4 font-bold text-red-700">{(ad.acos_pct || 0).toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100 p-12 rounded-3xl shadow-xl border-2 border-gray-200/60 text-center text-gray-600 hover:shadow-2xl transition-all duration-300 group"
            style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
          >
            <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">📭</div>
            <p className="text-xl font-bold text-gray-700 group-hover:text-gray-800">No advertising data available</p>
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
      `}</style>
    </div>
  );
};

export default Advertising;
