import { useContext } from 'react';
import { FilterContext } from '../../context/FilterContext';
import { format, subDays, startOfMonth, endOfMonth, startOfDay, endOfDay, isSameDay } from 'date-fns';
import { ChevronDown, RotateCcw } from 'lucide-react';

// value must match the platform_id codes seeded in the platforms table (sql/schema.sql)
export const PLATFORMS = [
  { id: 'all', label: 'All Platforms' },
  { id: 'AMZ', label: 'Amazon' },
  { id: 'FLP', label: 'Flipkart' },
  { id: 'MTR', label: 'Myntra' },
  { id: 'BLK', label: 'Blinkit' },
  { id: 'JMT', label: 'JioMart' },
];

const DATE_PRESETS = [
  { label: '7D', range: () => ({ startDate: startOfDay(subDays(new Date(), 6)), endDate: endOfDay(new Date()) }) },
  { label: '30D', range: () => ({ startDate: startOfDay(subDays(new Date(), 29)), endDate: endOfDay(new Date()) }) },
  { label: 'This month', range: () => ({ startDate: startOfDay(startOfMonth(new Date())), endDate: endOfDay(new Date()) }) },
  {
    label: 'Last month',
    range: () => {
      const lastMonthEnd = endOfDay(subDays(startOfMonth(new Date()), 1));
      return { startDate: startOfDay(startOfMonth(lastMonthEnd)), endDate: lastMonthEnd };
    },
  },
];

export default function FilterBar() {
  const { filters, updateFilters, resetFilters } = useContext(FilterContext);

  const handleDateChange = (type, value) => {
    updateFilters({ [type]: new Date(value) });
  };

  const handlePlatformChange = (value) => {
    updateFilters({ platform: value });
  };

  const applyPreset = (preset) => updateFilters(preset.range());

  const isActivePreset = (preset) => {
    const { startDate, endDate } = preset.range();
    return isSameDay(startDate, filters.startDate) && isSameDay(endDate, filters.endDate);
  };

  return (
    <div className="card mb-6">
      <div className="card-body space-y-4">
        <div className="flex items-center gap-2 flex-wrap">
          {DATE_PRESETS.map((preset) => (
            <button
              key={preset.label}
              onClick={() => applyPreset(preset)}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                isActivePreset(preset)
                  ? 'bg-sleepsia-600 text-white border-sleepsia-600'
                  : 'bg-white text-gray-600 border-gray-300 hover:border-sleepsia-400 hover:text-sleepsia-600'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>

        <div className="flex items-end gap-4 flex-wrap">
          <div className="flex-1 min-w-max">
            <label className="text-label block mb-2">From Date</label>
            <input
              type="date"
              value={format(filters.startDate, 'yyyy-MM-dd')}
              onChange={(e) => handleDateChange('startDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sleepsia-500"
            />
          </div>

          <div className="flex-1 min-w-max">
            <label className="text-label block mb-2">To Date</label>
            <input
              type="date"
              value={format(filters.endDate, 'yyyy-MM-dd')}
              onChange={(e) => handleDateChange('endDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sleepsia-500"
            />
          </div>

          <div className="flex-1 min-w-max">
            <label className="text-label block mb-2">Platform</label>
            <div className="relative">
              <select
                value={filters.platform}
                onChange={(e) => handlePlatformChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-sleepsia-500 appearance-none"
              >
                {PLATFORMS.map((platform) => (
                  <option key={platform.id} value={platform.id}>
                    {platform.label}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-gray-500 pointer-events-none" />
            </div>
          </div>

          <button
            onClick={resetFilters}
            className="btn-secondary flex items-center gap-2"
          >
            <RotateCcw className="w-4 h-4" />
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
