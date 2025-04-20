import React, { useState } from 'react';
import axios from 'axios';

const DigestGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [reportGenerated, setReportGenerated] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [formData, setFormData] = useState({
    title: 'Project Status Report',
    include_charts: true,
    include_blockers: true,
    start_date: '',
    end_date: ''
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const generateReport = async () => {
    setLoading(true);
    setError(null);
    setReportGenerated(false);
    setReportData(null);

    try {
      const response = await axios.post('http://localhost:8000/api/digest', formData);
      
      setReportGenerated(true);
      setReportData(response.data);
    } catch (err) {
      console.error('Error generating report:', err);
      setError(err.response?.data?.detail || 'Failed to generate report. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    if (!reportData || !reportData.pdf_path) return;
    
    // Extract filename from path
    const filename = reportData.pdf_path.split('/').pop();
    
    // Create download URL
    const downloadUrl = `http://localhost:8000/api/digest/download/${filename}`;
    
    // Open in new tab
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">Generate Stakeholder Report</h2>
      
      <div className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Report Title
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Project Status Report"
          />
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date (Optional)
            </label>
            <input
              type="date"
              name="start_date"
              value={formData.start_date}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date (Optional)
            </label>
            <input
              type="date"
              name="end_date"
              value={formData.end_date}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex items-center">
            <input
              id="include_charts"
              name="include_charts"
              type="checkbox"
              checked={formData.include_charts}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="include_charts" className="ml-2 block text-sm text-gray-700">
              Include Charts
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              id="include_blockers"
              name="include_blockers"
              type="checkbox"
              checked={formData.include_blockers}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="include_blockers" className="ml-2 block text-sm text-gray-700">
              Include Blockers & Risks
            </label>
          </div>
        </div>
      </div>
      
      <div className="flex justify-end">
        <button
          onClick={generateReport}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Report'}
        </button>
      </div>
      
      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
          <p>{error}</p>
        </div>
      )}
      
      {reportGenerated && reportData && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-medium text-green-800">Report Generated Successfully!</h3>
              <p className="text-sm text-green-600 mt-1">{reportData.message}</p>
            </div>
            <button
              onClick={downloadReport}
              className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white text-sm rounded-md shadow-sm"
            >
              Download PDF
            </button>
          </div>
          
          {reportData.charts && (
            <div className="mt-4 space-y-4">
              <h4 className="text-md font-medium text-gray-700">Report Charts</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {reportData.charts.status_chart && (
                  <div className="border rounded-md p-2">
                    <h5 className="text-sm font-medium text-gray-600 mb-2">Status Distribution</h5>
                    <img 
                      src={`data:image/png;base64,${reportData.charts.status_chart}`} 
                      alt="Status Chart" 
                      className="w-full" 
                    />
                  </div>
                )}
                
                {reportData.charts.burndown_chart && (
                  <div className="border rounded-md p-2">
                    <h5 className="text-sm font-medium text-gray-600 mb-2">Burndown Chart</h5>
                    <img 
                      src={`data:image/png;base64,${reportData.charts.burndown_chart}`} 
                      alt="Burndown Chart" 
                      className="w-full" 
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DigestGenerator;
