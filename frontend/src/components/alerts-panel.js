import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AlertsPanel = ({ refreshTrigger }) => {
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState(null);

  // Function to fetch alerts from the API
  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/alerts/check');
      setAlerts(response.data.overdue_tasks);
      setError(null);
    } catch (err) {
      console.error('Error fetching alerts:', err);
      setError('Failed to load alerts. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Send notifications to task owners
  const sendNotifications = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/alerts', {
        send_notifications: true,
        include_pending: false
      });
      
      setAlerts(response.data.overdue_tasks);
      
      // Show success message
      if (response.data.alerts_sent > 0) {
        alert(`Success! Sent ${response.data.alerts_sent} notifications to task owners.`);
      } else {
        alert('No notifications were sent. Either there are no overdue tasks or all have been notified already.');
      }
      
    } catch (err) {
      console.error('Error sending notifications:', err);
      setError('Failed to send notifications. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch alerts when the component mounts or refreshTrigger changes
  useEffect(() => {
    fetchAlerts();
  }, [refreshTrigger]);

  // Format dates nicely
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Overdue Task Alerts</h2>
        <div className="space-x-2">
          <button
            onClick={fetchAlerts}
            className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
            disabled={loading}
          >
            Refresh
          </button>
          <button
            onClick={sendNotifications}
            className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm"
            disabled={loading}
          >
            Send Notifications
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <svg className="animate-spin h-8 w-8 mx-auto text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="mt-2 text-gray-500">Loading alerts...</p>
        </div>
      ) : error ? (
        <div className="text-center py-8 text-red-500">
          <svg className="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <p className="mt-2">{error}</p>
        </div>
      ) : alerts.length === 0 ? (
        <div className="text-center py-8 text-green-500">
          <svg className="h-8 w-8 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
          </svg>
          <p className="mt-2 text-gray-500">No overdue tasks found. Everything is on track!</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Owner
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Date
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Days Overdue
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {alerts.map((task, index) => (
                <tr key={task.id || index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {task.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {task.owner}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {formatDate(task.due_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      task.days_overdue > 7 ? 'bg-red-100 text-red-800' : 
                      task.days_overdue > 3 ? 'bg-orange-100 text-orange-800' : 
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {task.days_overdue} {task.days_overdue === 1 ? 'day' : 'days'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AlertsPanel;
