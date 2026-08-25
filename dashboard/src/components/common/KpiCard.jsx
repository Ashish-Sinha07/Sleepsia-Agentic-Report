import { formatCurrency, formatPercentage, formatROAS, formatUnits } from '../../utils/formatting';

export default function KpiCard({ title, value, type = 'currency', icon: Icon, color = 'blue', delay = 0 }) {
  const colorClasses = {
    blue: 'kpi-card-blue',
    green: 'kpi-card-green',
    purple: 'kpi-card-purple',
    orange: 'kpi-card-orange',
  };

  const colorBgClasses = {
    blue: 'from-blue-600 to-cyan-600',
    green: 'from-green-600 to-emerald-600',
    purple: 'from-purple-600 to-pink-600',
    orange: 'from-orange-600 to-amber-600',
  };

  const getFormattedValue = () => {
    switch (type) {
      case 'currency':
        return formatCurrency(value);
      case 'percentage':
        return formatPercentage(value);
      case 'roas':
        return formatROAS(value);
      case 'units':
        return formatUnits(value);
      default:
        return value;
    }
  };

  return (
    <div
      className={`kpi-card-animated ${colorClasses[color]} group relative overflow-visible`}
      style={{ animation: `fadeInUp 0.6s ease-out ${delay}s both` }}
    >
      {/* Animated background glow */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none">
        <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${colorBgClasses[color]} rounded-full filter blur-3xl opacity-20 group-hover:opacity-40 transition-opacity`}></div>
      </div>

      {/* Shiny effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-30 animate-shimmer"></div>

      {/* Icon positioned at top right */}
      {Icon && (
        <div className={`absolute -top-2 -right-2 w-10 h-10 rounded-lg bg-gradient-to-br ${colorBgClasses[color]} flex items-center justify-center opacity-80 group-hover:opacity-100 transform group-hover:scale-110 group-hover:rotate-12 transition-all duration-500 shadow-md`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      )}

      {/* Data content */}
      <div className="relative z-10 pr-4">
        <p className="text-xs font-medium text-gray-600 mb-1 group-hover:text-gray-700 transition-colors">{title}</p>
        <p className="text-lg font-bold text-gray-900 group-hover:text-gray-800 transition-colors leading-tight">
          {getFormattedValue()}
        </p>
      </div>
    </div>
  );
}
