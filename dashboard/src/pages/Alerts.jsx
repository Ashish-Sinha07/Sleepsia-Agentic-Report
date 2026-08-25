import { useContext, useEffect, useState } from 'react';
import { FilterContext } from '../context/FilterContext';
import { analyticsApi } from '../services/analyticsApi';
import FilterBar from '../components/filters/FilterBar';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import { AlertCircle } from 'lucide-react';

export default function Alerts() {
  const { filters } = useContext(FilterContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await analyticsApi.getAlerts(filters);
        setData(result);
      } catch (err) {
        setError(err.message || 'Failed to load alerts');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const criticalAlerts = data?.filter(a => a.severity === 'CRITICAL') || [];
  const highAlerts = data?.filter(a => a.severity === 'HIGH') || [];
  const mediumAlerts = data?.filter(a => a.severity === 'MEDIUM') || [];

  const AlertRow = ({ alert, index }) => (
    <tr className="border-b border-gray-100 hover:bg-gradient-to-r hover:from-gray-50 hover:to-blue-50 transition-all duration-300 transform hover:scale-102 hover:shadow-md group relative overflow-hidden"
      style={{
        animation: `slideInRight ${0.4 + index * 0.1}s cubic-bezier(0.34, 1.56, 0.64, 1) both`
      }}
    >
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <div className={`p-2 rounded-lg transform group-hover:scale-125 group-hover:rotate-12 transition-all duration-300 ${
            alert.severity === 'CRITICAL' ? 'bg-red-100 text-red-600' :
            alert.severity === 'HIGH' ? 'bg-amber-100 text-amber-600' :
            'bg-blue-100 text-blue-600'
          }`}>
            <AlertCircle className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold text-gray-700">{alert.severity}</span>
        </div>
      </td>
      <td className="px-4 py-3 text-sm font-semibold text-gray-900 group-hover:text-gray-800 transition-colors">{alert.type}</td>
      <td className="px-4 py-3 text-sm text-gray-700 group-hover:text-gray-800 transition-colors">{alert.entity}</td>
      <td className="px-4 py-3 text-sm text-gray-700 group-hover:text-gray-800 transition-colors">{alert.metric}</td>
      <td className="px-4 py-3 text-sm font-bold text-gray-900 group-hover:text-gray-800 transition-colors">{alert.currentValue}</td>
      <td className="px-4 py-3 text-sm text-gray-600 group-hover:text-gray-700 transition-colors italic">{alert.recommendation}</td>
      <td className="px-4 py-3 text-xs text-gray-500 group-hover:text-gray-600 transition-colors font-medium">{alert.createdAt}</td>
    </tr>
  );

  const AlertSection = ({ title, alerts, color }) => (
    <div className={`card-enhanced border-l-4 ${color === 'red' ? 'border-l-red-600' : color === 'amber' ? 'border-l-amber-600' : 'border-l-blue-600'} group animate-fade-in-up`}>
      <div className={`card-header bg-gradient-to-r ${color === 'red' ? 'from-red-50 to-orange-50' : color === 'amber' ? 'from-amber-50 to-yellow-50' : 'from-blue-50 to-cyan-50'} border-b-2 border-gray-200`}>
        <h3 className={`font-bold text-lg bg-gradient-to-r ${color === 'red' ? 'from-red-700 to-red-900' : color === 'amber' ? 'from-amber-700 to-amber-900' : 'from-blue-700 to-blue-900'} bg-clip-text text-transparent`}>
          {title} ({alerts.length})
        </h3>
      </div>
      <div className="card-body overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gray-300 bg-gray-50">
              <th className="px-4 py-3 text-left font-bold text-gray-900">Severity</th>
              <th className="px-4 py-3 text-left font-bold text-gray-900">Type</th>
              <th className="px-4 py-3 text-left font-bold text-gray-900">Entity</th>
              <th className="px-4 py-3 text-left font-bold text-gray-900">Metric</th>
              <th className="px-4 py-3 text-left font-bold text-gray-900">Current</th>
              <th className="px-4 py-3 text-left font-bold text-gray-900">Recommendation</th>
              <th className="px-4 py-3 text-left font-bold text-gray-900">Time</th>
            </tr>
          </thead>
          <tbody>
            {alerts.map((alert, idx) => (
              <AlertRow key={alert.id} alert={alert} index={idx} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="space-y-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen p-0 -m-8 p-8">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-red-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 left-10 w-80 h-80 bg-orange-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10">
        <div className="group mb-8">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-red-600 to-orange-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-red-700 via-orange-600 to-red-800 bg-clip-text text-transparent">
              Alerts & Opportunities
            </h1>
          </div>
          <p className="text-sm text-gray-700 font-medium ml-4">⚡ Action center for critical business issues and opportunities</p>
        </div>

        <FilterBar />

        {criticalAlerts.length > 0 && <AlertSection title="🚨 Critical Alerts" alerts={criticalAlerts} color="red" />}
        {highAlerts.length > 0 && <AlertSection title="⚠️ High Priority" alerts={highAlerts} color="amber" />}
        {mediumAlerts.length > 0 && <AlertSection title="ℹ️ Warnings" alerts={mediumAlerts} color="blue" />}

        {!criticalAlerts.length && !highAlerts.length && !mediumAlerts.length && (
          <div className="bg-gradient-to-br from-green-50 via-emerald-50 to-green-50 p-12 rounded-3xl shadow-2xl shadow-green-300/30 border-2 border-green-300/60 text-center text-green-700 hover:shadow-3xl hover:shadow-green-400/40 transition-all duration-500 group relative overflow-hidden backdrop-blur-sm animate-fade-in-up">
            <div className="text-7xl mb-5 group-hover:scale-125 group-hover:-rotate-12 transition-all duration-500">✨</div>
            <p className="font-black text-2xl text-green-800 group-hover:text-green-900">No alerts at this time</p>
            <p className="text-sm mt-4 opacity-80 text-green-700">Everything looks great! All systems operating normally.</p>
            <div className="mt-6 flex justify-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse"></span>
              <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse animation-delay-200"></span>
              <span className="w-2 h-2 rounded-full bg-green-600 animate-pulse animation-delay-400"></span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
