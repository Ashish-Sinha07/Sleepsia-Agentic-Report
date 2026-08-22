import { useContext, useEffect, useState } from 'react';
import { FilterContext } from '../context/FilterContext';
import { analyticsApi } from '../services/analyticsApi';
import FilterBar from '../components/filters/FilterBar';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import ChartCard from '../components/common/ChartCard';
import BarChart from '../components/charts/BarChart';
import { formatCurrency, formatPercentage, formatROAS } from '../utils/formatting';

export default function PlatformAnalysis() {
  const { filters } = useContext(FilterContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await analyticsApi.getPlatformPerformance(filters);
        setData(result);
      } catch (err) {
        setError(err.message || 'Failed to load platform data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Platform Analysis</h1>
        <p className="text-gray-600 mt-1">Compare performance across all e-commerce platforms</p>
      </div>

      <FilterBar />

      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Revenue by Platform">
          <BarChart data={data} dataKey="revenue" name="Revenue" color="#4a9fbd" />
        </ChartCard>
        <ChartCard title="Profit Margin by Platform">
          <BarChart data={data} dataKey="margin" name="Margin %" color="#10b981" />
        </ChartCard>
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-gray-900">Platform Performance Comparison</h3>
        </div>
        <div className="card-body overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Platform</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Revenue</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Units</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Ad Spend</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">ROAS</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Margin</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-900">Status</th>
              </tr>
            </thead>
            <tbody>
              {data?.map((platform, idx) => (
                <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900">{platform.name}</td>
                  <td className="px-4 py-3 text-gray-700">{formatCurrency(platform.revenue)}</td>
                  <td className="px-4 py-3 text-gray-700">{platform.units.toLocaleString()}</td>
                  <td className="px-4 py-3 text-gray-700">{formatCurrency(platform.adSpend)}</td>
                  <td className="px-4 py-3 text-gray-700">{formatROAS(platform.roas)}</td>
                  <td className="px-4 py-3 text-gray-700">{formatPercentage(platform.margin)}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      platform.status === 'HEALTHY' ? 'bg-green-100 text-green-800' :
                      platform.status === 'LOW_MARGIN' ? 'bg-amber-100 text-amber-800' :
                      'bg-blue-100 text-blue-800'
                    }`}>
                      {platform.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
