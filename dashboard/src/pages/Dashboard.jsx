import { useContext, useEffect, useState } from 'react';
import { FilterContext } from '../context/FilterContext';
import { analyticsApi } from '../services/analyticsApi';
import FilterBar from '../components/filters/FilterBar';
import KpiCard from '../components/common/KpiCard';
import ChartCard from '../components/common/ChartCard';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import RevenueChart from '../components/charts/RevenueChart';
import BarChart from '../components/charts/BarChart';
import DonutChart from '../components/charts/DonutChart';
import {
  TrendingUp,
  DollarSign,
  Percent,
  Package,
  ShoppingCart,
  AlertCircle,
  CheckCircle,
  XCircle,
} from 'lucide-react';

export default function Dashboard() {
  const { filters } = useContext(FilterContext);
  const [kpis, setKpis] = useState(null);
  const [revenueData, setRevenueData] = useState(null);
  const [platformData, setPlatformData] = useState(null);
  const [topProducts, setTopProducts] = useState(null);
  const [bottomProducts, setBottomProducts] = useState(null);
  const [alertCounts, setAlertCounts] = useState({
    critical: 0,
    high: 0,
    medium: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [kpiRes, revenueRes, platformRes, topRes, bottomRes, alertsRes] = await Promise.all([
          analyticsApi.getKPIs(filters),
          analyticsApi.getRevenueChart(filters),
          analyticsApi.getPlatformPerformance(filters),
          analyticsApi.getTopProducts(filters),
          analyticsApi.getBottomProducts(filters),
          analyticsApi.getAlerts(filters),
        ]);
        setKpis(kpiRes);
        setRevenueData(revenueRes);
        setPlatformData(platformRes);
        setTopProducts(topRes);
        setBottomProducts(bottomRes);
        if (alertsRes) {
          setAlertCounts({
            critical: alertsRes.critical || 0,
            high: alertsRes.high || 0,
            medium: alertsRes.medium || 0,
          });
        } else {
          setAlertCounts({ critical: 0, high: 0, medium: 0 });
        }
      } catch (err) {
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  if (loading) return <LoadingState message="Loading dashboard data..." />;
  if (error) return <ErrorState message={error} />;

  const revenueComposition = [
    { name: 'Organic Sales', value: kpis?.organicSales || 0 },
    { name: 'Ad-Attributed Sales', value: kpis?.adAttributedSales || 0 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Executive Dashboard</h1>
        <p className="text-gray-600 mt-1">Business performance overview and key metrics</p>
      </div>

      <FilterBar />

      {/* Alert Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="card">
          <div className="card-body flex items-center gap-4">
            <AlertCircle className="w-10 h-10 text-red-600" />
            <div>
              <p className="text-sm text-gray-600">Critical Alerts</p>
              <p className="text-2xl font-bold text-red-600">{alertCounts.critical}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center gap-4">
            <AlertCircle className="w-10 h-10 text-amber-600" />
            <div>
              <p className="text-sm text-gray-600">High Priority</p>
              <p className="text-2xl font-bold text-amber-600">{alertCounts.high}</p>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-body flex items-center gap-4">
            <CheckCircle className="w-10 h-10 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Warnings</p>
              <p className="text-2xl font-bold text-blue-600">{alertCounts.medium}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Primary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <KpiCard
          title="Total Revenue"
          value={kpis?.totalRevenue}
          previousValue={kpis?.totalRevenue + (kpis?.totalRevenueChange || 0)}
          type="currency"
          icon={DollarSign}
        />
        <KpiCard
          title="Profit/Contribution"
          value={kpis?.contribution}
          previousValue={kpis?.contribution - (kpis?.contributionChange || 0)}
          type="currency"
          icon={TrendingUp}
        />
        <KpiCard
          title="Profit Margin"
          value={kpis?.profitMargin}
          previousValue={kpis?.profitMargin - (kpis?.profitMarginChange || 0)}
          type="percentage"
          icon={Percent}
        />
        <KpiCard
          title="Units Sold"
          value={kpis?.unitsSold}
          previousValue={kpis?.unitsSold - (kpis?.unitsSoldChange || 0)}
          type="units"
          icon={Package}
        />
        <KpiCard
          title="Orders"
          value={kpis?.orders}
          previousValue={kpis?.orders + (kpis?.ordersChange || 0)}
          type="units"
          icon={ShoppingCart}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Revenue & Profit Trend" subtitle="Last 21 days">
          <RevenueChart data={revenueData} showArea={true} />
        </ChartCard>
        <ChartCard title="Revenue Composition">
          <DonutChart data={revenueComposition} />
        </ChartCard>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Platform Performance" subtitle="Revenue by platform">
          <BarChart
            data={platformData}
            dataKey="revenue"
            name="Revenue"
            color="#4a9fbd"
          />
        </ChartCard>
        <ChartCard title="Platform Profitability" subtitle="Contribution by platform">
          <BarChart
            data={platformData}
            dataKey="margin"
            name="Margin %"
            color="#10b981"
          />
        </ChartCard>
      </div>

      {/* Charts Row 3 */}
      <div className="grid grid-cols-2 gap-6">
        <ChartCard title="Top 10 Products by Revenue">
          <BarChart
            data={topProducts}
            dataKey="revenue"
            name="Revenue"
            color="#4a9fbd"
            horizontal={true}
          />
        </ChartCard>
        <ChartCard title="Bottom 5 Products" subtitle="Lowest contribution">
          <BarChart
            data={bottomProducts}
            dataKey="revenue"
            name="Revenue"
            color="#ef4444"
            horizontal={true}
          />
        </ChartCard>
      </div>

      {/* Secondary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard
          title="Advertising Spend"
          value={kpis?.adSpend}
          previousValue={kpis?.adSpend - (kpis?.adSpendChange || 0)}
          type="currency"
        />
        <KpiCard
          title="ROAS"
          value={kpis?.roas}
          previousValue={kpis?.roas - (kpis?.roasChange || 0)}
          type="roas"
        />
        <KpiCard
          title="Return Rate"
          value={kpis?.returnRate}
          previousValue={kpis?.returnRate + (kpis?.returnRateChange || 0)}
          type="percentage"
        />
        <KpiCard
          title="Cancellation Rate"
          value={kpis?.cancellationRate}
          previousValue={kpis?.cancellationRate - (kpis?.cancellationRateChange || 0)}
          type="percentage"
        />
      </div>
    </div>
  );
}
