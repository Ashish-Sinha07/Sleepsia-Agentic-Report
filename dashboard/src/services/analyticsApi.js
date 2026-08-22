import apiClient from './api';
import { mockAnalyticsApi } from './mockData';

// During development, use mock data
// When backend is ready, switch to real API calls

const USE_MOCK = true;

export const analyticsApi = {
  getKPIs: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getKPIs(filters);
    }
    return apiClient.get('/api/kpis', { params: filters });
  },

  getPlatformPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getPlatformPerformance(filters);
    }
    return apiClient.get('/api/platform-performance', { params: filters });
  },

  getRevenueChart: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getRevenueChart(filters);
    }
    return apiClient.get('/api/revenue-chart', { params: filters });
  },

  getTopProducts: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getTopProducts(filters);
    }
    return apiClient.get('/api/top-products', { params: filters });
  },

  getBottomProducts: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getBottomProducts(filters);
    }
    return apiClient.get('/api/bottom-products', { params: filters });
  },

  getProductPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getProductPerformance(filters);
    }
    return apiClient.get('/api/product-performance', { params: filters });
  },

  getAlerts: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getAlerts(filters);
    }
    return apiClient.get('/api/alerts', { params: filters });
  },

  getWarehouses: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getWarehouses(filters);
    }
    return apiClient.get('/api/warehouses', { params: filters });
  },

  getInventory: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getInventory(filters);
    }
    return apiClient.get('/api/inventory', { params: filters });
  },
};
