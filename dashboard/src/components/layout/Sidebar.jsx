import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Store,
  Package,
  TrendingUp,
  DollarSign,
  Warehouse,
  AlertCircle,
  MessageSquare,
  FileText,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Executive Dashboard', icon: LayoutDashboard },
  { path: '/platforms', label: 'Platform Analysis', icon: Store },
  { path: '/products', label: 'Product Analysis', icon: Package },
  { path: '/advertising', label: 'Advertising', icon: TrendingUp },
  { path: '/profitability', label: 'Profitability', icon: DollarSign },
  { path: '/inventory', label: 'Inventory & Warehouse', icon: Warehouse },
  { path: '/alerts', label: 'Alerts & Opportunities', icon: AlertCircle },
  { path: '/assistant', label: 'AI Business Assistant', icon: MessageSquare },
  { path: '/reports', label: 'Reports', icon: FileText },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 h-screen sticky top-0 overflow-y-auto">
      <nav className="p-6 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all ${
                  isActive
                    ? 'bg-sleepsia-50 text-sleepsia-700 border-l-4 border-sleepsia-600'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-sleepsia-600'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-6 border-t border-gray-200 mt-8">
        <div className="bg-sleepsia-50 rounded-lg p-4 text-center">
          <p className="text-sm text-gray-700 mb-3">Data Quality Status</p>
          <div className="flex items-center justify-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <p className="text-sm font-medium text-gray-900">98.7% Validated</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
