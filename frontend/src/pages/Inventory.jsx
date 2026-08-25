import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

// Fix marker icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.1/images/marker-shadow.png',
});

const Inventory = () => {
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const fetchWarehouses = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/warehouses');
      if (!response.ok) throw new Error('Failed to fetch warehouse data');
      const data = await response.json();
      setWarehouses(Array.isArray(data.data) ? data.data : []);
      setError(null);
    } catch (err) {
      setError(err.message);
      setWarehouses([]);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-6">Loading inventory data...</div>;

  return (
    <div className="p-6 bg-gray-50">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Inventory & Warehouse</h1>
      <p className="text-gray-600 mb-6">Stock levels and warehouse status</p>

      {error && <div className="bg-red-50 p-4 rounded-lg text-red-700 mb-6">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Warehouse Map</h2>
          {warehouses.length > 0 && warehouses[0].latitude ? (
            <MapContainer
              center={[warehouses[0].latitude, warehouses[0].longitude]}
              zoom={5}
              style={{ height: '400px', width: '100%' }}
            >
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              {warehouses.map((wh, i) => (
                <Marker
                  key={i}
                  position={[wh.latitude || 0, wh.longitude || 0]}
                >
                  <Popup>
                    <div className="text-sm">
                      <p className="font-semibold">{wh.warehouse_name}</p>
                      <p>City: {wh.city}</p>
                      <p>Inventory: {wh.total_inventory || 0} units</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          ) : (
            <div className="h-96 bg-gray-100 rounded flex items-center justify-center text-gray-500">
              Map data not available
            </div>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Warehouse Status</h2>
          <div className="space-y-4">
            {warehouses.map((wh, i) => (
              <div key={i} className="border rounded p-4">
                <p className="font-semibold text-sm">{wh.warehouse_name}</p>
                <p className="text-xs text-gray-600">{wh.city}</p>
                <div className="mt-2 text-xs space-y-1">
                  <p>📦 Inventory: {wh.total_inventory || 0}</p>
                  <p>📊 SKUs: {wh.sku_count || 0}</p>
                  <p>⚠️ Low Stock: {wh.low_stock_count || 0}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {warehouses.length > 0 && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Detailed Warehouse Metrics</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="border-b">
                <tr>
                  <th className="text-left p-2">Warehouse</th>
                  <th className="text-right p-2">City</th>
                  <th className="text-right p-2">Inventory</th>
                  <th className="text-right p-2">SKU Count</th>
                  <th className="text-right p-2">Days of Cover</th>
                </tr>
              </thead>
              <tbody>
                {warehouses.map((wh, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="p-2">{wh.warehouse_name}</td>
                    <td className="p-2">{wh.city}</td>
                    <td className="text-right p-2">{wh.total_inventory || 0}</td>
                    <td className="text-right p-2">{wh.sku_count || 0}</td>
                    <td className="text-right p-2">{(wh.days_of_cover || 0).toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default Inventory;
