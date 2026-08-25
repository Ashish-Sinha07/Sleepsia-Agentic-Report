import { useState, useEffect } from 'react';
import { AlertCircle, Clock, Package } from 'lucide-react';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/alerts');
      if (!response.ok) throw new Error('Failed to fetch alerts');
      const data = await response.json();
      setAlerts(Array.isArray(data.alerts) ? data.alerts : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6 text-center text-gray-600">Loading alerts...</div>;

  const groupAlertsBySeverity = (alerts) => {
    return {
      critical: alerts.filter(a => a.severity === 'CRITICAL'),
      high: alerts.filter(a => a.severity === 'HIGH'),
      medium: alerts.filter(a => a.severity === 'MEDIUM'),
      low: alerts.filter(a => a.severity === 'LOW'),
    };
  };

  const getSeverityConfig = (severity) => {
    const config = {
      'CRITICAL': {
        bg: 'from-red-50 to-red-100',
        border: 'border-red-400',
        badge: 'bg-red-600 text-white',
        text: 'text-red-900',
        icon: 'text-red-600',
        urgency: '⚠️ URGENT',
      },
      'HIGH': {
        bg: 'from-orange-50 to-orange-100',
        border: 'border-orange-400',
        badge: 'bg-orange-600 text-white',
        text: 'text-orange-900',
        icon: 'text-orange-600',
        urgency: '⚡ HIGH',
      },
      'MEDIUM': {
        bg: 'from-yellow-50 to-yellow-100',
        border: 'border-yellow-400',
        badge: 'bg-yellow-600 text-white',
        text: 'text-yellow-900',
        icon: 'text-yellow-600',
        urgency: '📋 MEDIUM',
      },
      'LOW': {
        bg: 'from-blue-50 to-blue-100',
        border: 'border-blue-400',
        badge: 'bg-blue-600 text-white',
        text: 'text-blue-900',
        icon: 'text-blue-600',
        urgency: 'ℹ️ LOW',
      },
    };
    return config[severity] || config['MEDIUM'];
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const AlertCard = ({ alert }) => {
    const config = getSeverityConfig(alert.severity);
    const stockPercentage = Math.max(0, Math.min(100, (alert.current_value / alert.threshold) * 100));

    return (
      <div
        className={`bg-gradient-to-br ${config.bg} border-l-4 ${config.border} p-6 rounded-xl hover:shadow-lg transition-all duration-300`}
      >
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${config.badge}`}>
              <AlertCircle className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <h3 className={`font-bold text-lg ${config.text}`}>{alert.alert_type}</h3>
                <span className={`text-xs font-bold px-2 py-1 rounded ${config.badge}`}>
                  {config.urgency}
                </span>
              </div>
              <div className="bg-white/70 rounded-lg px-3 py-2 inline-block border border-gray-200/60 mb-2">
                <p className="text-xs font-semibold text-gray-600 mb-1">PRODUCT</p>
                <p className={`font-bold ${config.text}`}>
                  {alert.product_name || 'Unknown Product'} ({alert.entity})
                </p>
              </div>
              <div className="flex items-center gap-3 mt-2 text-sm text-gray-700">
                <span className="font-semibold">📍 Warehouse:</span>
                <span className={`px-2 py-1 rounded bg-white/60 border border-gray-200/60 font-bold`}>
                  {alert.warehouse}
                </span>
                {alert.region && (
                  <>
                    <span className="font-semibold">🏙️ Region:</span>
                    <span className={`px-2 py-1 rounded bg-white/60 border border-gray-200/60 font-bold`}>
                      {alert.region}
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>
          <p className="text-xs font-semibold text-gray-500">{formatDate(alert.created_at)}</p>
        </div>

        {/* Main Issue Statement */}
        <div className={`bg-white/60 rounded-lg p-4 mb-4 border ${config.border}/40`}>
          <p className={`font-semibold ${config.text} leading-relaxed`}>
            Stock for <span className="font-black">{alert.product_name || alert.entity}</span> ({alert.entity}) at{' '}
            <span className="font-black">{alert.warehouse}</span> warehouse has fallen to{' '}
            <span className="font-black text-lg">{alert.current_value}</span> units,
            <span className="font-black"> {Math.abs(alert.gap)} below</span> the minimum threshold of{' '}
            <span className="font-black">{alert.threshold}</span> units.
          </p>
        </div>

        {/* Context Metrics */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          {/* Stock Gap */}
          <div className="bg-white/70 rounded-lg p-3 border border-gray-200/60">
            <p className="text-xs font-semibold text-gray-600 mb-1">STOCK GAP</p>
            <div className="flex items-center gap-2">
              <Package className={`w-4 h-4 ${config.icon}`} />
              <p className={`font-black text-lg ${config.text}`}>{alert.gap}</p>
            </div>
            <p className="text-xs text-gray-500 mt-1">Below threshold</p>
          </div>

          {/* Days of Cover */}
          <div className="bg-white/70 rounded-lg p-3 border border-gray-200/60">
            <p className="text-xs font-semibold text-gray-600 mb-1">DAYS OF COVER</p>
            <div className="flex items-center gap-2">
              <Clock className={`w-4 h-4 ${config.icon}`} />
              <p className={`font-black text-lg ${config.text}`}>{alert.days_of_cover.toFixed(1)}</p>
            </div>
            <p className="text-xs text-gray-500 mt-1">at current demand</p>
          </div>

          {/* Daily Demand */}
          <div className="bg-white/70 rounded-lg p-3 border border-gray-200/60">
            <p className="text-xs font-semibold text-gray-600 mb-1">DAILY DEMAND</p>
            <div className="flex items-center gap-2">
              <TrendingDown className={`w-4 h-4 ${config.icon}`} />
              <p className={`font-black text-lg ${config.text}`}>{alert.avg_daily_demand}</p>
            </div>
            <p className="text-xs text-gray-500 mt-1">units/day (7-day avg)</p>
          </div>
        </div>

        {/* Stock Level Visualization */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <p className="text-xs font-semibold text-gray-600">STOCK LEVEL vs THRESHOLD</p>
            <p className="text-xs font-bold text-gray-700">{stockPercentage.toFixed(0)}% of threshold</p>
          </div>
          <div className="w-full h-2 bg-gray-300 rounded-full overflow-hidden">
            <div
              className={`h-full ${
                alert.gap < 0
                  ? 'bg-red-600'
                  : alert.gap < alert.threshold * 0.2
                    ? 'bg-orange-600'
                    : 'bg-green-600'
              } transition-all duration-300`}
              style={{ width: `${stockPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Recommendation */}
        <div className={`bg-white/60 border-l-4 ${config.border} rounded-lg p-3`}>
          <p className="text-xs font-semibold text-gray-600 mb-1">RECOMMENDED ACTION</p>
          <p className={`text-sm font-semibold ${config.text}`}>{alert.recommendation}</p>
        </div>
      </div>
    );
  };

  const groupedAlerts = groupAlertsBySeverity(alerts);
  const allAlerts = [
    ...groupedAlerts.critical,
    ...groupedAlerts.high,
    ...groupedAlerts.medium,
    ...groupedAlerts.low,
  ];

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-4xl font-black bg-gradient-to-r from-red-700 via-orange-600 to-red-800 bg-clip-text text-transparent mb-2">
          Alerts & Opportunities
        </h1>
        <p className="text-gray-600 text-lg">⚡ Critical inventory and action alerts</p>
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-lg mb-6 flex items-center gap-3">
          <span className="text-2xl">⚠️</span>
          <span className="text-red-700 font-semibold">{error}</span>
        </div>
      )}

      {allAlerts.length > 0 ? (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-red-50 border border-red-400 p-4 rounded-lg text-center">
              <p className="text-3xl font-black text-red-600">{groupedAlerts.critical.length}</p>
              <p className="text-xs text-red-700 font-semibold mt-2">Critical</p>
            </div>
            <div className="bg-orange-50 border border-orange-400 p-4 rounded-lg text-center">
              <p className="text-3xl font-black text-orange-600">{groupedAlerts.high.length}</p>
              <p className="text-xs text-orange-700 font-semibold mt-2">High</p>
            </div>
            <div className="bg-yellow-50 border border-yellow-400 p-4 rounded-lg text-center">
              <p className="text-3xl font-black text-yellow-600">{groupedAlerts.medium.length}</p>
              <p className="text-xs text-yellow-700 font-semibold mt-2">Medium</p>
            </div>
            <div className="bg-blue-50 border border-blue-400 p-4 rounded-lg text-center">
              <p className="text-3xl font-black text-blue-600">{groupedAlerts.low.length}</p>
              <p className="text-xs text-blue-700 font-semibold mt-2">Low</p>
            </div>
          </div>

          {/* Alerts by Severity */}
          {allAlerts.map((alert, i) => (
            <AlertCard key={i} alert={alert} />
          ))}
        </div>
      ) : (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 p-12 rounded-xl text-center border-2 border-green-300">
          <div className="text-6xl mb-4">✨</div>
          <p className="text-2xl font-black text-green-800">No Alerts</p>
          <p className="text-green-700 mt-2">All inventory levels are healthy!</p>
        </div>
      )}
    </div>
  );
};

export default Alerts;
