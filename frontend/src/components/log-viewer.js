import React, { useState, useEffect } from 'react';
import axios from 'axios';

const LogViewer = ({ refreshTrigger }) => {
  const [loading, setLoading] = useState(true);
  const [logEntries, setLogEntries] = useState([]);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({
    keyword: '',
    dateFrom: '',
    dateTo: '',
  });

  // Function to fetch log entries from the API
  const fetchLogEntries = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/log');
      setLogEntries(response.data.entries);
      setError(null);
    } catch (err) {
      console.error('Error fetching log entries:', err);
      setError('Failed to load project log. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Function to filter log entries
  const filterLogEntries = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/log/filter', {
        keyword: filter.keyword || undefined,
        date_from: filter.dateFrom || undefined,
        date_to: filter.dateTo || undefined,
        limit: 50
      });
      setLogEntries(response.data.entries);
      setError(null);
    } catch (err) {
      console.error('Error filtering log entries:', err);
      setError('Failed to filter log entries. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Reset filters
  const resetFilters = () => {
    setFilter({
      keyword: '',
      dateFrom: '',
      dateTo: '',
    });
    fetchLogEntries();
  };

  // Fetch log entries when the component mounts or refreshTrigger changes
  useEffect(() => {
    fetchLogEntries();
  }, [refreshTrigger]);

  // Parse code blocks and URLs in log messages
  const formatMessage = (message) => {
    // Replace `code` segments with styled spans
    let formattedMessage = message.replace(
      /`([^`]+)`/g, 
      '<span class="bg-gray-100 text-pink-600 px-1 rounded font-mono text-sm">$1</span>'
    );
    
    return (
      <div dangerouslySetInnerHTML={{ __html: formattedMessage }} />
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Project Log</h2>
        <button
          onClick={fetchLogEntries}
          className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="mb-6 bg-gray-50 p-4 rounded-md">
        <h3 className="text-sm font-medium text-gray-700 mb-2">Filter Log Entries</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-gray-500 mb-1">Keyword</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-md text-sm"
              placeholder="Search by keyword"
              value={filter.keyword}
              onChange={(e) => setFilter({ ...filter, keyword: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">From Date</label>
            <input
              type="date"
              className="w-full px-3 py-2 border rounded-md text-sm"
              value={filter.dateFrom}
              onChange={(e) => setFilter({ ...filter, dateFrom: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">To Date</label>
            <input
              type="date"
              className="w-full px-3 py-2 border rounded-md text-sm"
              value={filter.dateTo}
              onChange={(e) => setFilter({ ...filter, dateTo: e.target.value })}
            />
          </div>
        </div>
        <div className="mt-3 flex gap-2 justify-end">
          <button
            onClick={resetFilters}
            className="px-3 py-1 border border-gray-300 hover:bg-gray-100 rounded text-sm"
          >
            Reset
          </button>
          <button
            onClick={filterLogEntries}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
            disabled={loading}
          >
            Apply Filters
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <svg className="animate-spin h-8 w-8 mx-auto text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="mt-2 text-gray-500">Loading project log...</p>
        </div>
      ) : error ? (
        <div className="text-center py-8 text-red-500">
          <svg className="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p className="mt-2">{error}</p>
        </div>
      ) : logEntries.length === 0 ? (
        <div className="text-center py-8">
          <svg className="h-8 w-8 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
          </svg>
          <p className="mt-2 text-gray-500">No log entries found matching your criteria.</p>
        </div>
      ) : (
        <div className="overflow-hidden border border-gray-200 rounded-md">
          <ul className="divide-y divide-gray-200">
            {logEntries.map((entry, index) => (
              <li key={index} className="p-4 hover:bg-gray-50">
                <div className="flex flex-col md:flex-row md:justify-between">
                  <div className="font-mono text-xs text-gray-500 mb-1 md:mb-0">
                    {entry.timestamp}
                  </div>
                  <div className="text-sm text-gray-800">
                    {formatMessage(entry.message)}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default LogViewer;
