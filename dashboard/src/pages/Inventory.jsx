import { useContext, useEffect, useMemo, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { AlertTriangle, MapPin, Package, Warehouse } from 'lucide-react';
import { FilterContext } from '../context/FilterContext';
import FilterBar from '../components/filters/FilterBar';
import KpiCard from '../components/common/KpiCard';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import { analyticsApi } from '../services/analyticsApi';

const statusClass = (status) => status === 'HEALTHY' ? 'badge-success' : 'badge-warning';
const markerColor = (status) => status === 'HEALTHY' ? '#16a34a' : '#d97706';

export default function Inventory() {
  const { filters } = useContext(FilterContext);
  const [warehouses, setWarehouses] = useState(null);
  const [inventory, setInventory] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([analyticsApi.getWarehouses(filters), analyticsApi.getInventory(filters)])
      .then(([warehouseData, inventoryData]) => {
        setWarehouses(warehouseData);
        setInventory(inventoryData);
        setError(null);
      })
      .catch((err) => setError(err.message || 'Failed to load inventory data'));
  }, [filters]);

  const totals = useMemo(() => {
    if (!warehouses) return null;
    return {
      stock: warehouses.reduce((sum, item) => sum + item.totalInventory, 0),
      lowStock: warehouses.reduce((sum, item) => sum + item.lowStockSkus, 0),
      stockouts: warehouses.reduce((sum, item) => sum + item.stockoutSkus, 0),
    };
  }, [warehouses]);

  if (error) return <ErrorState message={error} />;
  if (!warehouses || !inventory || !totals) return <LoadingState message="Loading warehouse data..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Inventory & Warehouse</h1>
        <p className="text-gray-600 mt-1">Operational visibility into stock availability and warehouse health</p>
      </div>

      <FilterBar />

      <p className="text-xs text-gray-500 -mt-3">Warehouse snapshot from the latest report data.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard title="Active Warehouses" value={warehouses.length} previousValue={warehouses.length} type="number" icon={Warehouse} />
        <KpiCard title="Total Stock" value={totals.stock} previousValue={totals.stock} type="units" icon={Package} />
        <KpiCard title="Low-stock SKUs" value={totals.lowStock} previousValue={0} type="number" icon={AlertTriangle} />
        <KpiCard title="Stockouts" value={totals.stockouts} previousValue={0} type="number" icon={AlertTriangle} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
        <div className="card xl:col-span-3 overflow-hidden">
          <div className="card-header"><h2 className="font-semibold text-gray-900">Warehouse locations</h2></div>
          <MapContainer center={[22.8, 78.5]} zoom={4.5} scrollWheelZoom={false} className="h-[420px] w-full">
            <TileLayer attribution="&copy; OpenStreetMap contributors" url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {warehouses.map((warehouse) => (
              <CircleMarker key={warehouse.id} center={[warehouse.lat, warehouse.lng]} radius={11} pathOptions={{ color: markerColor(warehouse.status), fillColor: markerColor(warehouse.status), fillOpacity: 0.8 }}>
                <Popup>
                  <strong>{warehouse.name}</strong><br />{warehouse.city}<br />
                  Stock: {warehouse.totalInventory.toLocaleString()} units<br />
                  Health: {warehouse.status}
                </Popup>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>

        <div className="card xl:col-span-2">
          <div className="card-header"><h2 className="font-semibold text-gray-900">Warehouse health</h2></div>
          <div className="divide-y divide-gray-100">
            {warehouses.map((warehouse) => (
              <div className="p-4" key={warehouse.id}>
                <div className="flex items-start justify-between gap-2">
                  <div><p className="font-medium text-gray-900">{warehouse.name}</p><p className="text-sm text-gray-500 flex items-center gap-1"><MapPin className="w-3 h-3" />{warehouse.city}</p></div>
                  <span className={statusClass(warehouse.status)}>{warehouse.status}</span>
                </div>
                <div className="mt-3 grid grid-cols-2 text-sm"><span className="text-gray-500">Stock</span><span className="text-right font-medium">{warehouse.totalInventory.toLocaleString()} units</span><span className="text-gray-500 mt-1">Low-stock SKUs</span><span className="text-right font-medium mt-1">{warehouse.lowStockSkus}</span></div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="card-header"><h2 className="font-semibold text-gray-900">Inventory requiring attention</h2></div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm"><thead className="bg-gray-50 text-left text-gray-600"><tr><th className="p-4">Warehouse</th><th className="p-4">SKU</th><th className="p-4">Product</th><th className="p-4 text-right">Stock</th><th className="p-4 text-right">Days cover</th><th className="p-4">Status</th><th className="p-4 text-right">Reorder qty.</th></tr></thead>
            <tbody>{inventory.filter((item) => item.status !== 'HEALTHY').map((item) => <tr key={`${item.warehouse}-${item.sku}`} className="border-t border-gray-100"><td className="p-4">{item.warehouse}</td><td className="p-4">{item.sku}</td><td className="p-4">{item.product}</td><td className="p-4 text-right">{item.currentStock}</td><td className="p-4 text-right">{item.daysOfCover}</td><td className="p-4"><span className={statusClass(item.status)}>{item.status}</span></td><td className="p-4 text-right font-medium">{item.recommendedReorderQty}</td></tr>)}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
