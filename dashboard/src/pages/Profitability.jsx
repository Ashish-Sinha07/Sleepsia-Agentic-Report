import { DollarSign, Package, Percent, TrendingUp } from 'lucide-react';
import FilterBar from '../components/filters/FilterBar';
import KpiCard from '../components/common/KpiCard';
import ChartCard from '../components/common/ChartCard';
import BarChart from '../components/charts/BarChart';
import { profitabilitySummary } from '../services/mockData';
import { formatCurrency, formatUnits } from '../utils/formatting';

export default function Profitability() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Profitability Analysis</h1>
        <p className="text-gray-600 mt-1">Identify profitable and unprofitable products and platforms</p>
      </div>

      <FilterBar />

      <p className="text-xs text-gray-500 -mt-3">Sales, costs, and contribution aggregated from the report workbook.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard title="Net Sales" value={profitabilitySummary.netSales} previousValue={profitabilitySummary.netSales} icon={DollarSign} />
        <KpiCard title="Contribution" value={profitabilitySummary.contribution} previousValue={profitabilitySummary.contribution} icon={TrendingUp} />
        <KpiCard title="Contribution Margin" value={profitabilitySummary.margin} previousValue={profitabilitySummary.margin} type="percentage" icon={Percent} />
        <KpiCard title="Units Sold" value={profitabilitySummary.unitsSold} previousValue={profitabilitySummary.unitsSold} type="units" icon={Package} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <ChartCard title="Contribution by platform" subtitle="Profit contribution after all variable costs"><BarChart data={profitabilitySummary.platforms} dataKey="contribution" name="Contribution" /></ChartCard>
        <div className="card overflow-hidden"><div className="card-header"><h2 className="font-semibold">Platform profitability</h2></div><div className="overflow-x-auto"><table className="w-full text-sm"><thead className="bg-gray-50 text-left text-gray-600"><tr><th className="p-4">Platform</th><th className="p-4 text-right">Net sales</th><th className="p-4 text-right">Contribution</th><th className="p-4 text-right">Margin</th></tr></thead><tbody>{profitabilitySummary.platforms.map((item) => <tr key={item.name} className="border-t border-gray-100"><td className="p-4 font-medium">{item.name}</td><td className="p-4 text-right">{formatCurrency(item.netSales)}</td><td className="p-4 text-right text-green-700 font-medium">{formatCurrency(item.contribution)}</td><td className="p-4 text-right">{item.margin.toFixed(2)}%</td></tr>)}</tbody></table></div></div>
      </div>

      <div className="card overflow-hidden"><div className="card-header"><h2 className="font-semibold">Product profitability</h2></div><div className="overflow-x-auto"><table className="w-full text-sm"><thead className="bg-gray-50 text-left text-gray-600"><tr><th className="p-4">Product</th><th className="p-4 text-right">Units sold</th><th className="p-4 text-right">Net sales</th><th className="p-4 text-right">Contribution</th><th className="p-4 text-right">Margin</th></tr></thead><tbody>{profitabilitySummary.products.map((item) => <tr key={item.name} className="border-t border-gray-100"><td className="p-4 font-medium">{item.name}</td><td className="p-4 text-right">{formatUnits(item.units)}</td><td className="p-4 text-right">{formatCurrency(item.netSales)}</td><td className="p-4 text-right text-green-700 font-medium">{formatCurrency(item.contribution)}</td><td className="p-4 text-right">{item.margin.toFixed(2)}%</td></tr>)}</tbody></table></div></div>
    </div>
  );
}
