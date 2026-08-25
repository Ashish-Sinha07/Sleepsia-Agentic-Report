import { useContext, useEffect, useState } from 'react';
import { BarChart3, Eye, IndianRupee, MousePointerClick, TrendingUp } from 'lucide-react';
import { FilterContext } from '../context/FilterContext';
import { analyticsApi } from '../services/analyticsApi';
import FilterBar from '../components/filters/FilterBar';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import KpiCard from '../components/common/KpiCard';
import ChartCard from '../components/common/ChartCard';
import BarChart from '../components/charts/BarChart';
import { formatCurrency, formatNumber, formatROAS, formatPercentage, formatACOS } from '../utils/formatting';
import { getPlatformColor } from '../utils/platformColors';

export default function Advertising() {
  const { filters } = useContext(FilterContext);
  const [advertisingSummary, setAdvertisingSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await analyticsApi.getAdvertising(filters);
        setAdvertisingSummary(result);
      } catch (err) {
        setError(err.message || 'Failed to load advertising data');
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
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-orange-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 left-10 w-80 h-80 bg-amber-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10 space-y-6">
        <div className="group mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-orange-600 to-amber-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-orange-700 via-amber-600 to-orange-800 bg-clip-text text-transparent">
              Advertising Analysis
            </h1>
          </div>
          <p className="text-sm text-gray-700 font-medium ml-4">📢 Understand advertising effectiveness and ROI</p>
        </div>

      <FilterBar />

      <p className="text-xs text-gray-500 -mt-3">Advertising performance aggregated from the workbook’s Advertising sheet.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard title="Ad-attributed Sales" value={advertisingSummary.attributedSales} previousValue={advertisingSummary.attributedSales} icon={IndianRupee} />
        <KpiCard title="Ad Spend" value={advertisingSummary.adSpend} previousValue={advertisingSummary.adSpend} icon={BarChart3} />
        <KpiCard title="ROAS" value={advertisingSummary.roas} previousValue={advertisingSummary.roas} type="roas" icon={TrendingUp} />
        <KpiCard title="Clicks" value={advertisingSummary.clicks} previousValue={advertisingSummary.clicks} type="units" icon={MousePointerClick} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ChartCard title="Ad spend by platform" subtitle="Total advertising investment"><BarChart data={advertisingSummary.platforms} dataKey="spend" name="Ad Spend" colorFor={(entry) => getPlatformColor(entry.name)} /></ChartCard>
        <div className="card p-6"><h2 className="font-semibold text-gray-900">Campaign funnel</h2><div className="mt-6 space-y-5"><div className="flex justify-between"><span className="text-gray-600 flex gap-2"><Eye className="w-5 h-5" />Impressions</span><strong>{formatNumber(advertisingSummary.impressions)}</strong></div><div className="flex justify-between"><span className="text-gray-600 flex gap-2"><MousePointerClick className="w-5 h-5" />Clicks (CTR {formatPercentage(advertisingSummary.ctr)})</span><strong>{formatNumber(advertisingSummary.clicks)}</strong></div><div className="flex justify-between"><span className="text-gray-600">Attributed orders</span><strong>{formatNumber(advertisingSummary.orders)}</strong></div><div className="flex justify-between border-t pt-5"><span className="text-gray-600">ACOS</span><strong>{formatACOS(advertisingSummary.acos)}</strong></div></div></div>
      </div>

      <div className="card overflow-hidden"><div className="card-header"><h2 className="font-semibold">Platform advertising performance</h2></div><div className="overflow-x-auto"><table className="w-full text-sm"><thead className="bg-gray-50 text-left text-gray-600"><tr><th className="p-4">Platform</th><th className="p-4 text-right">Impressions</th><th className="p-4 text-right">Clicks</th><th className="p-4 text-right">Ad spend</th><th className="p-4 text-right">Attributed sales</th><th className="p-4 text-right">ROAS</th></tr></thead><tbody>{advertisingSummary.platforms.map((item) => <tr key={item.name} className="border-t border-gray-100"><td className="p-4 font-medium">{item.name}</td><td className="p-4 text-right">{formatNumber(item.impressions)}</td><td className="p-4 text-right">{formatNumber(item.clicks)}</td><td className="p-4 text-right">{formatCurrency(item.spend)}</td><td className="p-4 text-right">{formatCurrency(item.sales)}</td><td className="p-4 text-right font-medium text-green-700">{formatROAS(item.roas)}</td></tr>)}</tbody></table></div></div>
      </div>
    </div>
  );
}
