import React, { useState } from 'react';
import axios from 'axios';
import ChatInterface from '../components/chat-interface';
import KanbanBoard from '../components/kanban-board';
import RiskModal from '../components/risk-modal';
import AlertsPanel from '../components/alerts-panel';
import LogViewer from '../components/log-viewer';
import DigestGenerator from '../components/digest-generator';
import MeetingScheduler from '../components/meeting-scheduler';

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat');
  const [planData, setPlanData] = useState(null);
  const [riskModalOpen, setRiskModalOpen] = useState(false);
  const [teamLead, setTeamLead] = useState('');
  const [alertsRefreshTrigger, setAlertsRefreshTrigger] = useState(0);
  const [logRefreshTrigger, setLogRefreshTrigger] = useState(0);
  const [digestTitle, setDigestTitle] = useState('');

  const handleCommandSubmit = async (command, message) => {
    if (command === 'plan') {
      try {
        const response = await axios.post('http://localhost:8000/api/plan', {
          plan_text: message
        });
        setPlanData(response.data);
        setActiveTab('board');
        return response.data.message;
      } catch (error) {
        console.error('Error executing plan command:', error);
        return `Error: ${error.response?.data?.detail || error.message}`;
      }
    }
    else if (command === 'risk') {
      // Extract team lead name from the message or use default
      const lead = message.trim() || 'Alice';
      setTeamLead(lead);
      setRiskModalOpen(true);
      return `Opening risk check-in modal for ${lead}...`;
    }
    else if (command === 'alerts') {
      try {
        setActiveTab('alerts');
        setAlertsRefreshTrigger(prev => prev + 1);
        
        // If message contains 'send', trigger notifications
        if (message.toLowerCase().includes('send')) {
          const response = await axios.post('http://localhost:8000/api/alerts', {
            send_notifications: true
          });
          return `Checking for overdue tasks... Found ${response.data.overdue_tasks.length} overdue tasks. Sent ${response.data.alerts_sent} notifications.`;
        } else {
          const response = await axios.get('http://localhost:8000/api/alerts/check');
          return `Checking for overdue tasks... Found ${response.data.overdue_tasks.length} overdue tasks.`;
        }
      } catch (error) {
        console.error('Error executing alerts command:', error);
        return `Error: ${error.response?.data?.detail || error.message}`;
      }
    }
    else if (command === 'log') {
      try {
        setActiveTab('log');
        setLogRefreshTrigger(prev => prev + 1);
        
        // If message contains a keyword to filter by
        if (message.trim() !== '') {
          return `Showing project log filtered by: ${message}`;
        } else {
          return 'Showing complete project log';
        }
      } catch (error) {
        console.error('Error executing log command:', error);
        return `Error: ${error.response?.data?.detail || error.message}`;
      }
    }
    else if (command === 'digest') {
      try {
        setActiveTab('digest');
        
        // If message contains title for the report
        if (message.trim() !== '') {
          setDigestTitle(message.trim());
          return `Generating stakeholder report: "${message.trim()}". Please complete the form to customize the report.`;
        } else {
          setDigestTitle('Project Status Report');
          return 'Opening report generator. Please customize and generate your stakeholder report.';
        }
      } catch (error) {
        console.error('Error executing digest command:', error);
        return `Error: ${error.response?.data?.detail || error.message}`;
      }
    }
    else if (command === 'schedule') {
      try {
        setActiveTab('schedule');
        
        // Extract any specific parameters from message (not implemented in this version)
        return 'Opening triage meeting scheduler. Please configure meeting details.';
      } catch (error) {
        console.error('Error executing schedule command:', error);
        return `Error: ${error.response?.data?.detail || error.message}`;
      }
    }
    return `Command /${command} not implemented yet`;
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">PM Agent</h1>
          <nav>
            <ul className="flex space-x-4">
              <li>
                <button 
                  onClick={() => setActiveTab('chat')}
                  className={`px-3 py-1 rounded ${activeTab === 'chat' ? 'bg-blue-700' : 'hover:bg-blue-700'}`}
                >
                  Chat
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('board')}
                  className={`px-3 py-1 rounded ${activeTab === 'board' ? 'bg-blue-700' : 'hover:bg-blue-700'}`}
                >
                  Board
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('alerts')}
                  className={`px-3 py-1 rounded ${activeTab === 'alerts' ? 'bg-blue-700' : 'hover:bg-blue-700'}`}
                >
                  Alerts
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('log')}
                  className={`px-3 py-1 rounded ${activeTab === 'log' ? 'bg-blue-700' : 'hover:bg-blue-700'}`}
                >
                  Log
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('digest')}
                  className={`px-3 py-1 rounded ${activeTab === 'digest' ? 'bg-blue-700' : 'hover:bg-blue-700'}`}
                >
                  Reports
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('schedule')}
                  className={`px-3 py-1 rounded ${activeTab === 'schedule' ? 'bg-blue-700' : 'hover:bg-blue-700'}`}
                >
                  Schedule
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </header>
      
      <main className="container mx-auto py-6 px-4">
        {activeTab === 'chat' && (
          <ChatInterface onCommandSubmit={handleCommandSubmit} />
        )}
        
        {activeTab === 'board' && (
          <KanbanBoard planData={planData} />
        )}
        
        {activeTab === 'alerts' && (
          <AlertsPanel refreshTrigger={alertsRefreshTrigger} />
        )}
        
        {activeTab === 'log' && (
          <LogViewer refreshTrigger={logRefreshTrigger} />
        )}
        
        {activeTab === 'digest' && (
          <DigestGenerator />
        )}
        
        {activeTab === 'schedule' && (
          <MeetingScheduler />
        )}
        
        {/* Risk Check-In Modal */}
        <RiskModal 
          isOpen={riskModalOpen} 
          onClose={() => setRiskModalOpen(false)} 
          teamLead={teamLead} 
        />
      </main>
    </div>
  );
}
