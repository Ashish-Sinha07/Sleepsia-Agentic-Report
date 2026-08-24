import { useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, DollarSign, ShoppingCart } from 'lucide-react';
import { useDateRange } from '../App';

const Dashboard = () => {
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { dateRange } = useDateRange();

  useEffect(() => {
    fetchKpis();
  }, [dateRange]);

  const fetchKpis = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `http://localhost:8000/api/kpis?start_date=${dateRange.start}&end_date=${dateRange.end}`
      );
      if (!response.ok) throw new Error('Failed to fetch KPIs');
      const data = await response.json();
      setKpis(data.data || {});
      setError(null);
    } catch (err) {
      setError(err.message);
      setKpis({ metrics: {}, daily_kpis: [] });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading dashboard...</div>;
  }

  const metrics = kpis?.metrics || {};
  const dailyKpis = Array.isArray(kpis?.daily_kpis) ? kpis.daily_kpis : [];

  const KPICard = ({ label, value, icon: Icon }) => (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{label}</p>
          <p className="text-2xl font-bold mt-2">{value || 'N/A'}</p>
        </div>
        <Icon className="w-8 h-8 text-blue-500" />
      </div>
    </div>
  );

  return (
    <div className="p-6 bg-gray-50">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Executive Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of key business metrics</p>
      </div>

      {error && <div className="bg-red-50 p-4 rounded-lg text-red-700 mb-6">{error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <KPICard
          label="Total Revenue"
          value={`₹${(metrics.total_revenue || 0).toFixed(2)}`}
          icon={DollarSign}
        />
        <KPICard
          label="Total Orders"
          value={(metrics.total_orders || 0).toLocaleString()}
          icon={ShoppingCart}
        />
        <KPICard
          label="Total Units"
          value={(metrics.total_units || 0).toLocaleString()}
          icon={TrendingUp}
        />
        <KPICard
          label="Profit Margin"
          value={`${(metrics.profit_margin || 0).toFixed(2)}%`}
          icon={TrendingUp}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {dailyKpis.length > 0 ? (
          <>
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Daily Sales Trend</h2>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyKpis}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="net_sales" stroke="#3b82f6" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-lg font-semibold mb-4">Daily Orders</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dailyKpis}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="orders" fill="#10b981" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        ) : (
          <div className="col-span-2 bg-white p-6 rounded-lg shadow text-center text-gray-500">
            No chart data available
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
