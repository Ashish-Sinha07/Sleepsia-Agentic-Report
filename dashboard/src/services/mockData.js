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
  // Latest snapshot from final_sleepsia_report_data.xlsx (Warehouse_Master,
  // Inventory_Daily and Supply_Chain_Summary).
  { id: 'WH-NCR', name: 'Delhi NCR Warehouse', city: 'Gurugram', region: 'Delhi NCR', lat: 28.4595, lng: 77.0266, totalInventory: 1291, capacity: 5000, skuCount: 3, lowStockSkus: 0, stockoutSkus: 0, daysOfCover: 71.6, status: 'HEALTHY' },
  { id: 'WH-JPR', name: 'Jaipur Warehouse', city: 'Jaipur', region: 'Jaipur', lat: 26.9124, lng: 75.7873, totalInventory: 862, capacity: 3500, skuCount: 3, lowStockSkus: 1, stockoutSkus: 0, daysOfCover: 53, status: 'AT RISK' },
  { id: 'WH-MUM', name: 'Mumbai Warehouse', city: 'Mumbai', region: 'Mumbai', lat: 19.076, lng: 72.8777, totalInventory: 1142, capacity: 4500, skuCount: 3, lowStockSkus: 0, stockoutSkus: 0, daysOfCover: 61.7, status: 'HEALTHY' },
  { id: 'WH-BLR', name: 'Bengaluru Warehouse', city: 'Bengaluru', region: 'Bengaluru', lat: 12.9716, lng: 77.5946, totalInventory: 916, capacity: 4500, skuCount: 3, lowStockSkus: 0, stockoutSkus: 0, daysOfCover: 50.4, status: 'HEALTHY' },
  { id: 'WH-HYD', name: 'Hyderabad Warehouse', city: 'Hyderabad', region: 'Hyderabad', lat: 17.385, lng: 78.4867, totalInventory: 1129, capacity: 3000, skuCount: 3, lowStockSkus: 0, stockoutSkus: 0, daysOfCover: 64.1, status: 'HEALTHY' },
];

export const mockInventoryData = [
  { warehouse: 'Delhi NCR Warehouse', city: 'Gurugram', sku: 'SLP-1001', product: 'Contour Memory Foam Cervical Pillow', currentStock: 271, avgDailyDemand: 7, daysOfCover: 38.7, reorderPoint: 70, recommendedReorderQty: 0, status: 'HEALTHY' },
  { warehouse: 'Delhi NCR Warehouse', city: 'Gurugram', sku: 'SLP-1002', product: 'Travel Neck Memory Foam Pillow', currentStock: 371, avgDailyDemand: 8, daysOfCover: 46.4, reorderPoint: 80, recommendedReorderQty: 0, status: 'HEALTHY' },
  { warehouse: 'Jaipur Warehouse', city: 'Jaipur', sku: 'SLP-1002', product: 'Travel Neck Memory Foam Pillow', currentStock: 34, avgDailyDemand: 8, daysOfCover: 4.2, reorderPoint: 80, recommendedReorderQty: 86, status: 'LOW STOCK' },
  { warehouse: 'Mumbai Warehouse', city: 'Mumbai', sku: 'SLP-1003', product: 'Alpha Kids Memory Foam Pillow', currentStock: 486, avgDailyDemand: 5, daysOfCover: 97.2, reorderPoint: 50, recommendedReorderQty: 0, status: 'HEALTHY' },
  { warehouse: 'Bengaluru Warehouse', city: 'Bengaluru', sku: 'SLP-1002', product: 'Travel Neck Memory Foam Pillow', currentStock: 321, avgDailyDemand: 8, daysOfCover: 40.1, reorderPoint: 80, recommendedReorderQty: 0, status: 'HEALTHY' },
  { warehouse: 'Hyderabad Warehouse', city: 'Hyderabad', sku: 'SLP-1003', product: 'Alpha Kids Memory Foam Pillow', currentStock: 617, avgDailyDemand: 5, daysOfCover: 123.4, reorderPoint: 50, recommendedReorderQty: 0, status: 'HEALTHY' },
];

// Aggregated from Daily_KPI and Advertising in final_sleepsia_report_data.xlsx.
export const profitabilitySummary = {
  netSales: 6490253.01,
  contribution: 1685651.85,
  margin: 25.97,
  unitsSold: 6070,
  platforms: [
    { name: 'Amazon', netSales: 2054241.02, contribution: 576894.26, margin: 28.08, units: 1913 },
    { name: 'Flipkart', netSales: 1744209.57, contribution: 481637.86, margin: 27.61, units: 1644 },
    { name: 'Blinkit', netSales: 1474964.53, contribution: 340104.61, margin: 23.06, units: 1381 },
    { name: 'Myntra', netSales: 1216837.89, contribution: 287015.12, margin: 23.59, units: 1132 },
  ],
  products: [
    { name: 'Contour Memory Foam Cervical Pillow', netSales: 2971102.59, contribution: 788402.55, margin: 26.53, units: 2097 },
    { name: 'Travel Neck Memory Foam Pillow', netSales: 2103873.11, contribution: 570845.23, margin: 27.13, units: 2477 },
    { name: 'Alpha Kids Memory Foam Pillow', netSales: 1415277.31, contribution: 326404.07, margin: 23.06, units: 1496 },
  ],
};

export const advertisingSummary = {
  impressions: 735764,
  clicks: 32450,
  attributedSales: 2744179.72,
  adSpend: 603699.73,
  orders: 2458,
  ctr: 4.41,
  roas: 4.55,
  acos: 22,
  platforms: [
    { name: 'Amazon', impressions: 232888, clicks: 10241, sales: 860860.29, spend: 185405.28, orders: 769, roas: 4.64, ctr: 4.4 },
    { name: 'Flipkart', impressions: 196650, clicks: 8719, sales: 736171.05, spend: 159377.32, orders: 654, roas: 4.62, ctr: 4.43 },
    { name: 'Blinkit', impressions: 166418, clicks: 7376, sales: 632540.09, spend: 142117.31, orders: 564, roas: 4.45, ctr: 4.43 },
    { name: 'Myntra', impressions: 139808, clicks: 6114, sales: 514608.29, spend: 116799.82, orders: 471, roas: 4.41, ctr: 4.37 },
  ],
};

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
