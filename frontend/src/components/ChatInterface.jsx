import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessageStream } from '../services/api';

export default function ChatInterface() {
  const initialMessage = {
    role: 'assistant',
    text: 'Hello! I am your AI Real Estate Assistant. How can I help you find a property today?'
  };

  const [messages, setMessages] = useState([initialMessage]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom of the chat window on new messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // NEW: Function to reset the chat and session memory
  const handleClearSession = () => {
    if (isLoading) return; // Prevent clearing while the AI is currently typing
    setMessages([initialMessage]);
    setSessionId(null);
    setInput('');
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // 1. Append the user message locally
    setMessages((prev) => [...prev, { role: 'user', text: userMessage }]);

    // 2. Insert a temporary blank placeholder for the assistant stream
    setMessages((prev) => [...prev, { role: 'assistant', text: '' }]);

    try {
      // 3. Trigger the streaming generator
      const stream = sendChatMessageStream(userMessage, sessionId);

      for await (const chunk of stream) {
        // Set the active session ID if not already saved
        if (chunk.sessionId && !sessionId) {
          setSessionId(chunk.sessionId);
        }

        // 4. Update the very last message token-by-token
        setMessages((prev) => {
          const updated = [...prev];
          const lastIndex = updated.length - 1;
          updated[lastIndex] = {
            ...updated[lastIndex],
            text: updated[lastIndex].text + chunk.token,
          };
          return updated;
        });
      }
    } catch (error) {
      console.error("Failed to stream response:", error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: 'Sorry, an error occurred while generating the response.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[90vh] max-w-4xl mx-auto bg-gray-50 border border-gray-200 shadow-xl rounded-xl overflow-hidden my-4">
      {/* Header */}
      <div className="bg-slate-800 p-4 text-white flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold tracking-wide">REAL ESTATE AI CHATBOT</h1>
          <p className="text-xs text-slate-400">RAG + SQLite Plugin Enabled</p>
        </div>

        {/* CHANGED: Grouped the Session ID and the new Reset Button together */}
        <div className="flex items-center space-x-3">
          {sessionId && (
            <span className="text-xs bg-slate-700 px-2 py-1 rounded text-slate-300">
              Session: {sessionId.substring(0, 8)}...
            </span>
          )}
          <button
            onClick={handleClearSession}
            disabled={isLoading}
            className="text-xs bg-slate-700 hover:bg-red-600 text-white px-3 py-1.5 rounded transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            title="Start a new conversation"
          >
            Reset Chat
          </button>
        </div>
      </div>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[75%] rounded-lg p-3 text-sm whitespace-pre-wrap leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-none shadow-md'
                  : 'bg-white text-slate-800 border border-gray-200 rounded-bl-none shadow-sm'
              }`}
            >
              {msg.text === '' && isLoading && index === messages.length - 1 ? (
                <span className="inline-flex items-center space-x-1">
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></span>
                  <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></span>
                </span>
              ) : (
                msg.text
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Tray */}
      <form onSubmit={handleSend} className="p-4 bg-white border-t border-gray-200 flex space-x-3">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
          placeholder="Ask about properties, tours, or assigned agents..."
          className="flex-1 border border-gray-300 text-slate-900 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2 rounded-lg transition-colors shadow disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Typing...' : 'Send'}
        </button>
      </form>
    </div>
  );
}