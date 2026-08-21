import FilterBar from '../components/filters/FilterBar';

export default function Profitability() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Profitability Analysis</h1>
        <p className="text-gray-600 mt-1">Identify profitable and unprofitable products and platforms</p>
      </div>

      <FilterBar />

      <div className="card p-12 text-center">
        <p className="text-gray-600">Profitability analysis page coming soon...</p>
      </div>
    </div>
  );
}
