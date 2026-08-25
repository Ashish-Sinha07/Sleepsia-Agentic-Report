import { useState, createContext, useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import { mainRoutes } from './config/routes';
import { RefreshCw, Download, User, X, MessageSquare, Calendar, Sparkles } from 'lucide-react';

const DateRangeContext = createContext();

const DateRangeProvider = ({ children }) => {
  const [dateRange, setDateRange] = useState({
    start: '2026-07-25',
    end: '2026-08-24',
  });

  return (
    <DateRangeContext.Provider value={{ dateRange, setDateRange }}>
      {children}
    </DateRangeContext.Provider>
  );
};

export const useDateRange = () => useContext(DateRangeContext);

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-64 bg-gradient-to-b from-slate-900 via-blue-900 to-slate-900 shadow-2xl h-screen fixed left-0 top-0 overflow-y-auto backdrop-blur-sm border-r border-blue-400/20">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-10 left-10 w-40 h-40 bg-blue-500/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute bottom-20 right-10 w-40 h-40 bg-cyan-500/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="p-6 relative z-10">
        <div className="flex items-center gap-3 mb-10 group cursor-pointer">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-cyan-400 rounded-lg flex items-center justify-center text-slate-900 font-bold transform group-hover:scale-125 group-hover:rotate-12 transition-all duration-500 shadow-lg shadow-blue-500/50">
            S
          </div>
          <div className="flex-1">
            <h1 className="text-xl font-bold text-white group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-blue-300 group-hover:to-cyan-300 group-hover:bg-clip-text transition-all duration-300">Sleepsia</h1>
            <p className="text-xs text-blue-200/60 group-hover:text-blue-200 transition-colors">Analytics</p>
          </div>
        </div>

        <nav className="space-y-2">
          {mainRoutes.map((route, idx) => {
            const Icon = route.icon;
            const isActive = location.pathname === route.path;

            return (
              <Link
                key={route.path}
                to={route.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 transform hover:translate-x-2 group relative overflow-hidden ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-400/80 to-cyan-400/80 text-slate-900 font-semibold shadow-lg shadow-blue-500/50 backdrop-blur-md border border-blue-300/50'
                    : 'text-blue-100 hover:bg-blue-500/40 hover:shadow-lg backdrop-blur-sm border border-blue-400/10'
                }`}
                style={{
                  animation: `slideInLeft ${0.3 + idx * 0.05}s ease-out`,
                }}
              >
                {/* Ripple effect background */}
                {isActive && <div className="absolute inset-0 bg-white/10 animate-pulse"></div>}

                <Icon className="w-5 h-5 transform group-hover:scale-125 group-hover:rotate-12 transition-all duration-300 relative z-10" />
                <span className="group-hover:font-bold transition-all duration-300 relative z-10">{route.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <style>{`
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
      `}</style>
    </aside>
  );
};

const Header = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const currentRoute = mainRoutes.find((r) => r.path === location.pathname);
  const { dateRange, setDateRange } = useDateRange();

  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState(null);
  const [tempDateRange, setTempDateRange] = useState({ ...dateRange });

  const handleRefresh = () => {
    window.location.reload();
  };

  const generateReport = async () => {
    try {
      setReportLoading(true);
      setReportError(null);

      const response = await fetch('http://localhost:8000/api/reports/comprehensive/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: dateRange.start,
          end_date: dateRange.end,
          report_type: 'executive_summary',
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate report: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Executive_Report_${dateRange.end}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

      setShowReportModal(false);
    } catch (error) {
      setReportError(error.message);
    } finally {
      setReportLoading(false);
    }
  };

  const formatDateDisplay = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const applyDateRange = () => {
    setDateRange(tempDateRange);
    setShowDatePicker(false);
  };

  const resetDateRange = () => {
    setTempDateRange({ ...dateRange });
    setShowDatePicker(false);
  };

  return (
    <>
      <header className="bg-gradient-to-r from-white via-blue-50 to-white shadow-xl border-b-2 border-blue-200 backdrop-blur-sm sticky top-0 z-40">
        <div className="ml-64 px-6 py-5">
          <div className="flex items-center justify-between">
            <div className="group">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-blue-600 group-hover:text-blue-800 transition-colors animate-spin-slow" />
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent group-hover:from-blue-700 group-hover:to-blue-900 transition-all duration-300">
                  {currentRoute?.label || 'Dashboard'}
                </h1>
              </div>
              <p className="text-sm text-gray-600 group-hover:text-gray-800 transition-colors duration-300 mt-1">
                {currentRoute?.description}
              </p>
            </div>

            <div className="flex items-center gap-2">
              {/* Date Range Picker Button */}
              <div className="relative group/date">
                <button
                  onClick={() => setShowDatePicker(!showDatePicker)}
                  className="flex items-center gap-2 px-4 py-2 text-gray-700 bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-50 hover:from-blue-100 hover:via-cyan-100 hover:to-blue-100 rounded-xl transition-all duration-300 border-2 border-blue-200 hover:border-blue-500 hover:shadow-2xl hover:shadow-blue-300/50 transform hover:scale-110 relative overflow-hidden group"
                  title="Select date range"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 animate-shimmer"></span>
                  <Calendar className="w-4 h-4 transition-all duration-300 group-hover:rotate-12 group-hover:scale-125" />
                  <span className="text-sm font-semibold">
                    {formatDateDisplay(dateRange.start)} - {formatDateDisplay(dateRange.end)}
                  </span>
                </button>

                {showDatePicker && (
                  <div className="absolute right-0 mt-3 w-80 bg-gradient-to-br from-white to-blue-50/50 rounded-2xl shadow-2xl shadow-blue-300/40 z-50 border-2 border-blue-300/60 backdrop-blur-sm transform transition-all duration-300 origin-top animate-in fade-in zoom-in-95 slide-in-from-top-4">
                    <div className="p-6">
                      <div className="flex items-center justify-between mb-6">
                        <h3 className="font-bold text-gray-900 text-lg bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">Select Date Range</h3>
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Calendar className="w-4 h-4 text-blue-600" />
                        </div>
                      </div>

                      <div className="space-y-5">
                        <div className="relative">
                          <label className="block text-sm font-bold text-gray-700 mb-2">
                            From Date
                          </label>
                          <input
                            type="date"
                            value={tempDateRange.start}
                            onChange={(e) =>
                              setTempDateRange({
                                ...tempDateRange,
                                start: e.target.value,
                              })
                            }
                            className="w-full px-4 py-3 border-2 border-blue-300/40 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 hover:border-blue-400/80 bg-white/80 backdrop-blur-sm focus:bg-white"
                          />
                        </div>

                        <div className="relative">
                          <label className="block text-sm font-bold text-gray-700 mb-2">
                            To Date
                          </label>
                          <input
                            type="date"
                            value={tempDateRange.end}
                            onChange={(e) =>
                              setTempDateRange({
                                ...tempDateRange,
                                end: e.target.value,
                              })
                            }
                            className="w-full px-4 py-3 border-2 border-blue-300/40 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 hover:border-blue-400/80 bg-white/80 backdrop-blur-sm focus:bg-white"
                          />
                        </div>
                      </div>

                      <div className="mt-8 flex gap-3">
                        <button
                          onClick={applyDateRange}
                          className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 hover:shadow-lg hover:shadow-blue-400/50 transition-all duration-300 font-bold transform hover:scale-105 active:scale-95 relative overflow-hidden group"
                        >
                          <span className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-100 animate-pulse"></span>
                          <span className="relative">✓ Apply</span>
                        </button>
                        <button
                          onClick={resetDateRange}
                          className="flex-1 px-4 py-3 bg-gradient-to-r from-gray-200 to-gray-300 text-gray-700 rounded-xl hover:from-gray-300 hover:to-gray-400 hover:shadow-md transition-all duration-300 font-bold transform hover:scale-105 active:scale-95"
                        >
                          ✕ Cancel
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                className="p-3 text-gray-600 hover:text-blue-600 bg-gradient-to-br from-blue-50 to-cyan-50 hover:from-blue-100 hover:to-cyan-100 rounded-xl transition-all duration-300 transform hover:scale-125 hover:shadow-xl hover:shadow-blue-400/40 group relative border-2 border-blue-200/40 hover:border-blue-400"
                title="Refresh data"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-blue-500 via-cyan-500 to-blue-500 opacity-0 group-hover:opacity-10 rounded-xl animate-pulse"></span>
                <RefreshCw className="w-5 h-5 group-hover:rotate-180 transition-transform duration-700 relative z-10" />
              </button>

              {/* Download Report Button */}
              <button
                onClick={() => setShowReportModal(true)}
                className="p-3 text-gray-600 hover:text-green-600 bg-gradient-to-br from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 rounded-xl transition-all duration-300 transform hover:scale-125 hover:shadow-xl hover:shadow-green-400/40 group relative border-2 border-green-200/40 hover:border-green-400"
                title="Download report"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-green-500 via-emerald-500 to-green-500 opacity-0 group-hover:opacity-10 rounded-xl animate-pulse"></span>
                <Download className="w-5 h-5 group-hover:translate-y-1 group-hover:scale-125 transition-all duration-300 relative z-10" />
              </button>

              {/* Chat / AI Assistant Button */}
              <button
                onClick={() => navigate('/ai-assistant')}
                className="p-3 text-gray-600 hover:text-purple-600 bg-gradient-to-br from-purple-50 to-pink-50 hover:from-purple-100 hover:to-pink-100 rounded-xl transition-all duration-300 transform hover:scale-125 hover:shadow-xl hover:shadow-purple-400/40 group relative border-2 border-purple-200/40 hover:border-purple-400"
                title="AI Business Assistant"
              >
                <span className="absolute inset-0 bg-gradient-to-r from-purple-500 via-pink-500 to-purple-500 opacity-0 group-hover:opacity-10 rounded-xl animate-pulse"></span>
                <MessageSquare className="w-5 h-5 group-hover:scale-125 group-hover:bounce transition-all duration-300 relative z-10" />
              </button>

              {/* Notifications Button */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-3 text-gray-600 hover:text-red-600 bg-gradient-to-br from-red-50 to-orange-50 hover:from-red-100 hover:to-orange-100 rounded-xl transition-all duration-300 transform hover:scale-125 hover:shadow-xl hover:shadow-red-400/40 group relative border-2 border-red-200/40 hover:border-red-400"
                  title="Notifications"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-red-500 via-orange-500 to-red-500 opacity-0 group-hover:opacity-10 rounded-xl animate-pulse"></span>
                  <span className="text-2xl group-hover:scale-125 group-hover:animate-bounce transition-all duration-300 inline-block relative z-10">🔔</span>
                  <span className="absolute top-0 right-0 w-3 h-3 bg-gradient-to-br from-red-500 to-orange-600 rounded-full animate-pulse shadow-lg shadow-red-500/50 ring-2 ring-white"></span>
                </button>

                {showNotifications && (
                  <div className="absolute right-0 mt-3 w-96 bg-gradient-to-br from-white via-red-50/30 to-orange-50/30 rounded-2xl shadow-2xl shadow-red-300/40 z-50 border-2 border-red-300/50 backdrop-blur-sm transform transition-all duration-300 origin-top animate-in fade-in zoom-in-95 slide-in-from-top-4">
                    <div className="p-5 border-b-2 bg-gradient-to-r from-red-50 via-orange-50 to-red-50 rounded-t-2xl">
                      <div className="flex items-center justify-between">
                        <h3 className="font-bold text-gray-900 text-lg">🔔 Notifications</h3>
                        <button onClick={() => setShowNotifications(false)} className="text-gray-400 hover:text-gray-600">✕</button>
                      </div>
                    </div>
                    <div className="p-4 max-h-96 overflow-y-auto space-y-3">
                      {[
                        { icon: '🚨', title: 'Critical Alerts', msg: '3 new critical alerts detected in your warehouse inventory', color: 'red', time: 'Just now' },
                        { icon: '⚠️', title: 'Low Stock Warning', msg: '5 products are below reorder level', color: 'yellow', time: '2 hours ago' },
                        { icon: '📊', title: 'Report Ready', msg: 'Your comprehensive executive report is ready to download', color: 'blue', time: '4 hours ago' },
                        { icon: '✓', title: 'Sales Update', msg: 'Excellent sales performance on Amazon platform', color: 'green', time: '1 day ago' }
                      ].map((notif, idx) => (
                        <div key={idx} className={`p-4 bg-${notif.color}-50/80 rounded-xl border-l-4 border-${notif.color}-500 hover:shadow-lg hover:scale-105 transition-all duration-300 cursor-pointer transform backdrop-blur-sm hover:bg-${notif.color}-100/50 relative overflow-hidden group`}>
                          <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-10 rounded-xl"></div>
                          <p className="font-bold text-sm text-gray-900 relative z-10">{notif.icon} {notif.title}</p>
                          <p className="text-xs text-gray-600 mt-2 relative z-10">
                            {notif.msg}
                          </p>
                          <p className={`text-xs text-${notif.color}-600 mt-2 font-semibold relative z-10`}>{notif.time}</p>
                        </div>
                      ))}
                    </div>
                    <button
                      onClick={() => setShowNotifications(false)}
                      className="w-full p-4 text-sm text-blue-600 font-bold hover:bg-blue-50/80 border-t-2 border-gray-200 transition-all duration-300 rounded-b-2xl"
                    >
                      → View All Notifications
                    </button>
                  </div>
                )}
              </div>

              {/* Profile Menu */}
              <div className="relative">
                <button
                  onClick={() => setShowProfileMenu(!showProfileMenu)}
                  className="p-3 text-gray-600 hover:text-orange-600 bg-gradient-to-br from-orange-50 to-amber-50 hover:from-orange-100 hover:to-amber-100 rounded-xl transition-all duration-300 transform hover:scale-125 hover:shadow-xl hover:shadow-orange-400/40 group relative border-2 border-orange-200/40 hover:border-orange-400"
                  title="Profile"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-orange-500 via-amber-500 to-orange-500 opacity-0 group-hover:opacity-10 rounded-xl animate-pulse"></span>
                  <User className="w-5 h-5 group-hover:scale-125 group-hover:-rotate-12 transition-all duration-300 relative z-10" />
                </button>

                {showProfileMenu && (
                  <div className="absolute right-0 mt-3 w-64 bg-gradient-to-br from-white via-orange-50/30 to-amber-50/30 rounded-2xl shadow-2xl shadow-orange-300/40 z-50 border-2 border-orange-300/50 backdrop-blur-sm transform transition-all duration-300 origin-top animate-in fade-in zoom-in-95 slide-in-from-top-4">
                    <div className="p-5 bg-gradient-to-r from-orange-100/80 to-amber-100/80 rounded-t-2xl border-b-2 border-orange-200/50 backdrop-blur-sm">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-amber-500 flex items-center justify-center text-white font-bold">A</div>
                        <div>
                          <p className="font-bold text-gray-900">Ashish Sinha</p>
                          <p className="text-xs text-gray-600">ashish.sinha@agileventures.net</p>
                        </div>
                      </div>
                    </div>
                    <div className="py-3 space-y-1">
                      {[
                        { icon: '⚙️', label: 'Settings', color: 'orange' },
                        { icon: '❓', label: 'Help & Support', color: 'blue' },
                        { icon: '🚪', label: 'Logout', color: 'red' }
                      ].map((item, idx) => (
                        <button key={idx} className={`w-full text-left px-5 py-3 text-sm text-gray-700 hover:bg-${item.color}-50/80 transition-all duration-300 hover:translate-x-2 font-medium backdrop-blur-sm group relative overflow-hidden`}>
                          <span className={`absolute inset-0 bg-gradient-to-r from-${item.color}-400/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity`}></span>
                          <span className="relative z-10">{item.icon} {item.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Report Generation Modal */}
      {showReportModal && (
        <div className="fixed inset-0 bg-gradient-to-br from-black/40 via-black/50 to-black/40 backdrop-blur-lg flex items-center justify-center z-50 animate-in fade-in duration-300">
          <div className="bg-gradient-to-br from-white via-blue-50/50 to-cyan-50/50 rounded-3xl shadow-2xl shadow-blue-500/30 max-w-md w-full mx-4 transform transition-all duration-300 animate-in slide-in-from-bottom-8 border-2 border-blue-200/50 backdrop-blur-md">
            <div className="flex items-center justify-between p-6 border-b-2 border-blue-200/50 bg-gradient-to-r from-blue-50/80 via-cyan-50/80 to-blue-50/80 rounded-t-3xl">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <span className="text-white font-bold text-sm">📄</span>
                </div>
                <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">Generate Report</h2>
              </div>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-gray-600 hover:text-red-600 hover:bg-red-100/80 rounded-lg p-2 transition-all duration-300 transform hover:scale-125 hover:rotate-90 group relative border border-red-200/40 hover:border-red-400"
              >
                <span className="absolute inset-0 bg-red-500/10 rounded-lg opacity-0 group-hover:opacity-100"></span>
                <X className="w-5 h-5 relative z-10" />
              </button>
            </div>

            <div className="p-8">
              {reportError && (
                <div className="mb-6 p-4 bg-gradient-to-br from-red-50 to-orange-50 rounded-xl text-red-700 text-sm border-2 border-red-300/50 animate-in shake duration-500 font-semibold">
                  <span className="text-lg">⚠️</span> {reportError}
                </div>
              )}

              <div className="mb-8 p-5 bg-gradient-to-br from-blue-100/60 via-cyan-100/40 to-blue-100/60 rounded-2xl border-2 border-blue-300/60 backdrop-blur-sm hover:shadow-lg hover:border-blue-400 transition-all duration-300">
                <div className="flex items-center gap-2 mb-3">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <p className="text-sm font-bold text-gray-800">
                    Date Range
                  </p>
                </div>
                <p className="text-lg font-bold text-blue-700 mb-2">
                  {formatDateDisplay(dateRange.start)} → {formatDateDisplay(dateRange.end)}
                </p>
                <p className="text-xs text-gray-700 leading-relaxed">
                  📊 Report will include comprehensive metrics, insights, and analysis for the selected period.
                </p>
              </div>

              <div className="space-y-3">
                <button
                  onClick={() => generateReport()}
                  disabled={reportLoading}
                  className="w-full px-6 py-4 bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-600 text-white rounded-xl hover:from-blue-700 hover:via-cyan-700 hover:to-blue-700 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-400 hover:shadow-xl hover:shadow-blue-500/50 transition-all duration-300 font-bold flex items-center justify-center gap-3 transform hover:scale-105 active:scale-95 group relative overflow-hidden"
                >
                  <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 animate-shimmer"></span>
                  <span className="relative z-10 flex items-center gap-2">
                    {reportLoading ? (
                      <>
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Download className="w-5 h-5 group-hover:translate-y-1 transition-transform" />
                        Download as PDF
                      </>
                    )}
                  </span>
                </button>

                <button
                  onClick={() => setShowReportModal(false)}
                  className="w-full px-6 py-4 bg-gradient-to-r from-gray-200/80 via-gray-300/80 to-gray-200/80 text-gray-800 rounded-xl hover:from-gray-300 hover:via-gray-400 hover:to-gray-300 hover:shadow-lg transition-all duration-300 font-bold transform hover:scale-105 active:scale-95 group relative border-2 border-gray-300/40 hover:border-gray-500"
                >
                  <span className="absolute inset-0 bg-white/20 opacity-0 group-hover:opacity-30 rounded-xl"></span>
                  <span className="relative z-10">✕ Cancel</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
        }
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
      `}</style>
    </>
  );
};

const App = () => {
  return (
    <DateRangeProvider>
      <Router>
        <div className="flex">
          <Sidebar />
          <div className="flex-1 ml-64">
            <Header />
            <main className="bg-gray-50 min-h-screen">
              <Routes>
                {mainRoutes.map((route) => (
                  <Route
                    key={route.path}
                    path={route.path}
                    element={<route.component />}
                  />
                ))}
                <Route path="*" element={<div className="p-6">Page not found</div>} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </DateRangeProvider>
  );
};

export default App;
