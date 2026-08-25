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

// Derive a platform's health status from its own financials (margin is the
// primary signal; a very low ROAS demotes an otherwise-healthy margin, since
// that means ad spend is inefficient even though the platform is profitable).
const derivePlatformStatus = (margin, roas) => {
  if (margin == null) return 'REVIEW';
  if (margin < 0) return 'LOSS';
  if (margin < 15 || (roas != null && roas < 3)) return 'LOW_MARGIN';
  if (margin >= 25) return 'EXCELLENT';
  return 'HEALTHY';
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
    const kpi = response.metrics || response.kpis || response.data || response;

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
      unitsSold: kpi.units_sold || kpi.total_units || 0,
      unitsSoldChange: 0,
      orders: kpi.orders || kpi.total_orders || 0,
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
   * Maps to: GET /api/kpis
   */
  getRevenueChart: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getRevenueChart(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/kpis/by-date', { params });
    const dailyData = response.daily_data || response.daily_kpis || response.data || [];
    const dailyArray = Array.isArray(dailyData) ? dailyData : [];
    // Transform DailyKpiResponse[] to chart-ready format
    return dailyArray.map((item) => ({
      date: item.date || item.sale_date,
      revenue: Number(item.total_revenue || item.net_sales || 0),
      contribution: Number(item.total_profit || 0),
      units: item.units_sold || 0,
      orders: item.orders || 0,
    }));
  },

  /**
   * Get platform performance metrics
   * Maps to: GET /api/platforms
   */
  getPlatformPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getPlatformPerformance(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/platform-performance', { params });
    const platforms = response.platforms || (Array.isArray(response) ? response : response.data) || [];
    // Transform backend response to frontend format
    return platforms.map((p) => {
      const margin = p.profit_margin_pct ? Number(p.profit_margin_pct) : null;
      const roas = p.roas ? Number(p.roas) : null;
      return {
        name: p.platform_name,
        revenue: Number(p.total_sales || p.revenue || 0),
        units: p.total_units || p.units_sold || 0,
        orders: p.total_orders || p.orders || 0,
        adSpend: Number(p.ad_spend || 0),
        roas,
        acos: p.acos_pct ? Number(p.acos_pct) : null,
        margin,
        contribution: Number(p.profit || p.contribution || 0),
        returnRate: p.return_rate_pct ? Number(p.return_rate_pct) : null,
        status: derivePlatformStatus(margin, roas),
      };
    });
  },

  /**
   * Get all product performance
   * Maps to: GET /api/products
   */
  getProductPerformance: async (filters) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getProductPerformance(filters);
    }
    const params = mapFiltersToParams(filters);
    const response = await apiClient.get('/api/product-performance', { params });
    const products = response.products || (Array.isArray(response) ? response : response.data) || [];
    // Transform backend response to frontend format
    return products.map((p) => ({
      sku: p.sku,
      name: p.product_name,
      platform: p.platform || p.platform_id,
      revenue: Number(p.total_sales || p.revenue || 0),
      units: p.total_units || p.units_sold || 0,
      orders: p.total_orders || p.orders || 0,
      profit: Number(p.profit || p.contribution || 0),
      margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : null,
      roas: p.roas ? Number(p.roas) : null,
      acos: p.acos_pct ? Number(p.acos_pct) : null,
      adSpend: Number(p.ad_spend || 0),
      returns: 0, // Backend doesn't provide this per product
      cancellations: 0, // Backend doesn't provide this per product
      status: 'HEALTHY', // Derived from margin if needed
    }));
  },

  /**
   * Get top products by metric
   * Maps to: GET /api/products
   */
  getTopProducts: async (filters, limit = 10, sortBy = 'revenue') => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getTopProducts(filters);
    }
    const params = mapFiltersToParams(filters);
    params.limit = limit;
    params.sort_by = sortBy;
    const response = await apiClient.get('/api/product-performance/top', { params });
    const products = response.products || (Array.isArray(response) ? response : response.data) || [];
    return products.slice(0, limit).map((p) => ({
      id: p.sku,
      name: p.product_name,
      revenue: Number(p.total_sales || p.revenue || 0),
      units: p.total_units || p.units_sold || 0,
      margin: p.profit_margin_pct ? Number(p.profit_margin_pct) : null,
    }));
  },

  /**
   * Get bottom/unprofitable products
   * Maps to: GET /api/products
   */
  getBottomProducts: async (filters, limit = 10) => {
    if (USE_MOCK) {
      return mockAnalyticsApi.getBottomProducts(filters);
    }
    const params = mapFiltersToParams(filters);
    params.limit = limit;
    const response = await apiClient.get('/api/product-performance/bottom', { params });
    const products = response.products || (Array.isArray(response) ? response : response.data) || [];
    // Sort by margin and get bottom performers
    return products
      .sort((a, b) => (a.profit_margin_pct || 0) - (b.profit_margin_pct || 0))
      .slice(0, limit)
      .map((p) => ({
        id: p.sku,
        name: p.product_name,
        revenue: Number(p.total_sales || p.revenue || 0),
        units: p.total_units || p.units_sold || 0,
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

    const alertData = Array.isArray(response) ? response : response.data || response.alerts || [];
    const alerts = alertData.map((a) => ({
      id: a.alert_id || a.id,
      severity: a.severity,
      type: a.alert_type || a.type,
      entity: a.entity,
      platform: a.platform,
      metric: a.metric,
      currentValue: a.current_value,
      threshold: a.threshold,
      recommendation: a.recommendation,
      createdAt: a.created_at,
    }));

    // Count by severity
    const severityCounts = {
      critical: alerts.filter(a => a.severity === 'CRITICAL').length,
      high: alerts.filter(a => a.severity === 'HIGH').length,
      medium: alerts.filter(a => a.severity === 'MEDIUM').length,
    };

    // Return array but attach counts as properties for Dashboard compatibility
    alerts.critical = severityCounts.critical;
    alerts.high = severityCounts.high;
    alerts.medium = severityCounts.medium;

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
      const healthySkus = w.healthy_skus || 0;
      const lowStockSkus = w.low_stock_skus || w.lowStockSkus || 0;
      const criticalSkus = w.critical_skus || 0;
      // Backend has no capacity/days-of-cover per warehouse - don't fabricate them.
      return {
        id: w.warehouse_id,
        name: w.warehouse_name,
        city: w.city,
        region: w.region,
        zone: w.zone,
        lat: w.latitude ? Number(w.latitude) : coords.lat,
        lng: w.longitude ? Number(w.longitude) : coords.lng,
        totalInventory: w.totalInventory || w.total_stock_units || 0,
        totalSkus: healthySkus + lowStockSkus + criticalSkus,
        healthySkus,
        lowStockSkus,
        criticalSkus,
        stockoutSkus: w.stockout_skus || w.stockoutSkus || 0,
        status: w.warehouse_health || w.health_status || 'Healthy',
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
