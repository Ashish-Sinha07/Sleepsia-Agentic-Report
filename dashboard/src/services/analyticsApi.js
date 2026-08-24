import apiClient from './api';
import { mockAnalyticsApi } from './mockData';

// FastAPI backend is now live - using real API calls
// Mock mode disabled for production dashboard integration
// mockData kept as fallback/development reference only

const USE_MOCK = false;

// Helper function to format Date object to YYYY-MM-DD string
const formatDateParam = (date) => {
  if (!date) return null;
  if (typeof date === 'string') return date;
  return date.toISOString().split('T')[0];
};

// Helper function to map frontend filters to backend parameters
const mapFiltersToParams = (filters) => {
  const params = {};

  if (filters?.startDate) {
    params.start_date = formatDateParam(filters.startDate);
  }
  if (filters?.endDate) {
    params.end_date = formatDateParam(filters.endDate);
  }
  if (filters?.platform && filters.platform !== 'all') {
    params.platform_id = filters.platform;
  }
  if (filters?.sku && filters.sku !== 'all') {
    params.sku = filters.sku;
  }
  if (filters?.warehouse && filters.warehouse !== 'all') {
    params.warehouse_id = filters.warehouse;
  }
  if (filters?.region && filters.region !== 'all') {
    params.region = filters.region;
  }

  return params;
};

export const analyticsApi = {
  /**
   * Get aggregate KPIs for selected date range
   * Maps to: GET /api/kpis
   */
  getKPIs: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getKPIs(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/kpis', { params });
    const kpi = response.kpis;

    // Transform backend KpiMetrics to frontend format
    return {
      totalRevenue: kpi.total_revenue ? Number(kpi.total_revenue) : 0,
      totalRevenueChange: 0, // Backend doesn't provide change metrics
      netRevenue: kpi.net_revenue ? Number(kpi.net_revenue) : 0,
      netRevenueChange: 0,
      contribution: kpi.total_profit ? Number(kpi.total_profit) : 0,
      contributionChange: 0,
      profitMargin: kpi.profit_margin_pct ? Number(kpi.profit_margin_pct) : 0,
      profitMarginChange: 0,
      unitsSold: kpi.units_sold || 0,
      unitsSoldChange: 0,
      orders: kpi.orders || 0,
      ordersChange: 0,
      adSpend: kpi.ad_spend ? Number(kpi.ad_spend) : 0,
      adSpendChange: 0,
      roas: kpi.roas ? Number(kpi.roas) : null,
      roasChange: 0,
      returnRate: kpi.return_rate_pct ? Number(kpi.return_rate_pct) : 0,
      returnRateChange: 0,
      cancellationRate: kpi.cancellation_rate_pct ? Number(kpi.cancellation_rate_pct) : 0,
      cancellationRateChange: 0,
      organicSales: kpi.organic_sales ? Number(kpi.organic_sales) : 0,
      adAttributedSales: kpi.ad_attributed_sales ? Number(kpi.ad_attributed_sales) : 0,
    };
  },

  /**
   * Get daily KPI timeseries for revenue/sales trend chart
   * Maps to: GET /api/kpis/by-date
   */
  getRevenueChart: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getRevenueChart(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/kpis/by-date', { params });
    // Transform DailyKpiResponse[] to chart-ready format
    return response.data.map((item) => ({
      date: item.date,
      revenue: Number(item.total_revenue),
      contribution: Number(item.total_profit),
      units: item.units_sold,
      orders: item.orders,
    }));
  },

  /**
   * Get platform performance metrics
   * Maps to: GET /api/platform-performance
   */
  getPlatformPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getPlatformPerformance(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/platform-performance', { params });
    // Transform backend response to frontend format
    return response.platforms.map((p) => ({
      name: p.platform_name,
      revenue: Number(p.revenue),
      units: p.units_sold,
      orders: p.orders,
      adSpend: Number(p.ad_spend),
      roas: p.roas ? Number(p.roas) : null,
      acos: p.acos_pct ? Number(p.acos_pct) : null,
      margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : null,
      contribution: Number(p.contribution),
      returnRate: p.return_rate_pct ? Number(p.return_rate_pct) : null,
    }));
  },

  /**
   * Get all product performance
   * Maps to: GET /api/product-performance
   */
  getProductPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getProductPerformance(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/product-performance', { params });
    // Transform backend response to frontend format
    return response.products.map((p) => ({
      sku: p.sku,
      name: p.product_name,
      platform: p.platform || p.platform_id,
      revenue: Number(p.revenue),
      units: p.units_sold,
      orders: p.orders,
      profit: Number(p.contribution),
      margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : null,
      roas: p.roas ? Number(p.roas) : null,
      acos: p.acos_pct ? Number(p.acos_pct) : null,
      adSpend: Number(p.ad_spend),
      returns: 0, // Backend doesn't provide this per product
      cancellations: 0, // Backend doesn't provide this per product
      status: 'HEALTHY', // Derived from margin if needed
    }));
  },

  /**
   * Get top products by metric
   * Maps to: GET /api/product-performance/top
   */
  getTopProducts: async (filters, limit = 10, sortBy = 'revenue') => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getTopProducts(filters);
    }
    const params = mapFiltersToParams(filters);
    params.limit = limit;
    params.sort_by = sortBy;
    const response = await apiClient.get('/api/product-performance/top', { params });
    return response.products.map((p) => ({
      id: p.sku,
      name: p.product_name,
      revenue: Number(p.revenue),
      units: p.units_sold,
      margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : null,
    }));
  },

  /**
   * Get bottom/unprofitable products
   * Maps to: GET /api/product-performance/bottom
   */
  getBottomProducts: async (filters, limit = 10) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getBottomProducts(filters);
    }
    const params = mapFiltersToParams(filters);
    params.limit = limit;
    const response = await apiClient.get('/api/product-performance/bottom', { params });
    return response.products.map((p) => ({
      id: p.sku,
      name: p.product_name,
      revenue: Number(p.revenue),
      units: p.units_sold,
      margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : null,
    }));
  },

  /**
   * Get business alerts
   * Maps to: GET /api/alerts
   * Returns both the alert array and counts for Dashboard
   */
  getAlerts: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getAlerts(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/alerts', { params });

    const alerts = response.alerts.map((a) => ({
      id: a.alert_id,
      severity: a.severity,
      type: a.alert_type,
      entity: a.entity,
      platform: a.platform,
      metric: a.metric,
      currentValue: a.current_value,
      threshold: a.threshold,
      recommendation: a.recommendation,
      createdAt: a.created_at,
    }));

    // Return array but attach counts as properties for Dashboard compatibility
    alerts.critical = response.critical_count || 0;
    alerts.high = response.high_count || 0;
    alerts.medium = response.medium_count || 0;

    return alerts;
  },

  /**
   * Get warehouses with inventory summary
   * Maps to: GET /api/warehouses
   */
  getWarehouses: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getWarehouses(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/warehouses', { params });

    // Default coordinates for Indian warehouse cities
    const cityCoordinates = {
      'Bengaluru': { lat: 12.9716, lng: 77.5946 },
      'Hyderabad': { lat: 17.3850, lng: 78.4867 },
      'Jaipur': { lat: 26.9124, lng: 75.7873 },
      'Mumbai': { lat: 19.0760, lng: 72.8777 },
      'Gurugram': { lat: 28.4595, lng: 77.0266 },
      'Delhi NCR': { lat: 28.6139, lng: 77.2090 },
    };

    return response.warehouses.map((w) => {
      const coords = cityCoordinates[w.city] || { lat: 22.8, lng: 78.5 }; // India center as fallback
      return {
        id: w.warehouse_id,
        name: w.warehouse_name,
        city: w.city,
        region: w.region,
        lat: w.latitude ? Number(w.latitude) : coords.lat,
        lng: w.longitude ? Number(w.longitude) : coords.lng,
        totalInventory: w.totalInventory || w.total_stock_units || 0,
        capacity: 5000,
        skuCount: w.healthy_skus || 0,
        lowStockSkus: w.low_stock_skus || w.lowStockSkus || 0,
        stockoutSkus: w.stockout_skus || w.stockoutSkus || 0,
        daysOfCover: 30,
        status: w.warehouse_health || w.health_status || 'HEALTHY',
      };
    });
  },

  /**
   * Get inventory items with pagination
   * Maps to: GET /api/inventory
   */
  getInventory: async (filters, skip = 0, limit = 100) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getInventory(filters);
    }
    const params = mapFiltersToParams(filters);
    params.skip = skip;
    params.limit = limit;
    const response = await apiClient.get('/api/inventory', { params });
    return response.inventory.map((item) => ({
      warehouse: item.warehouse_name,
      sku: item.sku,
      product: item.product_name,
      currentStock: item.closing_stock || 0,
      avgDailyDemand: item.avg_daily_demand_7d || 0,
      daysOfCover: item.days_of_cover ? Number(item.days_of_cover) : 0,
      reorderPoint: item.reorder_point || 0,
      recommendedReorderQty: item.recommended_reorder_qty || 0,
      status: item.stock_status || 'HEALTHY',
    }));
  },

  /**
   * Get low stock items
   * Maps to: GET /api/inventory/low-stock
   */
  getLowStock: async (filters, limit = 100) => {
    if (USE_MOCK) {
      // Use inventory and filter in frontend
      const inv = await mockAnalyticsApi.getInventory(filters);
      return inv.filter((i) => i.status === 'LOW STOCK');
    }
    const params = mapFiltersToParams(filters);
    params.limit = limit;
    const response = await apiClient.get('/api/inventory/low-stock', { params });
    return response.inventory.map((item) => ({
      warehouse: item.warehouse_name,
      sku: item.sku,
      product: item.product_name,
      currentStock: item.closing_stock,
      daysOfCover: item.days_of_cover ? Number(item.days_of_cover) : 0,
      status: item.stock_status || 'LOW STOCK',
    }));
  },

  /**
   * Get stockout items
   * Maps to: GET /api/inventory/stockouts
   */
  getStockouts: async (filters, limit = 100) => {
    if (USE_MOCK) {
      // Use inventory and filter in frontend
      const inv = await mockAnalyticsApi.getInventory(filters);
      return inv.filter((i) => i.currentStock === 0);
    }
    const params = mapFiltersToParams(filters);
    params.limit = limit;
    const response = await apiClient.get('/api/inventory/stockouts', { params });
    return response.inventory.map((item) => ({
      warehouse: item.warehouse_name,
      sku: item.sku,
      product: item.product_name,
      currentStock: item.closing_stock,
      daysOfCover: item.days_of_cover ? Number(item.days_of_cover) : 0,
      status: item.stock_status || 'STOCKOUT',
    }));
  },

  /**
   * Get advertising performance for the selected period, by platform
   * Maps to: GET /api/advertising
   */
  getAdvertising: async (filters) => {
    if (USE_MOCK) {
      const { advertisingSummary } = await import('./mockData');
      return advertisingSummary;
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/advertising', { params });
    const { summary, platforms } = response;

    return {
      impressions: summary.impressions || 0,
      clicks: summary.clicks || 0,
      attributedSales: summary.attributed_sales ? Number(summary.attributed_sales) : 0,
      adSpend: summary.ad_spend ? Number(summary.ad_spend) : 0,
      orders: summary.orders || 0,
      ctr: summary.ctr_pct ? Number(summary.ctr_pct) : 0,
      roas: summary.roas ? Number(summary.roas) : null,
      acos: summary.acos_pct ? Number(summary.acos_pct) : 0,
      platforms: platforms.map((p) => ({
        name: p.platform_name,
        impressions: p.impressions || 0,
        clicks: p.clicks || 0,
        sales: p.attributed_sales ? Number(p.attributed_sales) : 0,
        spend: p.ad_spend ? Number(p.ad_spend) : 0,
        orders: p.orders || 0,
        roas: p.roas ? Number(p.roas) : null,
        ctr: p.ctr_pct ? Number(p.ctr_pct) : 0,
      })),
    };
  },

  /**
   * Get profitability data (aggregated from multiple endpoints)
   * Combines KPI, platform, and product data
   */
  getProfitabilityData: async (filters) => {
    if (USE_MOCK) {
      // Return hardcoded mock data
      const { profitabilitySummary } = await import('./mockData');
      return profitabilitySummary;
    }
    const params = mapFiltersToParams(filters);

    try {
      // Fetch all required data in parallel
      const [kpiRes, platformRes, productRes] = await Promise.all([
        apiClient.get('/api/kpis', { params }),
        apiClient.get('/api/platform-performance', { params }),
        apiClient.get('/api/product-performance', { params }),
      ]);

      const kpi = kpiRes.kpis;

      return {
        netSales: Number(kpi.net_revenue),
        contribution: Number(kpi.total_profit),
        margin: kpi.profit_margin_pct ? Number(kpi.profit_margin_pct) : 0,
        unitsSold: kpi.units_sold,
        platforms: platformRes.platforms.map((p) => ({
          name: p.platform_name,
          netSales: Number(p.revenue),
          contribution: Number(p.contribution),
          margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : 0,
          units: p.units_sold,
        })),
        products: productRes.products.map((p) => ({
          name: p.product_name,
          netSales: Number(p.revenue),
          contribution: Number(p.contribution),
          margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : 0,
          units: p.units_sold,
        })),
      };
    } catch (error) {
      console.error('Error fetching profitability data:', error);
      throw error;
    }
  },
};
