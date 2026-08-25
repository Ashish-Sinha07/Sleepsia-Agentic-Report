import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Profitability = () => {
  const [profitData, setProfitData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProfitability();
  }, []);

  const fetchProfitability = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/platforms?start_date=2026-07-25&end_date=2026-08-24');
      if (!response.ok) throw new Error('Failed to fetch profitability data');
      const data = await response.json();
      setProfitData(Array.isArray(data.data) ? data.data : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setProfitData([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading profitability data...</div>;

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="p-6 bg-gray-50">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Profitability Analysis</h1>
      <p className="text-gray-600 mb-6">Profit margin and cost analysis</p>

      {error && <div className="bg-red-50 p-4 rounded-lg text-red-700 mb-6">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {Array.isArray(profitData) && profitData.length > 0 ? (
          <>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Profit by Platform</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={profitData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="platform_name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="profit" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Profit Distribution</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={profitData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.platform_name}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="profit"
                  >
                    {profitData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Profitability Metrics</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left p-2">Platform</th>
                      <th className="text-right p-2">Revenue</th>
                      <th className="text-right p-2">Costs</th>
                      <th className="text-right p-2">Profit</th>
                      <th className="text-right p-2">Margin %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {profitData.map((p, i) => (
                      <tr key={i} className="border-b hover:bg-gray-50">
                        <td className="p-2">{p.platform_name}</td>
                        <td className="text-right p-2">₹{(p.total_sales || 0).toFixed(2)}</td>
                        <td className="text-right p-2">₹{((p.total_sales || 0) - (p.profit || 0)).toFixed(2)}</td>
                        <td className="text-right p-2">₹{(p.profit || 0).toFixed(2)}</td>
                        <td className="text-right p-2">{((p.profit || 0) / (p.total_sales || 1) * 100).toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow text-center text-gray-500">
            No profitability data available
          </div>
        )}
      </div>
    </div>
  );
};

export default Profitability;
