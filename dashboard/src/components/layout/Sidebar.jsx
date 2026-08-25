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
  X,
  Sparkles,
  Library,
} from 'lucide-react';

const navItems = [
  { path: '/', label: 'Executive Dashboard', icon: LayoutDashboard, color: 'from-blue-500 to-cyan-500' },
  { path: '/platforms', label: 'Platform Analysis', icon: Store, color: 'from-purple-500 to-pink-500' },
  { path: '/products', label: 'Product Analysis', icon: Package, color: 'from-green-500 to-emerald-500' },
  { path: '/advertising', label: 'Advertising', icon: TrendingUp, color: 'from-orange-500 to-red-500' },
  { path: '/profitability', label: 'Profitability', icon: DollarSign, color: 'from-yellow-500 to-orange-500' },
  { path: '/inventory', label: 'Inventory & Warehouse', icon: Warehouse, color: 'from-indigo-500 to-blue-500' },
  { path: '/alerts', label: 'Alerts & Opportunities', icon: AlertCircle, color: 'from-red-500 to-rose-500' },
  { path: '/assistant', label: 'AI Business Assistant', icon: MessageSquare, color: 'from-violet-500 to-purple-500' },
  { path: '/reports', label: 'Reports', icon: FileText, color: 'from-cyan-500 to-blue-500' },
  { path: '/knowledge', label: 'Knowledge Base', icon: Library, color: 'from-teal-500 to-emerald-500' },
];

export default function Sidebar({ isOpen = false, onClose = () => {} }) {
  return (
    <>
      {/* Backdrop: mobile/tablet only, shown while the drawer is open */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-900/50 z-40 lg:hidden backdrop-blur-sm transition-opacity duration-300"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed lg:sticky top-0 left-0 h-screen w-64 bg-gradient-to-b from-slate-900 via-blue-900 to-slate-900 border-r border-blue-400/20
          overflow-y-auto scrollbar-hide z-50 transform transition-all duration-300 ease-in-out shadow-2xl
          ${isOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 backdrop-blur-sm`}
      >
        {/* Animated background blobs */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-10 left-10 w-40 h-40 bg-blue-500/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
          <div className="absolute bottom-20 right-10 w-40 h-40 bg-cyan-500/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
        </div>

        {/* Logo Section */}
        <div className="sticky top-0 z-10 bg-gradient-to-b from-slate-900 via-blue-900 to-transparent p-6 backdrop-blur-sm border-b border-blue-400/10">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 group">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-lg flex items-center justify-center text-slate-900 font-bold transform group-hover:scale-110 group-hover:rotate-12 transition-all duration-500 shadow-lg shadow-blue-500/50">
                S
              </div>
              <div>
                <h1 className="text-lg font-bold text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-blue-300 group-hover:to-cyan-300 group-hover:bg-clip-text transition-all duration-300">Sleepsia</h1>
                <p className="text-xs text-blue-200/60 group-hover:text-blue-200 transition-colors">Analytics</p>
              </div>
            </div>
            {/* Close button for mobile */}
            <button
              onClick={onClose}
              className="lg:hidden min-w-[40px] min-h-[40px] flex items-center justify-center text-blue-200 hover:text-white hover:bg-blue-500/30 rounded-lg transition-all duration-300 transform hover:scale-110"
              aria-label="Close menu"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-4 space-y-2 relative z-10">
          {navItems.map((item, idx) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 transform hover:translate-x-2 group relative overflow-hidden ${
                    isActive
                      ? `bg-gradient-to-r ${item.color} text-white font-semibold shadow-lg shadow-blue-500/50 backdrop-blur-md border border-blue-300/50`
                      : 'text-blue-100 hover:bg-blue-500/40 hover:shadow-lg backdrop-blur-sm border border-blue-400/10'
                  }`
                }
                style={{
                  animation: `slideInLeft ${0.3 + idx * 0.05}s ease-out`,
                }}
              >
                {/* Ripple effect for active items */}
                {({ isActive }) => isActive && <div className="absolute inset-0 bg-white/10 animate-pulse"></div>}

                {/* Icon with animation */}
                <div className={`w-6 h-6 relative z-10 transform group-hover:scale-125 group-hover:rotate-12 transition-all duration-300 flex items-center justify-center`}>
                  <Icon className="w-5 h-5" />
                </div>

                {/* Label */}
                <span className="group-hover:font-bold transition-all duration-300 relative z-10">{item.label}</span>

                {/* Glow effect on hover */}
                <div className={`absolute inset-0 bg-gradient-to-r ${item.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300 rounded-xl`}></div>
              </NavLink>
            );
          })}
        </nav>

        {/* Data Quality Status Section */}
        <div className="sticky bottom-0 p-6 border-t border-blue-400/20 bg-gradient-to-t from-slate-900 via-blue-900 to-transparent backdrop-blur-sm relative z-10">
          <div className="bg-gradient-to-br from-green-500/20 via-emerald-500/20 to-green-500/20 rounded-xl p-4 border border-green-400/30 hover:border-green-400/60 transition-all duration-300 group cursor-pointer hover:shadow-lg hover:shadow-green-500/20">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-green-300 animate-spin-slow" />
              <p className="text-xs font-bold text-green-200">Data Quality Status</p>
            </div>
            <div className="flex items-center justify-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-500"></div>
              <p className="text-sm font-bold text-green-100 group-hover:text-green-50 transition-colors">98.7% Validated</p>
            </div>
          </div>
        </div>
      </aside>

      <style>{`
        .scrollbar-hide {
          scrollbar-width: none;
          -ms-overflow-style: none;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animate-spin-slow {
          animation: spin 3s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
}
