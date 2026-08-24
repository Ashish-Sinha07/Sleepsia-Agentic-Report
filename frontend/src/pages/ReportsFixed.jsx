/**
 * Reports Page - Fixed Version
 * Generates and downloads comprehensive business reports
 */

import React, { useState } from 'react';
import axios from 'axios';

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
  const [message, setMessage] = useState(null);

  const handleDateChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleReportTypeChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      report_type: e.target.value,
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
      console.log('Generating report with:', formData);

      // Make API request
      const response = await axios.post(
        'http://localhost:8000/api/reports/comprehensive/generate',
        formData,
        {
          responseType: 'blob',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      console.log('Report generated successfully, size:', response.data.size);

      // Create download link
      const url = window.URL.createObjectURL(response.data);
      const link = document.createElement('a');
      link.href = url;
      link.download = `sleepsia-report-${formData.end_date}.pdf`;

      // Trigger download
      document.body.appendChild(link);
      link.click();

      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setMessage({
        type: 'success',
        text: `Report downloaded successfully! File: sleepsia-report-${formData.end_date}.pdf`,
      });

    } catch (error) {
      console.error('Error generating report:', error);

      let errorText = 'Error generating report';
      if (error.response) {
        errorText = `Error: ${error.response.status} - ${error.response.statusText}`;
      } else if (error.message) {
        errorText = `Error: ${error.message}`;
      }

      setMessage({
        type: 'error',
        text: errorText,
      });
    } finally {
      setLoading(false);
    }
  };

  const previewReport = async () => {
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
      console.log('Previewing report with:', formData);

      const response = await axios.post(
        'http://localhost:8000/api/reports/comprehensive/json',
        formData
      );

      console.log('Preview data:', response.data);

      setPreview(response.data);
      setMessage({
        type: 'success',
        text: `Preview loaded: ${response.data.insights?.length || 0} insights, ${response.data.recommendations?.length || 0} recommendations`,
      });

    } catch (error) {
      console.error('Error previewing report:', error);
      setMessage({
        type: 'error',
        text: `Preview error: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      <h1>Report Generator</h1>
      <p>Generate comprehensive business reports with insights and recommendations</p>

      {/* Message */}
      {message && (
        <div
          style={{
            padding: '12px',
            marginBottom: '20px',
            borderRadius: '4px',
            backgroundColor: message.type === 'success' ? '#dcfce7' : '#fee2e2',
            borderLeft: `4px solid ${message.type === 'success' ? '#22c55e' : '#ef4444'}`,
            color: message.type === 'success' ? '#166534' : '#991b1b',
          }}
        >
          {message.text}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '20px' }}>
        {/* Form */}
        <div
          style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '20px',
            backgroundColor: '#f9fafb',
          }}
        >
          <h2>Report Configuration</h2>

          {/* Report Type */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Report Type
            </label>
            <select
              name="report_type"
              value={formData.report_type}
              onChange={handleReportTypeChange}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
              }}
            >
              <option value="executive_summary">Executive Summary</option>
              <option value="platform_analysis">Platform Analysis</option>
              <option value="product_analysis">Product Analysis</option>
              <option value="profitability">Profitability Analysis</option>
              <option value="advertising">Advertising Analysis</option>
            </select>
          </div>

          {/* Start Date */}
          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Start Date
            </label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleDateChange}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
              }}
            />
          </div>

          {/* End Date */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              End Date
            </label>
            <input
              type="date"
              name="end_date"
              value={formData.end_date}
              onChange={handleDateChange}
              style={{
                width: '100%',
                padding: '8px',
                border: '1px solid #ddd',
                borderRadius: '4px',
                fontSize: '14px',
              }}
            />
          </div>

          {/* Buttons */}
          <button
            onClick={generateReport}
            disabled={loading}
            style={{
              width: '100%',
              padding: '10px',
              marginBottom: '10px',
              backgroundColor: loading ? '#ccc' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            {loading ? 'Generating...' : 'Generate & Download PDF'}
          </button>

          <button
            onClick={previewReport}
            disabled={loading}
            style={{
              width: '100%',
              padding: '10px',
              backgroundColor: loading ? '#ccc' : '#6b7280',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: 'bold',
            }}
          >
            {loading ? 'Loading...' : 'Preview Report'}
          </button>

          <div
            style={{
              marginTop: '20px',
              padding: '10px',
              backgroundColor: 'white',
              borderRadius: '4px',
              fontSize: '12px',
              lineHeight: '1.6',
            }}
          >
            <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>Report includes:</p>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li>Executive summary</li>
              <li>Key performance indicators</li>
              <li>Platform & product analysis</li>
              <li>Business insights (AI-generated)</li>
              <li>Strategic recommendations</li>
            </ul>
          </div>
        </div>

        {/* Preview or Empty State */}
        <div
          style={{
            border: '1px solid #ddd',
            borderRadius: '8px',
            padding: '20px',
            backgroundColor: '#f9fafb',
            minHeight: '500px',
          }}
        >
          {preview ? (
            <div>
              <h2>Report Preview</h2>

              {/* Report Info */}
              <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: 'white', borderRadius: '4px' }}>
                <h3>Report Information</h3>
                <p><strong>Report ID:</strong> {preview.report_id}</p>
                <p><strong>Period:</strong> {preview.start_date} to {preview.end_date}</p>
                <p><strong>Generated:</strong> {new Date(preview.generated_at).toLocaleString()}</p>
              </div>

              {/* Metrics */}
              {preview.metrics && (
                <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: 'white', borderRadius: '4px' }}>
                  <h3>Key Metrics</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '13px' }}>
                    <div>
                      <p style={{ margin: '0 0 3px 0', color: '#666' }}>Revenue</p>
                      <p style={{ margin: 0, fontWeight: 'bold' }}>Rs {(preview.metrics.revenue || 0).toLocaleString()}</p>
                    </div>
                    <div>
                      <p style={{ margin: '0 0 3px 0', color: '#666' }}>Profit</p>
                      <p style={{ margin: 0, fontWeight: 'bold' }}>Rs {(preview.metrics.profit || 0).toLocaleString()}</p>
                    </div>
                    <div>
                      <p style={{ margin: '0 0 3px 0', color: '#666' }}>Profit Margin</p>
                      <p style={{ margin: 0, fontWeight: 'bold' }}>{(preview.metrics.profit_margin || 0).toFixed(1)}%</p>
                    </div>
                    <div>
                      <p style={{ margin: '0 0 3px 0', color: '#666' }}>ROAS</p>
                      <p style={{ margin: 0, fontWeight: 'bold' }}>{(preview.metrics.roas || 0).toFixed(2)}x</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Insights */}
              {preview.insights && preview.insights.length > 0 && (
                <div style={{ marginBottom: '20px' }}>
                  <h3>Insights ({preview.insights.length})</h3>
                  {preview.insights.map((insight, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '10px',
                        marginBottom: '8px',
                        borderRadius: '4px',
                        backgroundColor: insight.priority === 'HIGH' ? '#fee2e2' : '#dbeafe',
                        borderLeft: `4px solid ${insight.priority === 'HIGH' ? '#ef4444' : '#3b82f6'}`,
                        fontSize: '12px',
                      }}
                    >
                      <p style={{ margin: '0 0 3px 0', fontWeight: 'bold' }}>
                        {insight.title} <span style={{ color: '#666' }}>({insight.priority})</span>
                      </p>
                      <p style={{ margin: 0, fontSize: '11px' }}>{insight.description}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Recommendations */}
              {preview.recommendations && preview.recommendations.length > 0 && (
                <div>
                  <h3>Recommendations ({preview.recommendations.length})</h3>
                  {preview.recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: '10px',
                        marginBottom: '8px',
                        borderRadius: '4px',
                        backgroundColor: 'white',
                        border: '1px solid #ddd',
                        fontSize: '12px',
                      }}
                    >
                      <p style={{ margin: '0 0 3px 0', fontWeight: 'bold' }}>{rec.action}</p>
                      <p style={{ margin: '0 0 3px 0', fontSize: '11px' }}>{rec.description}</p>
                      {rec.timeline && (
                        <p style={{ margin: 0, fontSize: '11px', color: '#666' }}>Timeline: {rec.timeline}</p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Download Button */}
              <button
                onClick={generateReport}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '10px',
                  marginTop: '20px',
                  backgroundColor: loading ? '#ccc' : '#10b981',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  fontWeight: 'bold',
                }}
              >
                {loading ? 'Downloading...' : 'Download PDF Report'}
              </button>
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#999', marginTop: '200px' }}>
              <p>Click "Preview Report" to see insights and recommendations</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
