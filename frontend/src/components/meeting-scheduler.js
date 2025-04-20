import React, { useState, useEffect } from 'react';
import axios from 'axios';

const MeetingScheduler = () => {
  const [loading, setLoading] = useState(false);
  const [checkingBlocked, setCheckingBlocked] = useState(true);
  const [blockedTasks, setBlockedTasks] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [formData, setFormData] = useState({
    title: 'Project Triage Meeting',
    duration_minutes: 15,
    auto_schedule: true,
    blocked_stories: [],
    additional_attendees: [],
    preferred_start_time: '',
    preferred_day: ''
  });
  const [newAttendee, setNewAttendee] = useState({ name: '', email: '' });

  // Fetch blocked tasks when component mounts
  useEffect(() => {
    fetchBlockedTasks();
  }, []);

  const fetchBlockedTasks = async () => {
    setCheckingBlocked(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:8000/api/schedule/blocked');
      setBlockedTasks(response.data.blocked_stories);
      
      // Pre-select all blocked stories
      if (response.data.blocked_stories.length > 0) {
        setFormData(prev => ({
          ...prev,
          blocked_stories: response.data.blocked_stories.map(story => `${story.id}: ${story.title}`)
        }));
      }
    } catch (err) {
      console.error('Error fetching blocked tasks:', err);
      setError('Failed to load blocked tasks. Please try again.');
    } finally {
      setCheckingBlocked(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleAttendeeChange = (e) => {
    const { name, value } = e.target;
    setNewAttendee(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const addAttendee = () => {
    if (newAttendee.name.trim() === '' || newAttendee.email.trim() === '') {
      return;
    }
    
    setFormData(prev => ({
      ...prev,
      additional_attendees: [...prev.additional_attendees, { ...newAttendee }]
    }));
    
    // Reset the form
    setNewAttendee({ name: '', email: '' });
  };

  const removeAttendee = (index) => {
    setFormData(prev => ({
      ...prev,
      additional_attendees: prev.additional_attendees.filter((_, i) => i !== index)
    }));
  };

  const scheduleMeeting = async () => {
    setLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const response = await axios.post('http://localhost:8000/api/schedule', formData);
      
      setSuccess({
        message: response.data.message,
        meetingTime: new Date(response.data.scheduled_time).toLocaleString(),
        meetingLink: response.data.meeting_link,
        attendees: response.data.attendees
      });
      
      // Clear form if successful
      if (response.data.meeting_id) {
        setFormData({
          title: 'Project Triage Meeting',
          duration_minutes: 15,
          auto_schedule: true,
          blocked_stories: [],
          additional_attendees: [],
          preferred_start_time: '',
          preferred_day: ''
        });
      }
    } catch (err) {
      console.error('Error scheduling meeting:', err);
      setError(err.response?.data?.detail || 'Failed to schedule meeting. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Format date for input
  const formatDateForInput = (date) => {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2) month = '0' + month;
    if (day.length < 2) day = '0' + day;

    return [year, month, day].join('-');
  };

  // Set today as the default date
  const today = formatDateForInput(new Date());

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold mb-4">Schedule Triage Meeting</h2>
      
      {/* Blocked Tasks Section */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-md font-medium">Blocked Tasks</h3>
          <button
            onClick={fetchBlockedTasks}
            className="text-sm text-blue-600 hover:text-blue-800"
            disabled={checkingBlocked}
          >
            {checkingBlocked ? 'Checking...' : 'Refresh'}
          </button>
        </div>
        
        {checkingBlocked ? (
          <div className="text-center py-4">
            <svg className="animate-spin h-5 w-5 mx-auto text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        ) : blockedTasks.length === 0 ? (
          <div className="bg-green-50 border border-green-200 text-green-800 p-3 rounded-md text-sm">
            No blocked tasks found. All tasks are on track!
          </div>
        ) : (
          <div className="bg-gray-50 p-3 rounded-md max-h-40 overflow-y-auto">
            <ul className="space-y-2">
              {blockedTasks.map((task, index) => (
                <li key={index} className="flex items-start">
                  <input
                    type="checkbox"
                    id={`task-${index}`}
                    checked={formData.blocked_stories.includes(`${task.id}: ${task.title}`)}
                    onChange={(e) => {
                      const taskId = `${task.id}: ${task.title}`;
                      if (e.target.checked) {
                        setFormData(prev => ({
                          ...prev,
                          blocked_stories: [...prev.blocked_stories, taskId]
                        }));
                      } else {
                        setFormData(prev => ({
                          ...prev,
                          blocked_stories: prev.blocked_stories.filter(id => id !== taskId)
                        }));
                      }
                    }}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor={`task-${index}`} className="ml-2 block text-sm text-gray-700">
                    <span className="font-medium">{task.id}: {task.title}</span>
                    <br />
                    <span className="text-xs text-gray-500">Owner: {task.owner}</span>
                    <br />
                    <span className="text-xs text-red-500">Blocker: {task.blocker_description}</span>
                  </label>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {/* Meeting Settings Form */}
      <div className="mb-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Meeting Title
          </label>
          <input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            placeholder="Project Triage Meeting"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Duration (minutes)
          </label>
          <select
            name="duration_minutes"
            value={formData.duration_minutes}
            onChange={handleInputChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="15">15 minutes</option>
            <option value="30">30 minutes</option>
            <option value="45">45 minutes</option>
            <option value="60">1 hour</option>
          </select>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preferred Day
            </label>
            <input
              type="date"
              name="preferred_day"
              value={formData.preferred_day}
              min={today}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preferred Time
            </label>
            <input
              type="time"
              name="preferred_start_time"
              value={formData.preferred_start_time}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        <div className="flex items-center">
          <input
            id="auto_schedule"
            name="auto_schedule"
            type="checkbox"
            checked={formData.auto_schedule}
            onChange={handleInputChange}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="auto_schedule" className="ml-2 block text-sm text-gray-700">
            Automatically schedule meeting and send invitations
          </label>
        </div>
      </div>
      
      {/* Additional Attendees */}
      <div className="mb-6">
        <h3 className="text-md font-medium mb-2">Additional Attendees</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-2">
          <div>
            <input
              type="text"
              name="name"
              value={newAttendee.name}
              onChange={handleAttendeeChange}
              placeholder="Name"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md"
            />
          </div>
          <div className="md:col-span-1">
            <input
              type="email"
              name="email"
              value={newAttendee.email}
              onChange={handleAttendeeChange}
              placeholder="Email"
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <button
              onClick={addAttendee}
              className="w-full px-3 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
              disabled={!newAttendee.name || !newAttendee.email}
            >
              Add Attendee
            </button>
          </div>
        </div>
        
        {formData.additional_attendees.length > 0 && (
          <div className="bg-gray-50 p-3 rounded-md mt-2">
            <ul className="divide-y divide-gray-200">
              {formData.additional_attendees.map((attendee, index) => (
                <li key={index} className="py-2 flex justify-between items-center">
                  <div>
                    <span className="text-sm font-medium">{attendee.name}</span>
                    <span className="ml-2 text-xs text-gray-500">{attendee.email}</span>
                  </div>
                  <button
                    onClick={() => removeAttendee(index)}
                    className="text-red-500 hover:text-red-700 text-sm"
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {/* Submit Button */}
      <div className="flex justify-end">
        <button
          onClick={scheduleMeeting}
          disabled={loading || (blockedTasks.length === 0 && formData.blocked_stories.length === 0)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
        >
          {loading ? 'Scheduling...' : 'Schedule Meeting'}
        </button>
      </div>
      
      {/* Error Message */}
      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-md">
          <p>{error}</p>
        </div>
      )}
      
      {/* Success Message */}
      {success && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
          <h3 className="text-lg font-medium text-green-800 mb-2">Meeting Scheduled!</h3>
          <p className="text-sm text-green-600">{success.message}</p>
          
          <div className="mt-3 space-y-2">
            <p className="text-sm">
              <span className="font-medium">Time:</span> {success.meetingTime}
            </p>
            
            {success.meetingLink && (
              <p className="text-sm">
                <span className="font-medium">Meeting Link:</span>{' '}
                <a 
                  href={success.meetingLink} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {success.meetingLink}
                </a>
              </p>
            )}
            
            {success.attendees && success.attendees.length > 0 && (
              <div className="text-sm">
                <span className="font-medium">Attendees:</span>
                <ul className="mt-1 list-disc list-inside pl-2">
                  {success.attendees.map((email, i) => (
                    <li key={i} className="text-gray-600">{email}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MeetingScheduler;
