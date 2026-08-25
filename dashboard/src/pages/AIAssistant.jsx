import { useState, useEffect, useRef, useContext } from 'react';
import { Send, AlertCircle, Loader, Trash2, Copy } from 'lucide-react';
import { aiAssistantApi } from '../services/aiAssistantApi';
import { FilterContext } from '../context/FilterContext';

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);
  const [suggestionsLoading, setSuggestionsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const abortControllerRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Get filters from context
  const { filters } = useContext(FilterContext);

  // Default suggestions for fallback
  const defaultSuggestions = [
    'Which platform is most profitable?',
    'Which products are losing money?',
    'Which platform has the best ROAS?',
    'Which warehouse needs replenishment?',
    'What are today\'s critical alerts?',
    'Compare Amazon and Flipkart.',
    'Which products have declining sales?',
    'Summarize business performance.',
  ];

  // Load suggested questions on mount and scroll to bottom on new messages
  useEffect(() => {
    loadSuggestions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadSuggestions = async () => {
    setSuggestionsLoading(true);
    try {
      const suggestions = await aiAssistantApi.getSuggestions();
      const questions = Array.isArray(suggestions)
        ? suggestions.map(s => s.question || s)
        : suggestions?.data?.map(s => s.question || s) || [];

      if (questions.length > 0) {
        setSuggestedQuestions(questions);
      } else {
        setSuggestedQuestions(defaultSuggestions);
      }
    } catch (err) {
      console.error('Failed to load suggestions:', err);
      // Use default suggestions on error
      setSuggestedQuestions(defaultSuggestions);
    } finally {
      setSuggestionsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Cancel any previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller for this request
    abortControllerRef.current = new AbortController();

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    const question = input;
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Build context from filters if available
      const context = filters ? {
        startDate: filters.startDate,
        endDate: filters.endDate,
        platform: filters.platform !== 'all' ? filters.platform : null,
      } : null;

      const response = await aiAssistantApi.askQuestion(question, context, sessionId);

      // Handle different response formats
      const answerText = response?.answer || response?.data?.answer || 'Unable to generate response';
      const recommendations = response?.recommendations || response?.data?.recommendations || [];
      const confidence = response?.confidence || response?.data?.confidence || 0;
      const dataSources = response?.data_sources || response?.data?.data_sources || [];

      // Build message content with recommendations if available
      let aiContent = answerText;
      if (recommendations && recommendations.length > 0) {
        const recText = recommendations.map(r => `• ${r}`).join('\n');
        aiContent += `\n\n**Recommendations:**\n${recText}`;
      }

      const aiMessage = {
        role: 'assistant',
        content: aiContent,
        confidence: Math.round(confidence * 100) / 100,
        sources: dataSources,
        timestamp: new Date().toLocaleTimeString(),
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      // Don't show error if request was aborted
      if (err.name === 'AbortError') {
        console.log('Request cancelled');
        return;
      }

      console.error('AI Assistant Error:', err);

      // Provide user-friendly error message
      let errorMessage = 'Failed to get response from AI assistant';
      if (err.message?.includes('Network')) {
        errorMessage = 'Network error. Please check your connection and try again.';
      } else if (err.message?.includes('timeout')) {
        errorMessage = 'Request timed out. The backend may be busy. Please try again.';
      } else if (err.message?.includes('401')) {
        errorMessage = 'Authentication required. Please check your credentials.';
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);

      const aiMessage = {
        role: 'assistant',
        content: `I encountered an error: ${errorMessage}`,
        isError: true,
        timestamp: new Date().toLocaleTimeString(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    } finally {
      setLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleSuggestedQuestion = (question) => {
    setInput(question);
  };

  const handleRetry = () => {
    if (messages.length > 0) {
      const lastUserMessage = [...messages].reverse().find(m => m.role === 'user');
      if (lastUserMessage) {
        setInput(lastUserMessage.content);
      }
    }
  };

  const handleCopy = (text, index) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const handleClearChat = () => {
    if (window.confirm('Clear all messages? This cannot be undone.')) {
      setMessages([]);
      setError(null);
      setInput('');
    }
  };

  // Cleanup abort controller on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Business Assistant</h1>
          <p className="text-gray-600 mt-1">Ask questions about your business performance. Powered by Groq AI for intelligent analysis.</p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={handleClearChat}
            className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg border border-red-200 transition-colors"
            title="Clear conversation"
          >
            <Trash2 className="w-4 h-4" />
            Clear Chat
          </button>
        )}
      </div>

      {error && (
        <div className="flex gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="font-medium text-red-900">{error}</p>
            <p className="text-sm text-red-700 mt-1">
              Make sure the backend API is running on http://localhost:8000
            </p>
            {messages.length > 0 && (
              <button
                onClick={handleRetry}
                className="text-sm text-red-600 hover:text-red-700 font-medium mt-2 underline"
              >
                Retry Last Question
              </button>
            )}
          </div>
        </div>
      )}

      {suggestionsLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader className="w-5 h-5 text-sleepsia-600 animate-spin" />
          <span className="ml-2 text-gray-600">Loading suggested questions...</span>
        </div>
      ) : suggestedQuestions.length > 0 ? (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Suggested Questions</p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {suggestedQuestions.map((question, idx) => (
              <button
                key={idx}
                onClick={() => handleSuggestedQuestion(question)}
                disabled={loading}
                className="text-left p-3 border border-gray-200 rounded-lg hover:bg-sleepsia-50 hover:border-sleepsia-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <p className="text-sm font-medium text-gray-900 hover:text-sleepsia-700">
                  {question}
                </p>
              </button>
            ))}
          </div>
        </div>
      ) : null}

      <div className="card h-96 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <p className="text-gray-600 mb-2">No messages yet</p>
                <p className="text-sm text-gray-500">Select a suggested question or type your own business question</p>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group`}
              >
                <div
                  className={`max-w-2xl px-4 py-3 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-sleepsia-600 text-white'
                      : msg.isError
                        ? 'bg-red-50 text-red-900 border border-red-200'
                        : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <div className="flex justify-between items-start gap-2">
                    <div className="flex-1">
                      <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                      <div className="flex flex-col gap-1 mt-2">
                        {msg.confidence > 0 && msg.role === 'assistant' && !msg.isError && (
                          <p className="text-xs opacity-70">
                            Confidence: {(msg.confidence * 100).toFixed(0)}%
                          </p>
                        )}
                        {msg.sources && msg.sources.length > 0 && msg.role === 'assistant' && (
                          <p className="text-xs opacity-70">
                            Sources: {msg.sources.join(', ')}
                          </p>
                        )}
                        {msg.timestamp && (
                          <p className="text-xs opacity-50">
                            {msg.timestamp}
                          </p>
                        )}
                      </div>
                    </div>
                    {msg.role === 'assistant' && (
                      <button
                        onClick={() => handleCopy(msg.content, idx)}
                        className="opacity-0 group-hover:opacity-100 transition-opacity p-1.5 hover:bg-white/20 rounded"
                        title="Copy message"
                      >
                        <Copy className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-3 rounded-lg flex gap-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && !loading && handleSendMessage()}
              placeholder="Ask about your business..."
              disabled={loading}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sleepsia-500 disabled:bg-gray-50 disabled:text-gray-500"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              title={loading ? 'Processing request...' : 'Send message (Enter)'}
            >
              {loading ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
              {loading ? 'Processing...' : 'Send'}
            </button>
          </div>
          {loading && (
            <p className="text-xs text-gray-500 mt-2">Processing your question...</p>
          )}
        </div>
      </div>
    </div>
  );
}
