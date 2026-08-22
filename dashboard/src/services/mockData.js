// Mock data for development and frontend testing
// These will be replaced with real API calls to FastAPI backend

export const mockKPIData = {
  totalRevenue: 4250000,
  totalRevenueChange: -120000,
  netRevenue: 3850000,
  netRevenueChange: 85000,
  contribution: 820000,
  contributionChange: 125000,
  profitMargin: 21.3,
  profitMarginChange: 2.1,
  unitsSold: 12450,
  unitsSoldChange: 1200,
  orders: 2340,
  ordersChange: -45,
  adSpend: 385000,
  adSpendChange: 35000,
  roas: 3.45,
  roasChange: 0.35,
  returnRate: 4.2,
  returnRateChange: -0.5,
  cancellationRate: 3.1,
  cancellationRateChange: 0.2,
};

export const mockRevenueData = [
  { date: '1 Aug', revenue: 125400, contribution: 28650 },
  { date: '2 Aug', revenue: 138900, contribution: 31510 },
  { date: '3 Aug', revenue: 142100, contribution: 32485 },
  { date: '4 Aug', revenue: 135600, contribution: 30960 },
  { date: '5 Aug', revenue: 148300, contribution: 33996 },
  { date: '6 Aug', revenue: 156200, contribution: 35778 },
  { date: '7 Aug', revenue: 162400, contribution: 37150 },
  { date: '8 Aug', revenue: 145600, contribution: 33284 },
  { date: '9 Aug', revenue: 152100, contribution: 34981 },
  { date: '10 Aug', revenue: 158900, contribution: 36441 },
  { date: '11 Aug', revenue: 164200, contribution: 37663 },
  { date: '12 Aug', revenue: 170100, contribution: 38973 },
  { date: '13 Aug', revenue: 145600, contribution: 33384 },
  { date: '14 Aug', revenue: 152100, contribution: 34981 },
  { date: '15 Aug', revenue: 158900, contribution: 36441 },
  { date: '16 Aug', revenue: 164200, contribution: 37663 },
  { date: '17 Aug', revenue: 170100, contribution: 38973 },
  { date: '18 Aug', revenue: 176500, contribution: 40391 },
  { date: '19 Aug', revenue: 182100, contribution: 41782 },
  { date: '20 Aug', revenue: 188300, contribution: 43103 },
  { date: '21 Aug', revenue: 195600, contribution: 44865 },
];

export const mockPlatformData = [
  { name: 'Amazon', revenue: 1425000, units: 4200, orders: 890, adSpend: 145000, roas: 4.2, margin: 23.5, status: 'HEALTHY' },
  { name: 'Flipkart', revenue: 980000, units: 3100, orders: 620, adSpend: 98000, roas: 3.1, margin: 19.8, status: 'HEALTHY' },
  { name: 'Myntra', revenue: 620000, units: 2400, orders: 480, adSpend: 78000, roas: 2.8, margin: 18.2, status: 'LOW_MARGIN' },
  { name: 'Blinkit', revenue: 145000, units: 1850, orders: 240, adSpend: 32000, roas: 2.1, margin: 15.6, status: 'REVIEW' },
  { name: 'JioMart', revenue: 80000, units: 900, orders: 110, adSpend: 32000, roas: 1.5, margin: 12.3, status: 'REVIEW' },
];

export const mockTopProducts = [
  { id: 1, name: 'Sleep Pro Mattress', revenue: 450000, units: 1200, margin: 28.5 },
  { id: 2, name: 'Pillow Deluxe', revenue: 320000, units: 2100, margin: 22.3 },
  { id: 3, name: 'Bedsheet Set Premium', revenue: 285000, units: 1850, margin: 19.2 },
  { id: 4, name: 'Comforter King', revenue: 245000, units: 980, margin: 21.5 },
  { id: 5, name: 'Sleep Mask', revenue: 198000, units: 3200, margin: 35.2 },
  { id: 6, name: 'Mattress Protector', revenue: 165000, units: 1100, margin: 24.8 },
  { id: 7, name: 'Neck Support Pillow', revenue: 142000, units: 950, margin: 26.4 },
  { id: 8, name: 'Cooling Gel Pad', revenue: 135000, units: 850, margin: 23.1 },
  { id: 9, name: 'Sleep Spray', revenue: 98000, units: 2200, margin: 32.5 },
  { id: 10, name: 'Weighted Blanket', revenue: 85000, units: 340, margin: 19.8 },
];

export const mockBottomProducts = [
  { id: 11, name: 'Budget Pillow', revenue: 45000, units: 1200, margin: -5.2 },
  { id: 12, name: 'Basic Sheets', revenue: 38000, units: 950, margin: 2.1 },
  { id: 13, name: 'Economy Mattress', revenue: 32000, units: 250, margin: 1.5 },
  { id: 14, name: 'Clearance Blanket', revenue: 28000, units: 320, margin: -2.3 },
  { id: 15, name: 'Discontinued Pillow', revenue: 18000, units: 450, margin: -8.5 },
];

export const mockProductData = [
  { sku: 'SLEEP-001', name: 'Sleep Pro Mattress', platform: 'Amazon', revenue: 285000, units: 750, profit: 81225, margin: 28.5, roas: 4.8, returns: 2.1, cancellations: 1.2, status: 'HEALTHY' },
  { sku: 'SLEEP-002', name: 'Pillow Deluxe', platform: 'Amazon', revenue: 198000, units: 1320, profit: 44154, margin: 22.3, roas: 4.2, returns: 3.2, cancellations: 1.8, status: 'HEALTHY' },
  { sku: 'SLEEP-003', name: 'Bedsheet Premium', platform: 'Flipkart', revenue: 175000, units: 1200, profit: 33600, margin: 19.2, roas: 3.1, returns: 4.1, cancellations: 2.1, status: 'HEALTHY' },
  { sku: 'SLEEP-004', name: 'Sleep Pro Mattress', platform: 'Flipkart', revenue: 156000, units: 410, profit: 33852, margin: 21.7, roas: 2.9, returns: 2.8, cancellations: 1.5, status: 'LOW_MARGIN' },
  { sku: 'SLEEP-005', name: 'Pillow Deluxe', platform: 'Myntra', revenue: 98000, units: 650, profit: 17920, margin: 18.3, roas: 2.4, returns: 3.8, cancellations: 2.2, status: 'LOW_MARGIN' },
  { sku: 'SLEEP-006', name: 'Sleep Mask', platform: 'Blinkit', revenue: 65000, units: 2100, profit: 22880, margin: 35.2, roas: 1.8, returns: 1.2, cancellations: 0.5, status: 'REVIEW' },
];

export const mockAlerts = [
  { id: 1, severity: 'CRITICAL', type: 'Stockout', entity: 'SKU: SLEEP-001', platform: 'Gurgaon Warehouse', metric: 'Stock', currentValue: '0', threshold: '50', recommendation: 'Replenish immediately.', createdAt: '2 hours ago' },
  { id: 2, severity: 'CRITICAL', type: 'Negative Profit', entity: 'SKU: SLEEP-015', platform: 'Amazon', metric: 'Margin', currentValue: '-8.5%', threshold: '0%', recommendation: 'Review pricing or reduce ad spend.', createdAt: '4 hours ago' },
  { id: 3, severity: 'HIGH', type: 'Low Stock', entity: 'SKU: SLEEP-012', platform: 'Bangalore Warehouse', metric: 'Days of Cover', currentValue: '2.1', threshold: '3', recommendation: 'Replenish within 48 hours.', createdAt: '1 day ago' },
  { id: 4, severity: 'HIGH', type: 'Poor ROAS', entity: 'Myntra Campaign', platform: 'Myntra', metric: 'ROAS', currentValue: '1.5x', threshold: '2.5x', recommendation: 'Review targeting and reduce spend.', createdAt: '1 day ago' },
  { id: 5, severity: 'MEDIUM', type: 'Low Margin', entity: 'SKU: SLEEP-005', platform: 'Multiple', metric: 'Margin', currentValue: '5.2%', threshold: '15%', recommendation: 'Monitor or adjust strategy.', createdAt: '2 days ago' },
];

export const mockWarehouseData = [
  { id: 1, name: 'Gurgaon Hub', city: 'Gurgaon', region: 'North', lat: 28.4595, lng: 77.0266, totalInventory: 24520, skuCount: 132, lowStockSkus: 8, stockoutSkus: 2, daysOfCover: 6.4, status: 'LOW' },
  { id: 2, name: 'Bangalore Central', city: 'Bangalore', region: 'South', lat: 12.9716, lng: 77.5946, totalInventory: 31250, skuCount: 145, lowStockSkus: 5, stockoutSkus: 0, daysOfCover: 8.2, status: 'HEALTHY' },
  { id: 3, name: 'Mumbai West', city: 'Mumbai', region: 'West', lat: 19.0760, lng: 72.8777, totalInventory: 18900, skuCount: 98, lowStockSkus: 12, stockoutSkus: 1, daysOfCover: 4.8, status: 'CRITICAL' },
  { id: 4, name: 'Delhi North', city: 'Delhi', region: 'North', lat: 28.7041, lng: 77.1025, totalInventory: 22100, skuCount: 128, lowStockSkus: 6, stockoutSkus: 0, daysOfCover: 7.1, status: 'HEALTHY' },
  { id: 5, name: 'Kolkata Hub', city: 'Kolkata', region: 'East', lat: 22.5726, lng: 88.3639, totalInventory: 14200, skuCount: 76, lowStockSkus: 15, stockoutSkus: 3, daysOfCover: 3.2, status: 'CRITICAL' },
];

export const mockInventoryData = [
  { warehouse: 'Gurgaon Hub', city: 'Gurgaon', sku: 'SLEEP-001', product: 'Sleep Pro Mattress', currentStock: 450, avgDailyDemand: 70, daysOfCover: 6.4, reorderPoint: 210, recommendedReorderQty: 840, status: 'LOW' },
  { warehouse: 'Bangalore Central', city: 'Bangalore', sku: 'SLEEP-002', product: 'Pillow Deluxe', currentStock: 1200, avgDailyDemand: 145, daysOfCover: 8.3, reorderPoint: 435, recommendedReorderQty: 1450, status: 'HEALTHY' },
  { warehouse: 'Mumbai West', city: 'Mumbai', sku: 'SLEEP-003', product: 'Bedsheet Premium', currentStock: 0, avgDailyDemand: 95, daysOfCover: 0, reorderPoint: 285, recommendedReorderQty: 950, status: 'STOCKOUT' },
  { warehouse: 'Delhi North', city: 'Delhi', sku: 'SLEEP-004', product: 'Comforter King', currentStock: 165, avgDailyDemand: 50, daysOfCover: 3.3, reorderPoint: 150, recommendedReorderQty: 600, status: 'CRITICAL' },
];

// Simulated API delay
const simulateDelay = (ms = 500) => new Promise((resolve) => setTimeout(resolve, ms));

export const mockAnalyticsApi = {
  getKPIs: async (filters) => {
    await simulateDelay();
    return mockKPIData;
  },

  getPlatformPerformance: async (filters) => {
    await simulateDelay();
    return mockPlatformData;
  },

  getRevenueChart: async (filters) => {
    await simulateDelay();
    return mockRevenueData;
  },

  getTopProducts: async (filters) => {
    await simulateDelay();
    return mockTopProducts;
  },

  getBottomProducts: async (filters) => {
    await simulateDelay();
    return mockBottomProducts;
  },

  getProductPerformance: async (filters) => {
    await simulateDelay();
    return mockProductData;
  },

  getAlerts: async (filters) => {
    await simulateDelay();
    return mockAlerts;
  },

  getWarehouses: async (filters) => {
    await simulateDelay();
    return mockWarehouseData;
  },

  getInventory: async (filters) => {
    await simulateDelay();
    return mockInventoryData;
  },
};
