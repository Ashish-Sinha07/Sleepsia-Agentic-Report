import { formatCurrency, formatPercentage, formatROAS, formatUnits, getChangeIndicator } from '../../utils/formatting';
import { TrendingUp, TrendingDown } from 'lucide-react';

export default function KpiCard({ title, value, previousValue, type = 'currency', icon: Icon }) {
  const changeIndicator = getChangeIndicator(value, previousValue);

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
    <div className="card h-full">
      <div className="card-body">
        <div className="flex items-start justify-between mb-4">
          <div>
            <p className="text-label mb-2">{title}</p>
            <p className="text-value">{getFormattedValue()}</p>
          </div>
          {Icon && (
            <div className="text-sleepsia-600 opacity-50">
              <Icon className="w-8 h-8" />
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          {changeIndicator.direction === 'positive' && (
            <TrendingUp className="w-4 h-4 text-green-600" />
          )}
          {changeIndicator.direction === 'negative' && (
            <TrendingDown className="w-4 h-4 text-red-600" />
          )}
          <span className={`text-sm font-medium ${
            changeIndicator.direction === 'positive' ? 'text-change-positive' :
            changeIndicator.direction === 'negative' ? 'text-change-negative' :
            'text-gray-500'
          }`}>
            {changeIndicator.display}
          </span>
          <span className="text-xs text-gray-500">vs previous</span>
        </div>
      </div>
    </div>
  );
}
