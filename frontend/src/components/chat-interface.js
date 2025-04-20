import React, { useState, useRef, useEffect } from 'react';

const ChatInterface = ({ onCommandSubmit }) => {
  const [messages, setMessages] = useState([
    { 
      id: 1, 
      type: 'system', 
      content: 'Welcome to PM Agent! Try using a command like "/plan Redesign landing page by Sep-05; Dev: Alice,Bob; Mktg: Carol"'
    }
  ]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Process commands
    if (input.startsWith('/')) {
      const parts = input.substring(1).split(' ');
      const command = parts[0];
      const message = parts.slice(1).join(' ');
      
      // Show typing indicator
      setMessages(prev => [
        ...prev, 
        { id: 'typing', type: 'system', content: 'Processing...', isTyping: true }
      ]);
      
      // Execute command
      const response = await onCommandSubmit(command, message);
      
      // Remove typing indicator and add response
      setMessages(prev => 
        prev.filter(msg => msg.id !== 'typing').concat({
          id: Date.now() + 1,
          type: 'system',
          content: response
        })
      );
    } else {
      // Regular message - simple echo for now
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          type: 'system',
          content: 'Use a command like "/plan" to interact with the PM Agent.'
        }
      ]);
    }
    
    // Clear input
    setInput('');
  };

  return (
    <div className="flex flex-col h-[70vh] bg-white rounded-lg shadow-md">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(message => (
          <div 
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div 
              className={`max-w-3/4 p-3 rounded-lg ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white rounded-br-none' 
                  : 'bg-gray-200 text-gray-800 rounded-bl-none'
              } ${message.isTyping ? 'animate-pulse' : ''}`}
            >
              {message.content}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <form onSubmit={handleSubmit} className="border-t p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={handleInputChange}
            placeholder="Type a command (e.g., /plan) or message..."
            className="flex-1 border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;
