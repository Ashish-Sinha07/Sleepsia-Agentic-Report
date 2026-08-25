import { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Fix marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png',
});

const Inventory = () => {
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const fetchWarehouses = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/warehouses');
      if (!response.ok) throw new Error('Failed to fetch warehouse data');
      const data = await response.json();
      setWarehouses(Array.isArray(data.data) ? data.data : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setWarehouses([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading inventory data...</div>;

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 right-1/4 w-80 h-80 bg-sky-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 -left-20 w-80 h-80 bg-cyan-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10">
        {/* Header */}
        <div className="mb-12 group">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-sky-600 to-cyan-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-sky-700 via-cyan-600 to-sky-800 bg-clip-text text-transparent group-hover:from-sky-800 group-hover:via-cyan-700 group-hover:to-sky-900 transition-all duration-300">
              Inventory & Warehouse
            </h1>
          </div>
          <p className="text-gray-600 mt-3 group-hover:text-gray-800 transition-colors text-sm ml-4">📦 Stock levels and warehouse status</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="bg-gradient-to-r from-red-50 to-orange-50 p-6 rounded-2xl text-red-700 mb-8 border-2 border-red-300/60 animate-in shake duration-500 font-semibold flex items-center gap-3">
            <span className="text-2xl">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {warehouses.length > 0 && (
          <div className="space-y-8">
            {/* Map and Status Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Warehouse Map */}
              <div className="lg:col-span-2 bg-gradient-to-br from-white via-sky-50/30 to-white rounded-3xl shadow-2xl shadow-sky-300/30 hover:shadow-3xl hover:shadow-sky-400/40 border-2 border-sky-200/50 p-8 transition-all duration-500 transform hover:scale-105 hover:-translate-y-2 backdrop-blur-sm group"
                style={{ animation: 'fadeInUp 0.8s ease-out 0.2s both' }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-1 h-6 bg-gradient-to-b from-sky-600 to-cyan-600 rounded-full"></div>
                  <h2 className="text-lg font-bold bg-gradient-to-r from-sky-700 to-cyan-700 bg-clip-text text-transparent">🗺️ Warehouse Map</h2>
                </div>
                {warehouses.length > 0 && warehouses[0].latitude ? (
                  <MapContainer
                    center={[warehouses[0].latitude, warehouses[0].longitude]}
                    zoom={5}
                    style={{ height: '400px', width: '100%', borderRadius: '16px' }}
                  >
                    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    {warehouses.map((wh, i) => (
                      <Marker
                        key={i}
                        position={[wh.latitude || 0, wh.longitude || 0]}
                      >
                        <Popup>
                          <div className="text-sm">
                            <p className="font-bold text-gray-900">{wh.warehouse_name}</p>
                            <p className="text-gray-700">📍 {wh.city}</p>
                            <p className="text-gray-700">📦 {wh.total_inventory || 0} units</p>
                            <p className="text-gray-700">📊 {wh.sku_count || 0} SKUs</p>
                          </div>
                        </Popup>
                      </Marker>
                    ))}
                  </MapContainer>
                ) : (
                  <div className="h-96 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center text-gray-500">
                    Map data not available
                  </div>
                )}
              </div>

              {/* Warehouse Status Cards */}
              <div className="space-y-4"
                style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
              >
                <h3 className="text-lg font-bold text-gray-900 mb-4">📍 Status Overview</h3>
                {warehouses.map((wh, i) => (
                  <div
                    key={i}
                    className="bg-gradient-to-br from-cyan-50 via-sky-50/50 to-cyan-50 p-4 rounded-2xl border-l-4 border-l-cyan-600 hover:shadow-xl transition-all duration-300 transform hover:scale-105 group relative overflow-hidden backdrop-blur-sm"
                    style={{
                      animation: `slideInRight ${0.4 + i * 0.1}s cubic-bezier(0.34, 1.56, 0.64, 1) both`
                    }}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 animate-shimmer"></div>
                    <div className="relative z-10">
                      <p className="font-bold text-gray-900 text-sm group-hover:text-gray-800">{wh.warehouse_name}</p>
                      <p className="text-xs text-gray-600 mt-1">{wh.city}</p>
                      <div className="mt-3 text-xs space-y-2 font-semibold">
                        <p className="text-cyan-700">📦 {wh.total_inventory || 0} units</p>
                        <p className="text-sky-700">📊 {wh.sku_count || 0} SKUs</p>
                        <p className="text-red-600">⚠️ {wh.low_stock_count || 0} Low</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Detailed Metrics Table */}
            <div className="bg-gradient-to-br from-white via-teal-50/30 to-white rounded-3xl shadow-2xl shadow-teal-300/30 hover:shadow-3xl hover:shadow-teal-400/40 border-2 border-teal-200/50 p-8 transition-all duration-500 backdrop-blur-sm group"
              style={{ animation: 'fadeInUp 0.8s ease-out 0.4s both' }}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-1 h-6 bg-gradient-to-b from-teal-600 to-cyan-600 rounded-full"></div>
                <h2 className="text-lg font-bold bg-gradient-to-r from-teal-700 to-cyan-700 bg-clip-text text-transparent">📊 Detailed Warehouse Metrics</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b-2 border-teal-300/60">
                      <th className="text-left p-4 font-bold text-gray-900">Warehouse</th>
                      <th className="text-left p-4 font-bold text-gray-900">City</th>
                      <th className="text-right p-4 font-bold text-gray-900">Inventory</th>
                      <th className="text-right p-4 font-bold text-gray-900">SKU Count</th>
                      <th className="text-right p-4 font-bold text-gray-900">Days of Cover</th>
                    </tr>
                  </thead>
                  <tbody>
                    {warehouses.map((wh, i) => (
                      <tr
                        key={i}
                        className="border-b border-teal-200/60 hover:bg-gradient-to-r hover:from-teal-100/50 hover:via-cyan-100/50 hover:to-teal-100/50 transition-all duration-300 group"
                        style={{
                          animation: `slideInRight ${0.4 + i * 0.08}s cubic-bezier(0.34, 1.56, 0.64, 1) both`
                        }}
                      >
                        <td className="p-4 font-semibold text-gray-900">{wh.warehouse_name}</td>
                        <td className="p-4 text-gray-800">{wh.city}</td>
                        <td className="text-right p-4 font-bold text-cyan-700">{wh.total_inventory || 0}</td>
                        <td className="text-right p-4 font-bold text-sky-700">{wh.sku_count || 0}</td>
                        <td className="text-right p-4 font-bold text-teal-700">{(wh.days_of_cover || 0).toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {warehouses.length === 0 && !error && (
          <div className="bg-gradient-to-br from-gray-50 via-slate-50 to-gray-100 p-12 rounded-3xl shadow-xl border-2 border-gray-200/60 text-center text-gray-600 hover:shadow-2xl transition-all duration-300 group"
            style={{ animation: 'fadeInUp 0.8s ease-out 0.3s both' }}
          >
            <div className="text-6xl mb-4 group-hover:scale-110 transition-transform">📭</div>
            <p className="text-xl font-bold text-gray-700 group-hover:text-gray-800">No warehouse data available</p>
            <p className="text-sm text-gray-600 mt-2">Warehouse inventory data will appear once loaded</p>
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

export default Inventory;
