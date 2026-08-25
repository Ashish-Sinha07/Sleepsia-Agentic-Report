import React, { useState, useEffect } from 'react';
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
    <div className="p-6 bg-gray-50">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Product Analysis</h1>
      <p className="text-gray-600 mb-6">Product-wise performance metrics</p>

      {error && <div className="bg-red-50 p-4 rounded-lg text-red-700 mb-6">{error}</div>}

      <div className="grid grid-cols-1 gap-6">
        {products.length > 0 ? (
          <>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Sales by Product</h2>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={products}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="product_name" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="total_sales" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Product Details</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b">
                    <tr>
                      <th className="text-left p-2">SKU</th>
                      <th className="text-left p-2">Product</th>
                      <th className="text-right p-2">Sales</th>
                      <th className="text-right p-2">Units</th>
                      <th className="text-right p-2">Profit Margin</th>
                    </tr>
                  </thead>
                  <tbody>
                    {products.map((p, i) => (
                      <tr key={i} className="border-b hover:bg-gray-50">
                        <td className="p-2">{p.sku}</td>
                        <td className="p-2">{p.product_name}</td>
                        <td className="text-right p-2">₹{(p.total_sales || 0).toFixed(2)}</td>
                        <td className="text-right p-2">{p.total_units || 0}</td>
                        <td className="text-right p-2">{(p.profit_margin || 0).toFixed(2)}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="bg-white p-6 rounded-lg shadow text-center text-gray-500">
            No product data available
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductAnalysis;
