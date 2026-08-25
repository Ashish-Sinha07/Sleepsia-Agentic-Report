import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

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
    <div className="p-6 bg-gray-50">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Advertising Analysis</h1>
      <p className="text-gray-600 mb-6">Ad spend and ROI analysis</p>

      {error && <div className="bg-red-50 p-4 rounded-lg text-red-700 mb-6">{error}</div>}

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Impressions</p>
            <p className="text-2xl font-bold text-gray-900">{(summary.impressions || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Clicks (CTR {(summary.ctr_pct || 0).toFixed(2)}%)</p>
            <p className="text-2xl font-bold text-gray-900">{(summary.clicks || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-gray-600 text-sm">Attributed orders</p>
            <p className="text-2xl font-bold text-gray-900">{(summary.orders || 0).toLocaleString()}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-gray-600 text-sm">ACOS</p>
            <p className="text-2xl font-bold text-gray-900">{(summary.acos_pct || 0).toFixed(2)}%</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6">
        {adData.length > 0 ? (
          <>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Ad Spend by Platform</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={adData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="platform_name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="ad_spend" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Ad Metrics</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left p-2">Platform</th>
                      <th className="text-right p-2">Ad Spend</th>
                      <th className="text-right p-2">Ad Sales</th>
                      <th className="text-right p-2">ROAS</th>
                      <th className="text-right p-2">ACOS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {adData.map((ad, i) => (
                      <tr key={i} className="border-b hover:bg-gray-50">
                        <td className="p-2">{ad.platform_name}</td>
                        <td className="text-right p-2">₹{(ad.ad_spend || 0).toFixed(2)}</td>
                        <td className="text-right p-2">₹{(ad.attributed_sales || 0).toFixed(2)}</td>
                        <td className="text-right p-2">{(ad.roas || 0).toFixed(2)}</td>
                        <td className="text-right p-2">{(ad.acos_pct || 0).toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow text-center text-gray-500">
            No advertising data available
          </div>
        )}
      </div>
    </div>
  );
};

export default Advertising;
