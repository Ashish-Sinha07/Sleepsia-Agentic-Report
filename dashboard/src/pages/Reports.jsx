import { useContext, useState } from 'react';
import { PLATFORMS } from '../components/filters/FilterBar';
import { Download, FileText, ChevronDown, RotateCcw, Mail, BarChart3, TrendingUp, Zap, Package, Warehouse, Sparkles, CheckCircle } from 'lucide-react';
import { FilterContext } from '../context/FilterContext';
import { useToast } from '../context/ToastContext';
import apiClient from '../services/api';
import { format } from 'date-fns';

export default function Reports() {
  const { filters, updateFilters, resetFilters } = useContext(FilterContext);
  const toast = useToast();
  const [reportType, setReportType] = useState('management-summary');
  const [reportFormat, setFormat] = useState('pdf');
  const [generating, setGenerating] = useState(false);
  const [emailTo, setEmailTo] = useState('');
  const [emailing, setEmailing] = useState(false);

  const reportTypes = [
    { id: 'management-summary', label: 'Management Summary', description: 'Executive summary with key metrics', icon: BarChart3, color: 'from-blue-500 to-cyan-500', bgColor: 'from-blue-50 to-cyan-50' },
    { id: 'platform-report', label: 'Platform Report', description: 'Detailed platform performance analysis', icon: TrendingUp, color: 'from-purple-500 to-pink-500', bgColor: 'from-purple-50 to-pink-50' },
    { id: 'product-report', label: 'Product Report', description: 'Product-wise performance breakdown', icon: Package, color: 'from-green-500 to-emerald-500', bgColor: 'from-green-50 to-emerald-50' },
    { id: 'profitability-report', label: 'Profitability Report', description: 'Profitability and cost analysis', icon: Zap, color: 'from-orange-500 to-red-500', bgColor: 'from-orange-50 to-red-50' },
    { id: 'inventory-report', label: 'Inventory Report', description: 'Warehouse and inventory status', icon: Warehouse, color: 'from-indigo-500 to-blue-500', bgColor: 'from-indigo-50 to-blue-50' },
  ];

  // Must match ReportService.REPORT_TYPES keys in backend/app/services/report_service.py
  const REPORT_TYPE_MAP = {
    'management-summary': 'executive_summary',
    'platform-report': 'platform_analysis',
    'product-report': 'product_analysis',
    'profitability-report': 'profitability',
    'inventory-report': 'inventory',
  };

  const generateReport = () =>
    apiClient.post('/api/reports', {
      report_type: REPORT_TYPE_MAP[reportType],
      start_date: filters.startDate.toISOString().slice(0, 10),
      end_date: filters.endDate.toISOString().slice(0, 10),
      format: reportFormat,
      platform_filter: filters.platform !== 'all' ? filters.platform : null,
    });

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      const response = await generateReport();

      const reportFile = await apiClient.get(`/api/reports/${response.report_id}/download`, {
        params: { format: reportFormat },
        responseType: 'blob',
      });
      const downloadUrl = URL.createObjectURL(reportFile);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${response.report_id}.${response.format || reportFormat}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(downloadUrl);
      toast.success(`Report ${response.report_id} generated successfully.`);
    } catch (err) {
      const errorMessage = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Failed to generate report';
      toast.error(errorMessage);
      console.error('Report generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleEmailReport = async () => {
    if (!emailTo.trim()) {
      toast.error('Enter a recipient email address.');
      return;
    }
    setEmailing(true);
    try {
      // Generate a fresh report for the currently selected type/dates/platform/format
      // so the emailed file always matches what's configured above.
      const response = await generateReport();
      const emailResponse = await apiClient.post(
        `/api/reports/${response.report_id}/email`,
        null,
        { params: { email_to: emailTo.trim(), format: reportFormat } }
      );
      if (emailResponse?.success === false) {
        throw new Error(emailResponse.error || 'Failed to send email');
      }
      toast.success(`Report emailed to ${emailTo.trim()}.`);
    } catch (err) {
      const errorMessage = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Failed to email report';
      toast.error(errorMessage);
      console.error('Report email error:', err);
    } finally {
      setEmailing(false);
    }
  };

  const handleDateChange = (type, value) => {
    updateFilters({ [type]: new Date(value) });
  };

  return (
    <div className="space-y-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 min-h-screen p-0 -m-6 p-6">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none -z-10">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 left-10 w-80 h-80 bg-purple-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      {/* Header Section */}
      <div className="group relative z-10">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-1 h-10 bg-gradient-to-b from-blue-600 to-cyan-600 rounded-full"></div>
          <div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-blue-700 via-cyan-600 to-blue-800 bg-clip-text text-transparent group-hover:from-blue-800 group-hover:via-cyan-700 group-hover:to-blue-900 transition-all duration-300">
              Reports & Downloads
            </h1>
            <p className="text-sm text-gray-700 font-medium mt-2">📊 Generate comprehensive business reports in multiple formats</p>
          </div>
        </div>
      </div>

      {/* Report Type Selection */}
      <div className="relative z-10">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-blue-600" />
          Select Report Type
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
          {reportTypes.map((report, idx) => {
            const Icon = report.icon;
            return (
              <button
                key={report.id}
                onClick={() => setReportType(report.id)}
                className={`p-6 rounded-2xl border-2 cursor-pointer transition-all duration-300 transform group text-left relative overflow-hidden ${
                  reportType === report.id
                    ? `bg-gradient-to-br ${report.bgColor} border-blue-400 shadow-xl shadow-blue-300/40 scale-105 hover:scale-105`
                    : `bg-white border-gray-200 hover:border-blue-400 hover:shadow-lg hover:shadow-blue-200/50 hover:scale-102`
                }`}
                style={{
                  animation: `fadeInUp 0.6s ease-out ${idx * 0.1}s both`,
                }}
              >
                {/* Active indicator */}
                {reportType === report.id && (
                  <div className="absolute top-3 right-3">
                    <CheckCircle className="w-6 h-6 text-blue-600 animate-pulse" />
                  </div>
                )}

                <div className="flex items-start gap-4">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${report.color} flex items-center justify-center shadow-lg text-white transform group-hover:scale-125 group-hover:rotate-12 transition-all duration-300`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <p className="font-bold text-gray-900 group-hover:text-gray-800 transition-colors">{report.label}</p>
                    <p className="text-sm text-gray-600 mt-2 group-hover:text-gray-700 transition-colors">{report.description}</p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Configuration Card */}
      <div className="bg-gradient-to-br from-white via-blue-50/50 to-white rounded-3xl shadow-2xl shadow-blue-300/30 border-2 border-blue-200/50 overflow-hidden relative z-10 backdrop-blur-sm group animate-fade-in-up">
        {/* Header */}
        <div className="px-8 py-6 bg-gradient-to-r from-blue-50/80 to-cyan-50/80 border-b-2 border-blue-200/50 backdrop-blur-sm">
          <h3 className="text-lg font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent flex items-center gap-3">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            Report Configuration
          </h3>
        </div>

        {/* Body */}
        <div className="p-8 space-y-8">
          {/* Report Type Display */}
          <div className="p-5 bg-gradient-to-br from-blue-100/40 to-cyan-100/40 rounded-2xl border-2 border-blue-200/50 hover:border-blue-400 transition-all duration-300">
            <p className="text-xs font-bold text-blue-600 mb-2 uppercase tracking-wide">Selected Report Type</p>
            <p className="text-lg font-bold text-gray-900">
              {reportTypes.find(r => r.id === reportType)?.label}
            </p>
          </div>

          {/* Filter Section */}
          <div>
            <h4 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-orange-600" />
              Generate For
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* From Date */}
              <div className="relative group/input">
                <label className="block text-sm font-bold text-gray-700 mb-2">From Date</label>
                <input
                  type="date"
                  value={format(filters.startDate, 'yyyy-MM-dd')}
                  onChange={(e) => handleDateChange('startDate', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-blue-300/40 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 hover:border-blue-400/80 bg-white/80 backdrop-blur-sm focus:bg-white group-hover/input:border-blue-400"
                />
              </div>

              {/* To Date */}
              <div className="relative group/input">
                <label className="block text-sm font-bold text-gray-700 mb-2">To Date</label>
                <input
                  type="date"
                  value={format(filters.endDate, 'yyyy-MM-dd')}
                  onChange={(e) => handleDateChange('endDate', e.target.value)}
                  className="w-full px-4 py-3 border-2 border-blue-300/40 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 hover:border-blue-400/80 bg-white/80 backdrop-blur-sm focus:bg-white group-hover/input:border-blue-400"
                />
              </div>

              {/* Platform */}
              <div className="relative group/input">
                <label className="block text-sm font-bold text-gray-700 mb-2">Platform</label>
                <div className="relative">
                  <select
                    value={filters.platform}
                    onChange={(e) => updateFilters({ platform: e.target.value })}
                    className="w-full px-4 py-3 border-2 border-blue-300/40 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none transition-all duration-300 hover:border-blue-400/80 bg-white/80 backdrop-blur-sm focus:bg-white group-hover/input:border-blue-400"
                  >
                    {PLATFORMS.map((platform) => (
                      <option key={platform.id} value={platform.id}>
                        {platform.label}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-4 top-3.5 w-4 h-4 text-gray-600 pointer-events-none" />
                </div>
              </div>

              {/* Format */}
              <div className="relative group/input">
                <label className="block text-sm font-bold text-gray-700 mb-2">Format</label>
                <select
                  value={reportFormat}
                  onChange={(e) => setFormat(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-blue-300/40 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 hover:border-blue-400/80 bg-white/80 backdrop-blur-sm focus:bg-white group-hover/input:border-blue-400"
                >
                  <option value="pdf">📄 PDF</option>
                  <option value="json">📋 JSON</option>
                  <option value="excel">📊 Excel</option>
                </select>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 flex-wrap">
            <button
              onClick={handleGenerateReport}
              disabled={generating}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl hover:from-blue-700 hover:to-cyan-700 hover:shadow-xl hover:shadow-blue-500/50 disabled:from-gray-400 disabled:to-gray-500 transition-all duration-300 font-bold flex items-center justify-center gap-3 transform hover:scale-105 active:scale-95 relative overflow-hidden group min-w-[200px]"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent opacity-0 group-hover:opacity-20 animate-shimmer"></span>
              <span className="relative z-10 flex items-center gap-2">
                {generating ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Generating...
                  </>
                ) : (
                  <>
                    <Download className="w-5 h-5" />
                    Generate Report
                  </>
                )}
              </span>
            </button>

            <button
              onClick={resetFilters}
              className="px-8 py-4 bg-gradient-to-r from-gray-200/80 to-gray-300/80 text-gray-800 rounded-xl hover:from-gray-300 hover:to-gray-400 hover:shadow-lg transition-all duration-300 font-bold flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95"
            >
              <RotateCcw className="w-5 h-5" />
              Reset
            </button>
          </div>

          {/* Email Section */}
          <div className="border-t-2 border-blue-200/50 pt-8">
            <h4 className="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Mail className="w-5 h-5 text-purple-600" />
              Email Report
            </h4>
            <div className="flex gap-4 flex-wrap items-end">
              <div className="flex-1 min-w-[240px] group/input">
                <label className="block text-sm font-bold text-gray-700 mb-2">Recipient Email</label>
                <input
                  type="email"
                  value={emailTo}
                  onChange={(e) => setEmailTo(e.target.value)}
                  placeholder="recipient@example.com"
                  className="w-full px-4 py-3 border-2 border-purple-300/40 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-300 hover:border-purple-400/80 bg-white/80 backdrop-blur-sm focus:bg-white group-hover/input:border-purple-400"
                />
              </div>
              <button
                onClick={handleEmailReport}
                disabled={emailing}
                className="px-8 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:from-purple-700 hover:to-pink-700 hover:shadow-xl hover:shadow-purple-500/50 disabled:from-gray-400 disabled:to-gray-500 transition-all duration-300 font-bold flex items-center justify-center gap-2 transform hover:scale-105 active:scale-95"
              >
                {emailing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Sending...
                  </>
                ) : (
                  <>
                    <Mail className="w-4 h-4" />
                    Email Report
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(30px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fade-in-up {
          animation: fadeInUp 0.6s ease-out;
        }
        @keyframes shimmer {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-shimmer {
          animation: shimmer 2s infinite;
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
    </div>
  );
}
