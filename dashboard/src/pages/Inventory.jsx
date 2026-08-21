import FilterBar from '../components/filters/FilterBar';

export default function Inventory() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Inventory & Warehouse</h1>
        <p className="text-gray-600 mt-1">Operational visibility into stock availability and warehouse health</p>
      </div>

      <FilterBar />

      <div className="card p-12 text-center">
        <p className="text-gray-600">Inventory and warehouse page coming soon...</p>
      </div>
    </div>
  );
}
