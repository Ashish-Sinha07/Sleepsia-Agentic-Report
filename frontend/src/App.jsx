import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { mainRoutes } from './config/routes';
import { RefreshCw, Download, User, X } from 'lucide-react';

const Sidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-64 bg-white shadow-lg h-screen fixed left-0 top-0 overflow-y-auto">
      <div className="p-6">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold">
            S
          </div>
          <h1 className="text-xl font-bold">Sleepsia</h1>
        </div>

        <nav className="space-y-2">
          {mainRoutes.map((route) => {
            const Icon = route.icon;
            const isActive = location.pathname === route.path;

            return (
              <Link
                key={route.path}
                to={route.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-600 font-semibold'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{route.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </aside>
  );
};

const Header = () => {
  const location = useLocation();
  const currentRoute = mainRoutes.find((r) => r.path === location.pathname);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [reportError, setReportError] = useState(null);

  const handleRefresh = () => {
    window.location.reload();
  };

  const generateReport = async () => {
    try {
      setReportLoading(true);
      setReportError(null);

      const today = new Date();
      const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

      const startDate = thirtyDaysAgo.toISOString().split('T')[0];
      const endDate = today.toISOString().split('T')[0];

      const response = await fetch('http://localhost:8000/api/reports/comprehensive/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate,
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
      link.setAttribute('download', `Executive_Report_${endDate}.pdf`);
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

  return (
    <>
      <header className="bg-white shadow-sm border-b">
        <div className="ml-64 px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {currentRoute?.label || 'Dashboard'}
              </h1>
              <p className="text-sm text-gray-600">
                {currentRoute?.description}
              </p>
            </div>
            <div className="flex items-center gap-4">
              {/* Refresh Button */}
              <button
                onClick={handleRefresh}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Refresh data"
              >
                <RefreshCw className="w-5 h-5" />
              </button>

              {/* Download Report Button */}
              <button
                onClick={() => setShowReportModal(true)}
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                title="Download report"
              >
                <Download className="w-5 h-5" />
              </button>

              {/* Notifications Button */}
              <div className="relative">
                <button
                  onClick={() => setShowNotifications(!showNotifications)}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors relative"
                  title="Notifications"
                >
                  <span className="text-2xl">🔔</span>
                  <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

                {showNotifications && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl z-50">
                    <div className="p-4 border-b">
                      <h3 className="font-semibold text-gray-900">Notifications</h3>
                    </div>
                    <div className="p-4 max-h-96 overflow-y-auto">
                      <div className="space-y-3">
                        <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                          <p className="font-medium text-sm text-gray-900">New Alerts Available</p>
                          <p className="text-xs text-gray-600 mt-1">3 new critical alerts detected</p>
                        </div>
                        <div className="p-3 bg-yellow-50 rounded-lg border-l-4 border-yellow-500">
                          <p className="font-medium text-sm text-gray-900">Low Stock Warning</p>
                          <p className="text-xs text-gray-600 mt-1">5 products are below reorder level</p>
                        </div>
                        <div className="p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                          <p className="font-medium text-sm text-gray-900">Report Generated</p>
                          <p className="text-xs text-gray-600 mt-1">Your executive report is ready to download</p>
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowNotifications(false)}
                      className="w-full p-3 text-sm text-blue-600 font-medium hover:bg-gray-50"
                    >
                      View All Notifications
                    </button>
                  </div>
                )}
              </div>

              {/* Profile Menu */}
              <div className="relative">
                <button
                  onClick={() => setShowProfileMenu(!showProfileMenu)}
                  className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                  title="Profile"
                >
                  <User className="w-5 h-5" />
                </button>

                {showProfileMenu && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl z-50">
                    <div className="p-4">
                      <p className="font-semibold text-gray-900">Ashish Sinha</p>
                      <p className="text-sm text-gray-600">ashish.sinha@agileventures.net</p>
                    </div>
                    <div className="border-t">
                      <button className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50">
                        Settings
                      </button>
                      <button className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50">
                        Help & Support
                      </button>
                      <button className="w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50 border-t">
                        Logout
                      </button>
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
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-bold text-gray-900">Generate Report</h2>
              <button
                onClick={() => setShowReportModal(false)}
                className="text-gray-600 hover:text-gray-900"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6">
              {reportError && (
                <div className="mb-4 p-3 bg-red-50 rounded-lg text-red-700 text-sm">
                  {reportError}
                </div>
              )}

              <p className="text-gray-700 text-sm mb-6">
                Generate an executive summary report for the last 30 days.
              </p>

              <div className="space-y-3">
                <button
                  onClick={() => generateReport()}
                  disabled={reportLoading}
                  className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition-colors font-medium flex items-center justify-center gap-2"
                >
                  {reportLoading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download className="w-4 h-4" />
                      Download as PDF
                    </>
                  )}
                </button>

                <button
                  onClick={() => setShowReportModal(false)}
                  className="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

const App = () => {
  return (
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
  );
};

export default App;
