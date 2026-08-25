import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ProductAnalysis = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/products?start_date=2026-07-25&end_date=2026-08-24');
      if (!response.ok) throw new Error('Failed to fetch products');
      const data = await response.json();
      setProducts(Array.isArray(data.data) ? data.data : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading product analysis...</div>;

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 left-1/2 w-80 h-80 bg-orange-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 -right-40 w-80 h-80 bg-yellow-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="mb-12 group">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-orange-600 to-amber-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-orange-700 via-amber-600 to-orange-800 bg-clip-text text-transparent group-hover:from-orange-800 group-hover:via-amber-700 group-hover:to-orange-900 transition-all duration-300">
              Product Analysis
            </h1>
          </div>
          <p className="text-gray-600 mt-3 group-hover:text-gray-800 transition-colors text-sm ml-4">📦 Product-wise performance metrics</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-2xl text-red-700 mb-8 border-2 border-red-300/60 animate-in shake duration-500 font-semibold flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {products.length > 0 ? (
          <div className="space-y-8">
            {/* Chart Section */}
            <div className="bg-gradient-to-br from-white via-orange-50/30 to-white rounded-3xl shadow-2xl shadow-orange-300/30 hover:shadow-3xl hover:shadow-orange-400/40 border-2 border-orange-200/50 p-8 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 backdrop-blur-sm group"
              style={{ animation: 'fadeInUp 0.8s ease-out 0.2s both' }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-1 h-6 bg-gradient-to-b from-orange-600 to-amber-600 rounded-full"></div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-orange-700 to-amber-700 bg-clip-text text-transparent">💰 Sales by Product</h2>
              </div>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={products}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="product_name" angle={-45} textAnchor="end" height={80} stroke="#6b7280" />
                  <YAxis stroke="#6b7280" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '2px solid #f59e0b',
                      borderRadius: '12px',
                      boxShadow: '0 20px 25px -5px rgba(245, 158, 11, 0.3)',
                      backdropFilter: 'blur(10px)'
                    }}
                    labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                  />
                  <Legend />
                  <Bar dataKey="total_sales" fill="url(#productGradient)" radius={[12, 12, 0, 0]} />
                  <defs>
                    <linearGradient id="productGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#f59e0b" stopOpacity={0.8}/>
                      <stop offset="100%" stopColor="#fbbf24" stopOpacity={0.5}/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Product Details Table */}
            <div className="bg-gradient-to-br from-white via-yellow-50/30 to-white rounded-3xl shadow-2xl shadow-yellow-300/30 hover:shadow-3xl hover:shadow-yellow-400/40 border-2 border-yellow-200/50 p-8 transition-all duration-500 backdrop-blur-sm group"
              style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-1 h-6 bg-gradient-to-b from-yellow-600 to-amber-600 rounded-full"></div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-yellow-700 to-amber-700 bg-clip-text text-transparent">📊 Product Details</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-yellow-300/60">
                      <th className="text-left p-4 font-bold text-gray-900">SKU</th>
                      <th className="text-left p-4 font-bold text-gray-900">Product</th>
                      <th className="text-right p-4 font-bold text-gray-900">Sales</th>
                      <th className="text-right p-4 font-bold text-gray-900">Units</th>
                      <th className="text-right p-4 font-bold text-gray-900">Profit Margin</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p, i) => (
                      <tr
                        key={i}
                        className="border-b border-yellow-200/60 hover:bg-gradient-to-r hover:from-yellow-100/50 hover:via-amber-100/50 hover:to-yellow-100/50 transition-all duration-300 group"
                        style={{
                          animation: `slideInRight ${0.4 + i * 0.08}s cubic-bezier(0.34, 1.56, 0.64, 1) both`
                        }}
                      >
                        <td className="p-4 font-semibold text-gray-900">{p.sku}</td>
                        <td className="p-4 text-gray-800">{p.product_name}</td>
                        <td className="text-right p-4 font-bold text-orange-700">₹{(p.total_sales || 0).toFixed(2)}</td>
                        <td className="text-right p-4 font-bold text-amber-700">{p.total_units || 0}</td>
                        <td className="text-right p-4 font-bold text-green-700">{(p.profit_margin || 0).toFixed(2)}%</td>
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
            <p className="text-xl font-bold text-gray-700 group-hover:text-gray-800">No product data available</p>
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

export default ProductAnalysis;
