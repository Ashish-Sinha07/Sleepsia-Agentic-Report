import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error.response?.data || error.message || 'An error occurred'),
);

// KPI endpoints
export const getKpis = (startDate, endDate) =>
  apiClient.get('/api/kpis', {
    params: { start_date: startDate, end_date: endDate },
  });

export const getKpisByDate = (startDate, endDate) =>
  apiClient.get('/api/kpis/by-date', {
    params: { start_date: startDate, end_date: endDate },
  });

// Platform endpoints
export const getPlatformPerformance = (startDate, endDate, platformId = null) =>
  apiClient.get('/api/platforms', {
    params: { start_date: startDate, end_date: endDate, platform_id: platformId },
  });

// Product endpoints
export const getProductPerformance = (startDate, endDate, platformId = null, sku = null) =>
  apiClient.get('/api/products', {
    params: { start_date: startDate, end_date: endDate, platform_id: platformId, sku },
  });

export const getTopProducts = (startDate, endDate, limit = 10, sortBy = 'revenue') =>
  apiClient.get('/api/products', {
    params: { start_date: startDate, end_date: endDate, limit, sort_by: sortBy },
  });

export const getBottomProducts = (startDate, endDate, limit = 10) =>
  apiClient.get('/api/products', {
    params: { start_date: startDate, end_date: endDate, limit },
  });

// Warehouse endpoints
export const getWarehouses = (filterDate = null, region = null) =>
  apiClient.get('/api/warehouses', {
    params: { filter_date: filterDate, region },
  });

// Inventory endpoints
export const getInventory = (filterDate = null, warehouseId = null, status = null, skip = 0, limit = 100) =>
  apiClient.get('/api/inventory', {
    params: { filter_date: filterDate, warehouse_id: warehouseId, status, skip, limit },
  });

export const getLowStock = (filterDate = null, limit = 100) =>
  apiClient.get('/api/inventory/low-stock', {
    params: { filter_date: filterDate, limit },
  });

export const getStockouts = (filterDate = null, limit = 100) =>
  apiClient.get('/api/inventory/stockouts', {
    params: { filter_date: filterDate, limit },
  });

// Alert endpoints
export const getAlerts = (filterDate = null, priority = null, limit = 100) =>
  apiClient.get('/api/alerts', {
    params: { filter_date: filterDate, priority, limit },
  });

export default apiClient;

