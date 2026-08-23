import apiClient from './api';
import { mockAnalyticsApi } from './mockData';

// Switch between mock data and real API calls
// Set to true to use mock data, false to use real backend API
// The backend must be running on http://localhost:8000

const USE_MOCK = import.meta.env.VITE_USE_MOCK_DATA !== 'false';

const toApiFilters = (filters = {}) => ({
  start_date: filters.startDate ? new Date(filters.startDate).toISOString().slice(0, 10) : undefined,
  end_date: filters.endDate ? new Date(filters.endDate).toISOString().slice(0, 10) : undefined,
  platform_id: filters.platform && filters.platform !== 'all' ? filters.platform : undefined,
});

const toNumber = (value) => Number(value || 0);

const normalizePlatform = (platform) => ({
  name: platform.platform_name,
  revenue: toNumber(platform.revenue),
  units: toNumber(platform.units_sold),
  adSpend: toNumber(platform.ad_spend),
  roas: toNumber(platform.roas),
  margin: toNumber(platform.margin ?? platform.profit_margin_pct),
  status: platform.margin >= 15 ? 'HEALTHY' : 'LOW_MARGIN',
});

const normalizeProduct = (product) => ({
  sku: product.sku,
  name: product.product_name,
  platform: product.platform || product.platform_id || 'All Platforms',
  revenue: toNumber(product.revenue),
  profit: toNumber(product.contribution),
  margin: toNumber(product.margin ?? product.profit_margin_pct),
  roas: toNumber(product.roas),
  status: product.margin >= 15 ? 'HEALTHY' : 'LOW_MARGIN',
});

export const analyticsApi = {
  getKPIs: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getKPIs(filters);
    }
    return apiClient.get('/api/kpis', {
      params: { ...toApiFilters(filters), include_insights: false },
    });
  },

  getPlatformPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getPlatformPerformance(filters);
    }
    const response = await apiClient.get('/api/platform-performance', { params: toApiFilters(filters) });
    return (response.platforms || []).map(normalizePlatform);
  },

  getRevenueChart: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getRevenueChart(filters);
    }
    const response = await apiClient.get('/api/kpis/by-date', { params: toApiFilters(filters) });
    return (response.daily_data || []).map((item) => ({
      date: item.date,
      revenue: toNumber(item.total_revenue),
      contribution: toNumber(item.total_profit),
    }));
  },

  getTopProducts: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getTopProducts(filters);
    }
    const response = await apiClient.get('/api/product-performance/top', { params: toApiFilters(filters) });
    return (response.products || []).map(normalizeProduct);
  },

  getBottomProducts: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getBottomProducts(filters);
    }
    const response = await apiClient.get('/api/product-performance/bottom', { params: toApiFilters(filters) });
    return (response.products || []).map(normalizeProduct);
  },

  getProductPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getProductPerformance(filters);
    }
    const response = await apiClient.get('/api/product-performance', { params: toApiFilters(filters) });
    return (response.products || []).map(normalizeProduct);
  },

  getAlerts: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getAlerts(filters);
    }
    const response = await apiClient.get('/api/alerts', { params: toApiFilters(filters) });
    return (response.alerts || []).map((alert) => ({
      severity: alert.severity,
      type: alert.alert_type,
      entity: alert.entity,
      metric: alert.metric,
      currentValue: alert.current_value,
      recommendation: alert.recommendation,
      createdAt: alert.created_at,
    }));
  },

  getWarehouses: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getWarehouses(filters);
    }
    const response = await apiClient.get('/api/warehouses', { params: toApiFilters(filters) });
    return (response.warehouses || []).map((warehouse) => ({
      id: warehouse.warehouse_id,
      name: warehouse.warehouse_name,
      city: warehouse.city,
      lat: toNumber(warehouse.latitude),
      lng: toNumber(warehouse.longitude),
      totalInventory: toNumber(warehouse.totalInventory ?? warehouse.total_stock_units),
      lowStockSkus: toNumber(warehouse.lowStockSkus ?? warehouse.low_stock_skus),
      stockoutSkus: toNumber(warehouse.stockoutSkus ?? warehouse.stockout_skus),
      status: warehouse.warehouse_health || warehouse.health_status || 'HEALTHY',
    }));
  },

  getInventory: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getInventory(filters);
    }
    const response = await apiClient.get('/api/inventory', { params: toApiFilters(filters) });
    return (response.inventory || []).map((item) => ({
      warehouse: item.warehouse_name,
      sku: item.sku,
      product: item.product_name,
      currentStock: toNumber(item.closing_stock),
      daysOfCover: toNumber(item.days_of_cover),
      status: String(item.stock_status || '').toUpperCase(),
      recommendedReorderQty: toNumber(item.recommended_reorder_qty),
    }));
  },
};
