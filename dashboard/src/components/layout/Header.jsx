import { useContext, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, MessageCircle, User, Calendar, Menu, Zap, TrendingUp, Sparkles } from 'lucide-react';
import { FilterContext } from '../../context/FilterContext';
import { analyticsApi } from '../../services/analyticsApi';
import { format } from 'date-fns';

export default function Header({ onMenuClick = () => {} }) {
  const { filters } = useContext(FilterContext);
  const navigate = useNavigate();
  const [alertCount, setAlertCount] = useState(0);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileRef = useRef(null);

  useEffect(() => {
    let active = true;
    analyticsApi
      .getAlerts(filters)
      .then((alerts) => {
        if (!active) return;
        setAlertCount((alerts?.critical || 0) + (alerts?.high || 0));
      })
      .catch(() => {
        if (active) setAlertCount(0);
      });
    return () => {
      active = false;
    };
  }, [filters]);

  useEffect(() => {
    const closeOnOutsideClick = (event) => {
      if (profileRef.current && !profileRef.current.contains(event.target)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', closeOnOutsideClick);
    return () => document.removeEventListener('mousedown', closeOnOutsideClick);
  }, []);

  return (
    <header className="bg-gradient-to-r from-white via-blue-50 to-white border-b-2 border-blue-200/50 shadow-lg sticky top-0 z-40 backdrop-blur-sm">
      <div className="px-4 sm:px-8 py-4 flex items-center justify-between gap-4">

        {/* Left Section - Logo & Title */}
        <div className="flex items-center gap-3 min-w-0">
          {/* Mobile Menu Button */}
          <button
            onClick={onMenuClick}
            className="lg:hidden -ml-1 min-w-[48px] min-h-[48px] flex items-center justify-center text-gray-600 hover:text-blue-600 hover:bg-blue-100/50 rounded-lg transition-all duration-300 transform hover:scale-110 group"
            aria-label="Open menu"
          >
            <Menu className="w-5 h-5 group-hover:rotate-90 transition-transform duration-300" />
          </button>

          {/* Logo - Clickable */}
          <button
            onClick={() => navigate('/')}
            className="w-11 h-11 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0 shadow-lg shadow-blue-500/50 group transform hover:scale-110 hover:rotate-12 transition-all duration-500 cursor-pointer"
            title="Go to Executive Dashboard"
          >
            <span className="text-white font-bold text-lg">S</span>
          </button>

          {/* Title - Clickable */}
          <button
            onClick={() => navigate('/')}
            className="min-w-0 hidden sm:block group cursor-pointer text-left"
            title="Go to Executive Dashboard"
          >
            <h1 className="text-base font-bold bg-gradient-to-r from-blue-700 to-blue-900 bg-clip-text text-transparent group-hover:from-blue-800 group-hover:to-blue-900 transition-all duration-300 truncate flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600 group-hover:animate-spin-slow" />
              Sleepsia Analytics
            </h1>
            <p className="text-xs text-gray-600 group-hover:text-gray-800 transition-colors truncate">Business Intelligence Dashboard</p>
          </button>
        </div>

        {/* Center Section - Date & Range */}
        <div className="flex items-center gap-4 sm:gap-8">
          {/* Data Updated */}
          <div className="text-right text-sm hidden lg:block group">
            <p className="text-gray-600 group-hover:text-gray-800 transition-colors text-xs font-medium">Data Updated</p>
            <p className="text-gray-900 font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent group-hover:from-gray-800 group-hover:to-gray-600 transition-all">21 Aug 2026, 2:35 PM</p>
          </div>

          {/* Date Range */}
          <div className="flex items-center gap-2 text-gray-700 hidden md:flex bg-gradient-to-r from-blue-50 to-cyan-50 px-4 py-2 rounded-lg border border-blue-200/50 hover:border-blue-400 transition-all duration-300 group">
            <Calendar className="w-4 h-4 text-blue-600 group-hover:scale-125 group-hover:rotate-12 transition-all duration-300" />
            <span className="text-sm font-medium group-hover:text-gray-900 transition-colors">{format(filters.startDate, 'dd MMM')} - {format(filters.endDate, 'dd MMM')}</span>
          </div>
        </div>

        {/* Right Section - Action Buttons */}
        <div className="flex items-center gap-2 sm:gap-4 border-l border-blue-200/50 pl-2 sm:pl-4">

          {/* Alerts Button */}
          <button
            onClick={() => navigate('/alerts')}
            title={alertCount > 0 ? `${alertCount} active critical/high alerts` : 'No active alerts'}
            className={`relative p-3 rounded-lg transition-all duration-300 transform hover:scale-110 group ${
              alertCount > 0
                ? 'text-red-600 bg-red-50/50 hover:bg-red-100 hover:shadow-lg hover:shadow-red-200'
                : 'text-gray-600 bg-gray-50/50 hover:bg-blue-100 hover:text-blue-600 hover:shadow-lg hover:shadow-blue-200'
            }`}
          >
            <Bell className="w-5 h-5 group-hover:rotate-12 transition-transform duration-300" />
            {alertCount > 0 && (
              <span className="absolute top-1 right-1 w-3 h-3 bg-gradient-to-br from-red-500 to-rose-600 rounded-full animate-pulse shadow-lg shadow-red-500/50 border border-white"></span>
            )}
          </button>

          {/* AI Assistant Button */}
          <button
            onClick={() => navigate('/assistant')}
            title="AI Business Assistant"
            className="p-3 text-purple-600 bg-purple-50/50 hover:bg-purple-100 rounded-lg transition-all duration-300 transform hover:scale-110 hover:shadow-lg hover:shadow-purple-200 group"
          >
            <MessageCircle className="w-5 h-5 group-hover:scale-125 group-hover:bounce transition-all duration-300" />
          </button>

          {/* Profile Menu */}
          <div className="relative" ref={profileRef}>
            <button
              onClick={() => setProfileOpen((open) => !open)}
              title="Account"
              className="p-3 text-orange-600 bg-orange-50/50 hover:bg-orange-100 rounded-lg transition-all duration-300 transform hover:scale-110 hover:shadow-lg hover:shadow-orange-200 group"
            >
              <User className="w-5 h-5 group-hover:scale-125 group-hover:-rotate-12 transition-all duration-300" />
            </button>

            {/* Profile Dropdown */}
            {profileOpen && (
              <div className="absolute right-0 mt-3 w-64 bg-gradient-to-br from-white via-blue-50/50 to-white border-2 border-blue-200/50 rounded-xl shadow-2xl shadow-blue-300/30 z-50 backdrop-blur-sm overflow-hidden transform transition-all duration-300 animate-in fade-in zoom-in-95 slide-in-from-top-2 origin-top-right">
                {/* Profile Header */}
                <div className="px-5 py-4 bg-gradient-to-r from-orange-50 to-amber-50 border-b border-blue-200/50">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-amber-500 flex items-center justify-center text-white font-bold shadow-lg">
                      A
                    </div>
                    <div>
                      <p className="text-sm font-bold text-gray-900">Admin User</p>
                      <p className="text-xs text-gray-600">Sleepsia Analytics</p>
                    </div>
                  </div>
                </div>

                {/* Menu Items */}
                <div className="py-2">
                  <button
                    onClick={() => {
                      setProfileOpen(false);
                      navigate('/reports');
                    }}
                    className="w-full text-left px-5 py-3 text-sm text-gray-700 hover:bg-blue-50/80 transition-all duration-300 flex items-center gap-3 group font-medium"
                  >
                    <TrendingUp className="w-4 h-4 text-blue-600 group-hover:scale-125 transition-transform" />
                    <span className="group-hover:text-gray-900 transition-colors">My Reports</span>
                  </button>
                  <button
                    onClick={() => {
                      setProfileOpen(false);
                    }}
                    className="w-full text-left px-5 py-3 text-sm text-gray-700 hover:bg-purple-50/80 transition-all duration-300 flex items-center gap-3 group font-medium border-t border-blue-200/30"
                  >
                    <Zap className="w-4 h-4 text-purple-600 group-hover:scale-125 transition-transform" />
                    <span className="group-hover:text-gray-900 transition-colors">Settings</span>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
      `}</style>
    </header>
  );
}
