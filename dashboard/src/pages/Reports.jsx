import { useContext, useState } from 'react';
import FilterBar from '../components/filters/FilterBar';
import { Download, FileText } from 'lucide-react';
import { FilterContext } from '../context/FilterContext';
import apiClient from '../services/api';

export default function Reports() {
  const { filters } = useContext(FilterContext);
  const [reportType, setReportType] = useState('management-summary');
  const [format, setFormat] = useState('pdf');
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const reportTypes = [
    { id: 'management-summary', label: 'Management Summary', description: 'Executive summary with key metrics' },
    { id: 'platform-report', label: 'Platform Report', description: 'Detailed platform performance analysis' },
    { id: 'product-report', label: 'Product Report', description: 'Product-wise performance breakdown' },
    { id: 'profitability-report', label: 'Profitability Report', description: 'Profitability and cost analysis' },
    { id: 'inventory-report', label: 'Inventory Report', description: 'Warehouse and inventory status' },
  ];

  const handleGenerateReport = async () => {
    setGenerating(true);
    setError(null);
    setResult(null);
    try {
      const response = await apiClient.post('/api/reports', {
        report_type: reportType === 'management-summary' ? 'executive_summary' : reportType.replace('-report', '').replace('-', '_'),
        start_date: filters.startDate.toISOString().slice(0, 10),
        end_date: filters.endDate.toISOString().slice(0, 10),
        format,
      });
      setResult(response);

      const reportFile = await apiClient.get(`/api/reports/${response.report_id}/download`, {
        params: { format },
        responseType: 'blob',
      });
      const downloadUrl = URL.createObjectURL(reportFile);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `${response.report_id}.${response.format || format}`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      const errorMessage = err?.response?.data?.detail || err?.response?.data?.message || err?.message || 'Failed to generate report';
      setError(errorMessage);
      console.error('Report generation error:', err);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600 mt-1">Generate and download management reports</p>
      </div>

      <FilterBar />

      <div className="grid grid-cols-2 gap-4 mb-6">
        {reportTypes.map((report) => (
          <div
            key={report.id}
            onClick={() => setReportType(report.id)}
            className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
              reportType === report.id
                ? 'border-sleepsia-600 bg-sleepsia-50'
                : 'border-gray-200 hover:border-sleepsia-300'
            }`}
          >
            <div className="flex items-start gap-3">
              <FileText className={`w-5 h-5 flex-shrink-0 ${
                reportType === report.id ? 'text-sleepsia-600' : 'text-gray-400'
              }`} />
              <div>
                <p className="font-medium text-gray-900">{report.label}</p>
                <p className="text-sm text-gray-600 mt-1">{report.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <div className="card-header">
          <h3 className="font-semibold text-gray-900">Report Configuration</h3>
        </div>
        <div className="card-body space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">Report Type</label>
            <p className="text-sm text-gray-600">
              {reportTypes.find(r => r.id === reportType)?.label}
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">From Date</label>
              <input
                type="date"
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">To Date</label>
              <input
                type="date"
                disabled
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-gray-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-900 mb-2">Format</label>
              <select value={format} onChange={(e) => setFormat(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
                <option value="pdf">PDF</option>
                <option value="json">JSON</option>
                <option value="excel">Excel</option>
              </select>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleGenerateReport}
              disabled={generating}
              className="btn-primary flex items-center gap-2"
            >
              {generating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Generating...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Generate Report
                </>
              )}
            </button>
          </div>
          {error && <p className="text-sm text-red-700">{error}</p>}
          {result && <p className="text-sm text-green-700">Report {result.report_id} generated successfully.</p>}
        </div>
      </div>
    </div>
  );
}
