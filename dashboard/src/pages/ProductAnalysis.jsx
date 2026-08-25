import { useContext, useEffect, useState } from 'react';
import { FilterContext } from '../context/FilterContext';
import { analyticsApi } from '../services/analyticsApi';
import FilterBar from '../components/filters/FilterBar';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import { formatCurrency, formatPercentage, formatROAS } from '../utils/formatting';

export default function ProductAnalysis() {
  const { filters } = useContext(FilterContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await analyticsApi.getProductPerformance(filters);
        setData(result);
      } catch (err) {
        setError(err.message || 'Failed to load product data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen p-0 -m-8 p-8">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-green-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 left-10 w-80 h-80 bg-emerald-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10 space-y-6">
        <div className="group mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-green-600 to-emerald-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-green-700 via-emerald-600 to-green-800 bg-clip-text text-transparent">
              Product Analysis
            </h1>
          </div>
          <p className="text-sm text-gray-700 font-medium ml-4">📦 Understand product-level performance across platforms</p>
        </div>

      <FilterBar />

      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-gray-900">Product Performance</h3>
        </div>
        <div className="card-body overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-900">SKU</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Product</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Platform</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Revenue</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Profit</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Margin</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">ROAS</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Status</th>
              </tr>
            </thead>
            <tbody>
              {data?.map((product, idx) => (
                <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-sm text-gray-600">{product.sku}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{product.name}</td>
                  <td className="px-4 py-3 text-gray-700">{product.platform}</td>
                  <td className="px-4 py-3 text-gray-700">{formatCurrency(product.revenue)}</td>
                  <td className="px-4 py-3 text-gray-700">{formatCurrency(product.profit)}</td>
                  <td className="px-4 py-3 text-gray-700">{formatPercentage(product.margin)}</td>
                  <td className="px-4 py-3 text-gray-700">{formatROAS(product.roas)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      product.status === 'HEALTHY' ? 'bg-green-100 text-green-800' :
                      product.status === 'LOW_MARGIN' ? 'bg-amber-100 text-amber-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {product.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      </div>
    </div>
  );
}
