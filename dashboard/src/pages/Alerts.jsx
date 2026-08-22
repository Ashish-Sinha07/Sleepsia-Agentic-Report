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

  const AlertRow = ({ alert }) => (
    <tr className="border-b border-gray-100 hover:bg-gray-50">
      <td className="px-4 py-3">
        <div className="flex items-center gap-2">
          <AlertCircle className={`w-4 h-4 ${
            alert.severity === 'CRITICAL' ? 'text-red-600' :
            alert.severity === 'HIGH' ? 'text-amber-600' :
            'text-blue-600'
          }`} />
          <span className="text-xs font-semibold">{alert.severity}</span>
        </div>
      </td>
      <td className="px-4 py-3 text-sm text-gray-900">{alert.type}</td>
      <td className="px-4 py-3 text-sm text-gray-700">{alert.entity}</td>
      <td className="px-4 py-3 text-sm text-gray-700">{alert.metric}</td>
      <td className="px-4 py-3 text-sm text-gray-900 font-medium">{alert.currentValue}</td>
      <td className="px-4 py-3 text-sm text-gray-600">{alert.recommendation}</td>
      <td className="px-4 py-3 text-xs text-gray-500">{alert.createdAt}</td>
    </tr>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Alerts & Opportunities</h1>
        <p className="text-gray-600 mt-1">Action center for critical business issues</p>
      </div>

      <FilterBar />

      {criticalAlerts.length > 0 && (
        <div className="card border-l-4 border-l-red-600">
          <div className="card-header bg-red-50">
            <h3 className="font-semibold text-red-900">Critical Alerts ({criticalAlerts.length})</h3>
          </div>
          <div className="card-body overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Severity</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Type</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Entity</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Metric</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Current</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Recommendation</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Time</th>
                </tr>
              </thead>
              <tbody>
                {criticalAlerts.map((alert) => (
                  <AlertRow key={alert.id} alert={alert} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {highAlerts.length > 0 && (
        <div className="card border-l-4 border-l-amber-600">
          <div className="card-header bg-amber-50">
            <h3 className="font-semibold text-amber-900">High Priority ({highAlerts.length})</h3>
          </div>
          <div className="card-body overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Severity</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Type</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Entity</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Metric</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Current</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Recommendation</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Time</th>
                </tr>
              </thead>
              <tbody>
                {highAlerts.map((alert) => (
                  <AlertRow key={alert.id} alert={alert} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {mediumAlerts.length > 0 && (
        <div className="card border-l-4 border-l-blue-600">
          <div className="card-header bg-blue-50">
            <h3 className="font-semibold text-blue-900">Warnings ({mediumAlerts.length})</h3>
          </div>
          <div className="card-body overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Severity</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Type</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Entity</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Metric</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Current</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Recommendation</th>
                  <th className="px-4 py-3 text-left font-semibold text-gray-900">Time</th>
                </tr>
              </thead>
              <tbody>
                {mediumAlerts.map((alert) => (
                  <AlertRow key={alert.id} alert={alert} />
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
