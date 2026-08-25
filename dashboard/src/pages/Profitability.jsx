import { useContext, useEffect, useState } from 'react';
import { DollarSign, Package, Percent, TrendingUp } from 'lucide-react';
import { FilterContext } from '../context/FilterContext';
import { analyticsApi } from '../services/analyticsApi';
import FilterBar from '../components/filters/FilterBar';
import KpiCard from '../components/common/KpiCard';
import ChartCard from '../components/common/ChartCard';
import BarChart from '../components/charts/BarChart';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import { formatCurrency, formatUnits } from '../utils/formatting';

export default function Profitability() {
  const { filters } = useContext(FilterContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await analyticsApi.getProfitabilityData(filters);
        setData(result);
      } catch (err) {
        setError(err.message || 'Failed to load profitability data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  if (loading) return <LoadingState message="Loading profitability data..." />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <ErrorState message="No profitability data available" />;

  return (
    <div className="space-y-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen p-0 -m-8 p-8">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-orange-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 left-10 w-80 h-80 bg-red-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10 space-y-6">
        <div className="group mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-orange-600 to-red-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-orange-700 via-red-600 to-orange-800 bg-clip-text text-transparent">
              Profitability Analysis
            </h1>
          </div>
          <p className="text-sm text-gray-700 font-medium ml-4">💰 Identify profitable and unprofitable products and platforms</p>
        </div>

      <FilterBar />

      <p className="text-xs text-gray-500 -mt-3">Sales, costs, and contribution aggregated from the report workbook.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard title="Net Sales" value={data.netSales} previousValue={data.netSales} icon={DollarSign} />
        <KpiCard title="Contribution" value={data.contribution} previousValue={data.contribution} icon={TrendingUp} />
        <KpiCard title="Contribution Margin" value={data.margin} previousValue={data.margin} type="percentage" icon={Percent} />
        <KpiCard title="Units Sold" value={data.unitsSold} previousValue={data.unitsSold} type="units" icon={Package} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ChartCard title="Contribution by platform" subtitle="Profit contribution after all variable costs"><BarChart data={data.platforms} dataKey="contribution" name="Contribution" /></ChartCard>
        <div className="card overflow-hidden"><div className="card-header"><h2 className="font-semibold">Platform profitability</h2></div><div className="overflow-x-auto"><table className="w-full text-sm"><thead className="bg-gray-50 text-left text-gray-600"><tr><th className="p-4">Platform</th><th className="p-4 text-right">Net sales</th><th className="p-4 text-right">Contribution</th><th className="p-4 text-right">Margin</th></tr></thead><tbody>{data.platforms.map((item) => <tr key={item.name} className="border-t border-gray-100"><td className="p-4 font-medium">{item.name}</td><td className="p-4 text-right">{formatCurrency(item.netSales)}</td><td className="p-4 text-right text-green-700 font-medium">{formatCurrency(item.contribution)}</td><td className="p-4 text-right">{item.margin.toFixed(2)}%</td></tr>)}</tbody></table></div></div>
      </div>

      <div className="card overflow-hidden"><div className="card-header"><h2 className="font-semibold">Product profitability</h2></div><div className="overflow-x-auto"><table className="w-full text-sm"><thead className="bg-gray-50 text-left text-gray-600"><tr><th className="p-4">Product</th><th className="p-4 text-right">Units sold</th><th className="p-4 text-right">Net sales</th><th className="p-4 text-right">Contribution</th><th className="p-4 text-right">Margin</th></tr></thead><tbody>{data.products.map((item) => <tr key={item.name} className="border-t border-gray-100"><td className="p-4 font-medium">{item.name}</td><td className="p-4 text-right">{formatUnits(item.units)}</td><td className="p-4 text-right">{formatCurrency(item.netSales)}</td><td className="p-4 text-right text-green-700 font-medium">{formatCurrency(item.contribution)}</td><td className="p-4 text-right">{item.margin.toFixed(2)}%</td></tr>)}</tbody></table></div></div>
      </div>
    </div>
  );
}
