import { useEffect, useState } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, ShoppingCart } from 'lucide-react';
import { useDateRange } from '../App';

const Dashboard = () => {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { dateRange } = useDateRange();

  useEffect(() => {
    fetchKpis();
  }, [dateRange]);

  const fetchKpis = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/api/kpis?start_date=${dateRange.start}&end_date=${dateRange.end}`
      );
      if (!response.ok) throw new Error('Failed to fetch KPIs');
      const data = await response.json();
      setKpis(data.data || {});
      setError(null);
    } catch (err) {
      setError(err.message);
      setKpis({ metrics: {}, daily_kpis: [] });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading dashboard...</div>;
  }

  const metrics = kpis?.metrics || {};
  const dailyKpis = Array.isArray(kpis?.daily_kpis) ? kpis.daily_kpis : [];

  const KPICard = ({ label, value, icon: Icon, color = 'blue', delay = 0 }) => {
    const colorConfig = {
      blue: {
        gradient: 'from-blue-50 via-cyan-50 to-blue-50 hover:from-blue-100 hover:via-cyan-100 hover:to-blue-100',
        border: 'border-blue-300/60 hover:border-blue-500',
        icon: 'text-blue-600',
        shadow: 'shadow-blue-200/50 hover:shadow-blue-400/60',
        accent: 'bg-gradient-to-br from-blue-600 to-cyan-600'
      },
      green: {
        gradient: 'from-green-50 via-emerald-50 to-green-50 hover:from-green-100 hover:via-emerald-100 hover:to-green-100',
        border: 'border-green-300/60 hover:border-green-500',
        icon: 'text-green-600',
        shadow: 'shadow-green-200/50 hover:shadow-green-400/60',
        accent: 'bg-gradient-to-br from-green-600 to-emerald-600'
      },
      purple: {
        gradient: 'from-purple-50 via-pink-50 to-purple-50 hover:from-purple-100 hover:via-pink-100 hover:to-purple-100',
        border: 'border-purple-300/60 hover:border-purple-500',
        icon: 'text-purple-600',
        shadow: 'shadow-purple-200/50 hover:shadow-purple-400/60',
        accent: 'bg-gradient-to-br from-purple-600 to-pink-600'
      },
      orange: {
        gradient: 'from-orange-50 via-amber-50 to-orange-50 hover:from-orange-100 hover:via-amber-100 hover:to-orange-100',
        border: 'border-orange-300/60 hover:border-orange-500',
        icon: 'text-orange-600',
        shadow: 'shadow-orange-200/50 hover:shadow-orange-400/60',
        accent: 'bg-gradient-to-br from-orange-600 to-amber-600'
      },
    };

    const config = colorConfig[color];

    return (
      <div
        className={`bg-gradient-to-br ${config.gradient} p-8 rounded-2xl shadow-xl ${config.shadow} border-2 ${config.border} transition-all duration-500 transform hover:scale-110 hover:-translate-y-4 cursor-pointer group relative overflow-hidden backdrop-blur-sm`}
        style={{ animation: `fadeInUp 0.6s ease-out ${delay}s both` }}
      >
        {/* Animated background elements */}
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <div className={`absolute top-0 right-0 w-32 h-32 ${config.accent} rounded-full filter blur-3xl opacity-20 group-hover:opacity-40 transition-opacity`}></div>
        </div>

        {/* Shiny effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-30 animate-shimmer"></div>

        <div className="flex items-center justify-between relative z-10">
          <div>
            <p className="text-gray-600 text-sm font-semibold group-hover:text-gray-800 transition-colors">{label}</p>
            <p className="text-4xl font-black mt-4 text-gray-900 group-hover:text-gray-800 transition-colors bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent group-hover:from-gray-800 group-hover:to-gray-600">
              {value || 'N/A'}
            </p>
          </div>
          <div className={`w-16 h-16 rounded-xl ${config.accent} flex items-center justify-center opacity-90 group-hover:opacity-100 transform group-hover:scale-150 group-hover:rotate-12 transition-all duration-500 shadow-lg`}>
            <Icon className={`w-8 h-8 text-white drop-shadow-lg group-hover:drop-shadow-xl`} />
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-purple-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-4000"></div>
      </div>

      <div className="relative z-10">
        <div className="mb-12 group">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-blue-600 to-cyan-600 rounded-full"></div>
            <h1 className="text-5xl font-black bg-gradient-to-r from-blue-700 via-cyan-600 to-blue-800 bg-clip-text text-transparent group-hover:from-blue-800 group-hover:via-cyan-700 group-hover:to-blue-900 transition-all duration-300">
              Executive Dashboard
            </h1>
          </div>
          <p className="text-gray-600 mt-3 group-hover:text-gray-800 transition-colors text-lg font-medium ml-4">📊 Overview of key business metrics and performance indicators</p>
        </div>

        {error && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 p-5 rounded-2xl text-red-700 mb-8 border-2 border-red-300/60 animate-in shake duration-500 font-semibold flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
          <KPICard
            label="Total Revenue"
            value={`₹${(metrics.total_revenue || 0).toFixed(2)}`}
            icon={DollarSign}
            color="blue"
            delay={0}
          />
          <KPICard
            label="Total Orders"
            value={(metrics.total_orders || 0).toLocaleString()}
            icon={ShoppingCart}
            color="green"
            delay={0.1}
          />
          <KPICard
            label="Total Units"
            value={(metrics.total_units || 0).toLocaleString()}
            icon={TrendingUp}
            color="purple"
            delay={0.2}
          />
          <KPICard
            label="Profit Margin"
            value={`${(metrics.profit_margin || 0).toFixed(2)}%`}
            icon={TrendingUp}
            color="orange"
            delay={0.3}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {dailyKpis.length > 0 ? (
            <>
              <div className="bg-gradient-to-br from-white via-blue-50/30 to-white rounded-3xl shadow-2xl shadow-blue-300/30 hover:shadow-3xl hover:shadow-blue-400/40 border-2 border-blue-200/50 p-8 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 backdrop-blur-sm group"
                style={{ animation: 'fadeInUp 0.8s ease-out 0.2s both' }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-1 h-6 bg-gradient-to-b from-blue-600 to-cyan-600 rounded-full"></div>
                  <h2 className="text-xl font-bold bg-gradient-to-r from-blue-700 to-cyan-700 bg-clip-text text-transparent">📈 Daily Sales Trend</h2>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dailyKpis}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="date" stroke="#6b7280" />
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
                    <Line
                      type="monotone"
                      dataKey="net_sales"
                      stroke="url(#colorGradient)"
                      strokeWidth={4}
                      dot={{ fill: '#3b82f6', r: 6 }}
                      activeDot={{ r: 9, shadow: '0 0 20px rgba(59, 130, 246, 0.5)' }}
                      filter="drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3))"
                    />
                    <defs>
                      <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-gradient-to-br from-white via-green-50/30 to-white rounded-3xl shadow-2xl shadow-green-300/30 hover:shadow-3xl hover:shadow-green-400/40 border-2 border-green-200/50 p-8 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 backdrop-blur-sm group"
                style={{ animation: 'fadeInUp 0.8s ease-out 0.4s both' }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-1 h-6 bg-gradient-to-b from-green-600 to-emerald-600 rounded-full"></div>
                  <h2 className="text-xl font-bold bg-gradient-to-r from-green-700 to-emerald-700 bg-clip-text text-transparent">📊 Daily Orders</h2>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={dailyKpis}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="date" stroke="#6b7280" />
                    <YAxis stroke="#6b7280" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '2px solid #10b981',
                        borderRadius: '12px',
                        boxShadow: '0 20px 25px -5px rgba(16, 185, 129, 0.3)',
                        backdropFilter: 'blur(10px)'
                      }}
                      labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                    />
                    <Legend />
                    <Bar
                      dataKey="orders"
                      fill="url(#colorBarGradient)"
                      radius={[12, 12, 0, 0]}
                      filter="drop-shadow(0 4px 8px rgba(16, 185, 129, 0.25))"
                    />
                    <defs>
                      <linearGradient id="colorBarGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#10b981" stopOpacity={0.8}/>
                        <stop offset="100%" stopColor="#059669" stopOpacity={0.5}/>
                      </linearGradient>
                    </defs>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </>
          ) : (
            <div className="col-span-2 bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100 p-12 rounded-3xl shadow-xl border-2 border-gray-200/60 text-center text-gray-600 hover:shadow-2xl transition-all duration-300 group"
              style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
            >
              <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">📭</div>
              <p className="text-xl font-bold text-gray-700 group-hover:text-gray-800">No chart data available</p>
              <p className="text-sm text-gray-600 mt-2">Data will appear once your analytics are processed</p>
            </div>
          )}
        </div>
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
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
};

export default Dashboard;
