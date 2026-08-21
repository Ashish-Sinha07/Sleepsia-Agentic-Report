import { useContext } from 'react';
import { FilterContext } from '../../context/FilterContext';
import { format } from 'date-fns';
import { ChevronDown, RotateCcw } from 'lucide-react';

const PLATFORMS = ['all', 'Amazon', 'Flipkart', 'Myntra', 'Blinkit', 'JioMart'];

export default function FilterBar() {
  const { filters, updateFilters, resetFilters } = useContext(FilterContext);

  const handleDateChange = (type, value) => {
    updateFilters({ [type]: new Date(value) });
  };

  const handlePlatformChange = (value) => {
    updateFilters({ platform: value });
  };

  return (
    <div className="card mb-6">
      <div className="card-body">
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
                  <option key={platform} value={platform}>
                    {platform === 'all' ? 'All Platforms' : platform}
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
