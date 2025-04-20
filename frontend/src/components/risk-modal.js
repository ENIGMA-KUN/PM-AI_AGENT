import React, { useState, useEffect } from 'react';
import axios from 'axios';

const RiskModal = ({ isOpen, onClose, teamLead }) => {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Fetch stories for the team lead when modal opens
  useEffect(() => {
    if (isOpen && teamLead) {
      fetchStories();
    }
  }, [isOpen, teamLead]);

  const fetchStories = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/risk/stories/${teamLead}`);
      
      // Transform stories into form state
      const storiesWithStatus = response.data.stories.map(story => ({
        ...story,
        on_track: true, // Default to on track
        reason: '', // Default to no reason
      }));
      
      setStories(storiesWithStatus);
    } catch (err) {
      setError('Failed to load stories. Please try again.');
      console.error('Error fetching stories:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTrackChange = (storyId, value) => {
    setStories(prev => 
      prev.map(story => 
        story.story_id === storyId ? { ...story, on_track: value } : story
      )
    );
  };

  const handleReasonChange = (storyId, reason) => {
    setStories(prev => 
      prev.map(story => 
        story.story_id === storyId ? { ...story, reason } : story
      )
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');
    
    try {
      const payload = {
        team_lead: teamLead,
        items: stories.map(story => ({
          story_id: story.story_id,
          title: story.title,
          on_track: story.on_track,
          reason: story.reason
        }))
      };
      
      const response = await axios.post('http://localhost:8000/api/risk', payload);
      
      // Show success message
      setSuccess('Risk check-in submitted successfully!');
      
      // Auto-close after delay
      setTimeout(() => {
        onClose();
        setSuccess('');
      }, 2000);
    } catch (err) {
      setError('Failed to submit risk check-in. Please try again.');
      console.error('Error submitting risk check:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-11/12 max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Risk Check-In: {teamLead}</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>
        
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            {stories.length === 0 ? (
              <p className="text-gray-500 py-4">No active stories found for {teamLead}.</p>
            ) : (
              <div className="space-y-6">
                {stories.map(story => (
                  <div key={story.story_id} className="border rounded-lg p-4">
                    <div className="font-medium mb-2">{story.title}</div>
                    <div className="text-sm text-gray-600 mb-3">Due: {story.due_date}</div>
                    
                    <div className="mb-3">
                      <div className="text-sm font-medium mb-1">Is this story on track?</div>
                      <div className="flex space-x-4">
                        <label className="inline-flex items-center">
                          <input
                            type="radio"
                            name={`on_track_${story.story_id}`}
                            checked={story.on_track}
                            onChange={() => handleTrackChange(story.story_id, true)}
                            className="form-radio text-blue-500"
                          />
                          <span className="ml-2">Yes</span>
                        </label>
                        <label className="inline-flex items-center">
                          <input
                            type="radio"
                            name={`on_track_${story.story_id}`}
                            checked={!story.on_track}
                            onChange={() => handleTrackChange(story.story_id, false)}
                            className="form-radio text-red-500"
                          />
                          <span className="ml-2">No</span>
                        </label>
                      </div>
                    </div>
                    
                    {!story.on_track && (
                      <div>
                        <div className="text-sm font-medium mb-1">Reason:</div>
                        <select
                          value={story.reason}
                          onChange={(e) => handleReasonChange(story.story_id, e.target.value)}
                          className="w-full p-2 border rounded-lg"
                        >
                          <option value="">Select a reason...</option>
                          <option value="Need Discussion">Need Discussion</option>
                          <option value="Missing Estimated Completion">Missing Estimated Completion</option>
                          <option value="Technical Issue">Technical Issue</option>
                          <option value="Dependency Blocked">Dependency Blocked</option>
                          <option value="Other">Other</option>
                        </select>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
            
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mt-4">
                {error}
              </div>
            )}
            
            {success && (
              <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mt-4">
                {success}
              </div>
            )}
            
            <div className="flex justify-end mt-6 space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border rounded-lg hover:bg-gray-100"
                disabled={submitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
                disabled={submitting || stories.length === 0}
              >
                {submitting ? 'Submitting...' : 'Submit'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default RiskModal;
