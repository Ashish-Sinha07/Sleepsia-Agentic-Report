import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

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
    <div className="p-6 bg-gray-50">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Platform Analysis</h1>
      <p className="text-gray-600 mb-6">Performance by e-commerce platform</p>

      {error && <div className="bg-red-50 p-4 rounded-lg text-red-700 mb-6">{error}</div>}

      {platforms.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Sales by Platform</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={platforms}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="platform_name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="total_sales" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-lg font-semibold mb-4">Platform Metrics</h2>
            <div className="space-y-4">
              {platforms.map((p, i) => (
                <div key={i} className="border-b pb-4">
                  <p className="font-semibold">{p.platform_name}</p>
                  <div className="grid grid-cols-2 gap-2 text-sm mt-2">
                    <p>Orders: {p.total_orders || 0}</p>
                    <p>Units: {p.total_units || 0}</p>
                    <p>Revenue: ₹{(p.total_sales || 0).toFixed(2)}</p>
                    <p>Profit: ₹{(p.profit || 0).toFixed(2)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow text-center text-gray-500">
          No platform data available
        </div>
      )}
    </div>
  );
};

export default PlatformAnalysis;
