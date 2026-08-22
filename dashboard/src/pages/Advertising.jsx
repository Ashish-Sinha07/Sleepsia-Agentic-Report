import FilterBar from '../components/filters/FilterBar';

export default function Advertising() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Advertising Analysis</h1>
        <p className="text-gray-600 mt-1">Understand advertising effectiveness and ROI</p>
      </div>

      <FilterBar />

      <div className="card p-12 text-center">
        <p className="text-gray-600">Advertising analysis page coming soon...</p>
      </div>
    </div>
  );
}
