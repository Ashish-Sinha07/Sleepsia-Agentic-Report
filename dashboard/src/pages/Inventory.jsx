import { useEffect, useMemo, useRef, useState } from 'react';
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { AlertTriangle, MapPin, Package, Warehouse } from 'lucide-react';
import KpiCard from '../components/common/KpiCard';
import LoadingState from '../components/common/LoadingState';
import ErrorState from '../components/common/ErrorState';
import { analyticsApi } from '../services/analyticsApi';

// Warehouse/inventory statuses come from the backend as 'Healthy', 'At Risk',
// 'Critical', 'Low Stock', or 'Stockout' (see vw_warehouse_summary /
// inventory_daily.stock_status) - normalize case so this doesn't silently
// fall through to a single default color.
const STATUS_META = {
  'healthy': { badge: 'badge-success', chip: 'bg-green-100 text-green-800', color: '#16a34a' },
  'at risk': { badge: 'badge-atrisk', chip: 'bg-yellow-100 text-yellow-800', color: '#eab308' },
  'low stock': { badge: 'badge-atrisk', chip: 'bg-yellow-100 text-yellow-800', color: '#eab308' },
  'critical': { badge: 'badge-error', chip: 'bg-red-100 text-red-800', color: '#dc2626' },
  'stockout': { badge: 'badge-error', chip: 'bg-red-100 text-red-800', color: '#dc2626' },
};

const statusMeta = (status) =>
  STATUS_META[(status || '').toLowerCase()] || { badge: 'badge-info', chip: 'bg-gray-100 text-gray-700', color: '#6b7280' };
const statusClass = (status) => statusMeta(status).badge;
const statusChipClass = (status) => statusMeta(status).chip;
const markerColor = (status) => statusMeta(status).color;

// Keep the map framed on India rather than the whole hemisphere.
const INDIA_BOUNDS = [[6.0, 67.0], [37.5, 98.0]];

const pulseIcon = (color) =>
  L.divIcon({
    className: '',
    html: `<div class="map-marker">
      <div class="map-marker__pulse" style="background:${color}"></div>
      <div class="map-marker__dot" style="background:${color}"></div>
    </div>`,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -10],
  });

// Keeps India framed to fill the map container - re-fitting whenever the
// container itself resizes (breakpoint changes, sidebar toggling, etc.),
// not just on window resize, since a grid/flex reflow doesn't fire that.
function FitIndiaOnResize({ bounds }) {
  const map = useMap();
  const containerRef = useRef(null);

  useEffect(() => {
    const container = map.getContainer();
    containerRef.current = container;

    const fit = () => {
      map.invalidateSize();
      map.fitBounds(bounds, { padding: [12, 12] });
    };

    fit();

    const observer = new ResizeObserver(() => fit());
    observer.observe(container);
    return () => observer.disconnect();
  }, [map, bounds]);

  return null;
}

export default function Inventory() {
  const [warehouses, setWarehouses] = useState(null);
  const [inventory, setInventory] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Inventory/warehouse endpoints are point-in-time snapshots (they default
    // to the latest available date server-side, with no platform dimension
    // in the underlying schema) - fetch the snapshot as-is, unfiltered.
    Promise.all([analyticsApi.getWarehouses({}), analyticsApi.getInventory({})])
      .then(([warehouseData, inventoryData]) => {
        setWarehouses(warehouseData);
        setInventory(inventoryData);
        setError(null);
      })
      .catch((err) => setError(err.message || 'Failed to load inventory data'));
  }, []);

  const totals = useMemo(() => {
    if (!warehouses) return null;
    return {
      stock: warehouses.reduce((sum, item) => sum + item.totalInventory, 0),
      lowStock: warehouses.reduce((sum, item) => sum + item.lowStockSkus, 0),
      stockouts: warehouses.reduce((sum, item) => sum + item.stockoutSkus, 0),
    };
  }, [warehouses]);

  const productsByWarehouse = useMemo(() => {
    if (!inventory) return {};
    const grouped = {};
    for (const item of inventory) {
      (grouped[item.warehouse] ||= []).push(item);
    }
    return grouped;
  }, [inventory]);

  if (error) return <ErrorState message={error} />;
  if (!warehouses || !inventory || !totals) return <LoadingState message="Loading warehouse data..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Inventory & Warehouse</h1>
        <p className="text-gray-600 mt-1">Operational visibility into stock availability and warehouse health</p>
      </div>

      <p className="text-xs text-gray-500">Warehouse snapshot from the latest report data.</p>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard title="Active Warehouses" value={warehouses.length} previousValue={warehouses.length} type="number" icon={Warehouse} />
        <KpiCard title="Total Stock" value={totals.stock} previousValue={totals.stock} type="units" icon={Package} />
        <KpiCard title="Low-stock SKUs" value={totals.lowStock} previousValue={0} type="number" icon={AlertTriangle} />
        <KpiCard title="Stockouts" value={totals.stockouts} previousValue={0} type="number" icon={AlertTriangle} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-6 items-start">
        <div className="card xl:col-span-3 overflow-hidden">
          <div className="card-header"><h2 className="font-semibold text-gray-900">Warehouse locations</h2></div>
          <MapContainer
            bounds={INDIA_BOUNDS}
            minZoom={3.5}
            maxZoom={8}
            maxBounds={INDIA_BOUNDS}
            maxBoundsViscosity={1.0}
            scrollWheelZoom={false}
            className="h-[420px] w-full"
          >
            <FitIndiaOnResize bounds={INDIA_BOUNDS} />
            <TileLayer
              attribution="&copy; OpenStreetMap contributors &copy; CARTO"
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />
            {warehouses.map((warehouse) => (
              <Marker key={warehouse.id} position={[warehouse.lat, warehouse.lng]} icon={pulseIcon(markerColor(warehouse.status))}>
                <Popup>
                  <strong>{warehouse.name}</strong><br />{warehouse.city}<br />
                  Stock: {warehouse.totalInventory.toLocaleString()} units<br />
                  Health: {warehouse.status}
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        <div className="card xl:col-span-2">
          <div className="card-header"><h2 className="font-semibold text-gray-900">Warehouse health</h2></div>
          <div className="divide-y divide-gray-100">
            {warehouses.map((warehouse) => {
              const products = productsByWarehouse[warehouse.name] || [];
              return (
                <div className="p-4" key={warehouse.id}>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium text-gray-900">{warehouse.name}</p>
                      <p className="text-sm text-gray-500 flex items-center gap-1">
                        <MapPin className="w-3 h-3" />
                        {warehouse.city}{warehouse.region ? ` · ${warehouse.region}` : ''}{warehouse.zone ? ` (${warehouse.zone})` : ''}
                      </p>
                    </div>
                    <span className={statusClass(warehouse.status)}>{warehouse.status}</span>
                  </div>
                  <div className="mt-3 grid grid-cols-2 text-sm">
                    <span className="text-gray-500">Stock</span>
                    <span className="text-right font-medium">{warehouse.totalInventory.toLocaleString()} units</span>
                    <span className="text-gray-500 mt-1">Products</span>
                    <span className="text-right font-medium mt-1">{warehouse.totalSkus || products.length}</span>
                    <span className="text-gray-500 mt-1">Low-stock SKUs</span>
                    <span className="text-right font-medium mt-1">{warehouse.lowStockSkus}</span>
                  </div>
                  {products.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-1.5">
                      {products.map((p) => (
                        <span
                          key={p.sku}
                          title={`${p.product} — ${p.status}`}
                          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${statusChipClass(p.status)}`}
                        >
                          <span className="w-1.5 h-1.5 rounded-full" style={{ background: markerColor(p.status) }} />
                          {p.sku}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      <div className="card overflow-hidden">
        <div className="card-header"><h2 className="font-semibold text-gray-900">Inventory requiring attention</h2></div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm"><thead className="bg-gray-50 text-left text-gray-600"><tr><th className="p-4">Warehouse</th><th className="p-4">SKU</th><th className="p-4">Product</th><th className="p-4 text-right">Stock</th><th className="p-4 text-right">Days cover</th><th className="p-4">Status</th><th className="p-4 text-right">Reorder qty.</th></tr></thead>
            <tbody>{inventory.filter((item) => (item.status || '').toLowerCase() !== 'healthy').map((item) => <tr key={`${item.warehouse}-${item.sku}`} className="border-t border-gray-100"><td className="p-4">{item.warehouse}</td><td className="p-4">{item.sku}</td><td className="p-4">{item.product}</td><td className="p-4 text-right">{item.currentStock}</td><td className="p-4 text-right">{item.daysOfCover}</td><td className="p-4"><span className={statusClass(item.status)}>{item.status}</span></td><td className="p-4 text-right font-medium">{item.recommendedReorderQty}</td></tr>)}</tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
