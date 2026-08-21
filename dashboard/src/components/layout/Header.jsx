import { useContext } from 'react';
import { Bell, MessageCircle, User, Calendar } from 'lucide-react';
import { FilterContext } from '../../context/FilterContext';
import { format } from 'date-fns';

export default function Header() {
  const { filters } = useContext(FilterContext);

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
      <div className="px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-sleepsia-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">S</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Sleepsia Analytics</h1>
            <p className="text-xs text-gray-500">Business Intelligence Dashboard</p>
          </div>
        </div>

        <div className="flex items-center gap-8">
          <div className="text-right text-sm">
            <p className="text-gray-600">Data Updated</p>
            <p className="text-gray-900 font-medium">21 Aug 2026, 2:35 PM</p>
          </div>

          <div className="flex items-center gap-2 text-gray-600">
            <Calendar className="w-4 h-4" />
            <span className="text-sm">{format(filters.startDate, 'dd MMM')} - {format(filters.endDate, 'dd MMM')}</span>
          </div>

          <div className="flex items-center gap-4 border-l border-gray-200 pl-4">
            <button className="relative p-2 text-gray-600 hover:text-sleepsia-600 hover:bg-gray-100 rounded-lg transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <button className="p-2 text-gray-600 hover:text-sleepsia-600 hover:bg-gray-100 rounded-lg transition-colors">
              <MessageCircle className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-600 hover:text-sleepsia-600 hover:bg-gray-100 rounded-lg transition-colors">
              <User className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
