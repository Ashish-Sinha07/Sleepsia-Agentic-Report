/**
 * Application Routes Configuration
 * Maps URL paths to React components
 */

import {
  BarChart3,
  ShoppingCart,
  Package,
  TrendingUp,
  DollarSign,
  Warehouse,
  AlertCircle,
  MessageSquare,
  FileText,
  Layout,
} from 'lucide-react';

// Import page components
import Dashboard from '@/pages/Dashboard';
import PlatformAnalysis from '@/pages/PlatformAnalysis';
import ProductAnalysis from '@/pages/ProductAnalysis';
import Advertising from '@/pages/Advertising';
import Profitability from '@/pages/Profitability';
import Inventory from '@/pages/Inventory';
import Alerts from '@/pages/Alerts';
import AIAssistant from '@/pages/AIAssistant';
import Reports from '@/pages/Reports';

export const mainRoutes = [
  {
    path: '/',
    label: 'Executive Dashboard',
    icon: Layout,
    component: Dashboard,
    description: 'Overview of key business metrics',
  },
  {
    path: '/platforms',
    label: 'Platform Analysis',
    icon: ShoppingCart,
    component: PlatformAnalysis,
    description: 'Performance by e-commerce platform',
  },
  {
    path: '/products',
    label: 'Product Analysis',
    icon: Package,
    component: ProductAnalysis,
    description: 'Product-wise performance metrics',
  },
  {
    path: '/advertising',
    label: 'Advertising',
    icon: TrendingUp,
    component: Advertising,
    description: 'Ad spend and ROI analysis',
  },
  {
    path: '/profitability',
    label: 'Profitability',
    icon: DollarSign,
    component: Profitability,
    description: 'Profit margin and cost analysis',
  },
  {
    path: '/inventory',
    label: 'Inventory & Warehouse',
    icon: Warehouse,
    component: Inventory,
    description: 'Stock levels and warehouse status',
  },
  {
    path: '/alerts',
    label: 'Alerts & Opportunities',
    icon: AlertCircle,
    component: Alerts,
    description: 'Critical alerts and action items',
  },
  {
    path: '/reports',
    label: 'Reports',
    icon: FileText,
    component: Reports,
    description: 'Generate business reports',
  },
  {
    path: '/ai-assistant',
    label: 'AI Business Assistant',
    icon: MessageSquare,
    component: AIAssistant,
    description: 'Ask business questions',
  },
];

/**
 * Get route by path
 * @param {string} path - Route path
 * @returns {object} Route configuration
 */
export const getRouteByPath = (path) => {
  return mainRoutes.find((route) => route.path === path);
};

/**
 * Get all navigation items (for sidebar/menu)
 * @returns {array} Navigation items
 */
export const getNavigationItems = () => {
  return mainRoutes.map((route) => ({
    path: route.path,
    label: route.label,
    icon: route.icon,
  }));
};
