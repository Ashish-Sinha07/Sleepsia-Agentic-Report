/**
 * Reports Page - Generate and Download Business Reports
 *
 * Features:
 * - Generate comprehensive business reports with date selection
 * - Preview insights and recommendations before download
 * - Download PDF reports
 * - Support for multiple report types
 */

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, Download, Eye, AlertCircle, CheckCircle } from 'lucide-react';

export default function Reports() {
  const [formData, setFormData] = useState({
    start_date: new Date(new Date().setDate(new Date().getDate() - 7))
      .toISOString()
      .split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    report_type: 'executive_summary',
  });

  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [message, setMessage] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleReportTypeChange = (value) => {
    setFormData((prev) => ({
      ...prev,
      report_type: value,
    }));
  };

  const generateReport = async () => {
    // Validate dates
    if (!formData.start_date || !formData.end_date) {
      setMessage({
        type: 'error',
        text: 'Please select both start and end dates',
      });
      return;
    }

    if (new Date(formData.start_date) > new Date(formData.end_date)) {
      setMessage({
        type: 'error',
        text: 'Start date cannot be after end date',
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch('/api/reports/comprehensive/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Get the PDF blob
      const blob = await response.blob();

      // Create a download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `sleepsia-report-${new Date().toISOString().split('T')[0]}.pdf`;

      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Clean up
      window.URL.revokeObjectURL(url);

      setMessage({
        type: 'success',
        text: 'Report generated and downloaded successfully!',
      });

      setPreview(null);
      setShowPreview(false);
    } catch (error) {
      console.error('Error generating report:', error);
      setMessage({
        type: 'error',
        text: `Error generating report: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  const previewReport = async () => {
    // Validate dates
    if (!formData.start_date || !formData.end_date) {
      setMessage({
        type: 'error',
        text: 'Please select both start and end dates',
      });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await fetch('/api/reports/comprehensive/json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setPreview(data);
      setShowPreview(true);
      setMessage({
        type: 'success',
        text: `Report preview loaded - ${data.insights?.length || 0} insights, ${data.recommendations?.length || 0} recommendations`,
      });
    } catch (error) {
      console.error('Error previewing report:', error);
      setMessage({
        type: 'error',
        text: `Error previewing report: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
        <p className="text-gray-500 mt-2">
          Generate comprehensive business reports with insights and recommendations
        </p>
      </div>

      {/* Message Alert */}
      {message && (
        <div
          className={`p-4 rounded-lg flex items-start gap-3 ${
            message.type === 'success'
              ? 'bg-green-50 border border-green-200'
              : 'bg-red-50 border border-red-200'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          )}
          <p
            className={
              message.type === 'success' ? 'text-green-800' : 'text-red-800'
            }
          >
            {message.text}
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Generator */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Report Generator</CardTitle>
              <CardDescription>
                Configure and generate your business report
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Report Type */}
              <div className="space-y-2">
                <Label htmlFor="report_type">Report Type</Label>
                <Select value={formData.report_type} onValueChange={handleReportTypeChange}>
                  <SelectTrigger id="report_type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="executive_summary">
                      Executive Summary
                    </SelectItem>
                    <SelectItem value="platform_analysis">
                      Platform Analysis
                    </SelectItem>
                    <SelectItem value="product_analysis">
                      Product Analysis
                    </SelectItem>
                    <SelectItem value="profitability">
                      Profitability Analysis
                    </SelectItem>
                    <SelectItem value="advertising">
                      Advertising Analysis
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Start Date */}
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleInputChange}
                />
              </div>

              {/* End Date */}
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleInputChange}
                />
              </div>

              {/* Buttons */}
              <div className="pt-4 space-y-2">
                <Button
                  onClick={generateReport}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      Generate & Download PDF
                    </>
                  )}
                </Button>

                <Button
                  onClick={previewReport}
                  disabled={loading}
                  variant="outline"
                  className="w-full"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    <>
                      <Eye className="mr-2 h-4 w-4" />
                      Preview Report
                    </>
                  )}
                </Button>
              </div>

              {/* Info */}
              <div className="text-sm text-gray-600 border-t pt-4">
                <p>
                  Your report will include:
                </p>
                <ul className="mt-2 space-y-1 text-xs">
                  <li>✓ Executive summary</li>
                  <li>✓ Key performance indicators</li>
                  <li>✓ Platform & product analysis</li>
                  <li>✓ Business insights</li>
                  <li>✓ Strategic recommendations</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Preview */}
        <div className="lg:col-span-2">
          {showPreview && preview ? (
            <div className="space-y-4">
              {/* Report Info */}
              <Card>
                <CardHeader>
                  <CardTitle>Report Preview</CardTitle>
                  <CardDescription>
                    Report ID: {preview.report_id}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-500">Start Date</p>
                      <p className="font-medium">{preview.start_date}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">End Date</p>
                      <p className="font-medium">{preview.end_date}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Generated At</p>
                      <p className="font-medium">
                        {new Date(preview.generated_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Generated Time</p>
                      <p className="font-medium">
                        {new Date(preview.generated_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Metrics */}
              {preview.metrics && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Key Metrics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-500">Revenue</p>
                        <p className="font-medium text-lg">
                          ₹{(preview.metrics.revenue || 0).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Profit</p>
                        <p className="font-medium text-lg">
                          ₹{(preview.metrics.profit || 0).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Profit Margin</p>
                        <p className="font-medium text-lg">
                          {(preview.metrics.profit_margin || 0).toFixed(1)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Orders</p>
                        <p className="font-medium text-lg">
                          {(preview.metrics.orders || 0).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">Units Sold</p>
                        <p className="font-medium text-lg">
                          {(preview.metrics.units || 0).toLocaleString()}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-500">ROAS</p>
                        <p className="font-medium text-lg">
                          {(preview.metrics.roas || 0).toFixed(2)}x
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Insights */}
              {preview.insights && preview.insights.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">
                      Business Insights ({preview.insights.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {preview.insights.map((insight, idx) => (
                      <div
                        key={idx}
                        className={`p-3 rounded-lg border ${
                          insight.priority === 'HIGH'
                            ? 'border-red-200 bg-red-50'
                            : 'border-blue-200 bg-blue-50'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <p className="font-medium text-sm">
                              {insight.title}
                            </p>
                            <p className="text-xs text-gray-600 mt-1">
                              {insight.description}
                            </p>
                          </div>
                          <span
                            className={`text-xs font-bold px-2 py-1 rounded ${
                              insight.priority === 'HIGH'
                                ? 'bg-red-200 text-red-800'
                                : 'bg-blue-200 text-blue-800'
                            }`}
                          >
                            {insight.priority}
                          </span>
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Recommendations */}
              {preview.recommendations && preview.recommendations.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">
                      Strategic Recommendations ({preview.recommendations.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {preview.recommendations.map((rec, idx) => (
                      <div key={idx} className="p-3 border rounded-lg">
                        <p className="font-medium text-sm">{rec.action}</p>
                        <p className="text-xs text-gray-600 mt-1">
                          {rec.description}
                        </p>
                        {rec.timeline && (
                          <p className="text-xs text-gray-500 mt-2">
                            Timeline: {rec.timeline}
                          </p>
                        )}
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Download Button in Preview */}
              <Button
                onClick={generateReport}
                disabled={loading}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="mr-2 h-4 w-4" />
                    Download PDF Report
                  </>
                )}
              </Button>
            </div>
          ) : (
            <Card className="h-full flex items-center justify-center">
              <CardContent className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Eye className="w-12 h-12 mx-auto opacity-50" />
                </div>
                <p className="text-gray-500">
                  Click "Preview Report" to see insights and recommendations
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
