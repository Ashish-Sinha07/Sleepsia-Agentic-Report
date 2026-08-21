import { useState } from 'react';
import FilterBar from '../components/filters/FilterBar';
import { Send } from 'lucide-react';

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const suggestedQuestions = [
    'Which platform is most profitable?',
    'Which products are losing money?',
    'Which platform has the best ROAS?',
    'Which warehouse needs replenishment?',
    'What are today\'s critical alerts?',
    'Compare Amazon and Flipkart.',
    'Which products have declining sales?',
    'Summarize business performance.',
  ];

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    setTimeout(() => {
      const aiMessage = {
        role: 'assistant',
        content: 'I\'m analyzing your business data. This is a placeholder response. Real AI responses will be integrated from the backend.',
      };
      setMessages((prev) => [...prev, aiMessage]);
      setLoading(false);
    }, 1500);
  };

  const handleSuggestedQuestion = (question) => {
    setInput(question);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Business Assistant</h1>
        <p className="text-gray-600 mt-1">Ask questions about your business performance</p>
      </div>

      <FilterBar />

      <div className="grid grid-cols-3 gap-4">
        {suggestedQuestions.map((question, idx) => (
          <button
            key={idx}
            onClick={() => handleSuggestedQuestion(question)}
            className="text-left p-3 border border-gray-200 rounded-lg hover:bg-sleepsia-50 hover:border-sleepsia-300 transition-colors"
          >
            <p className="text-sm font-medium text-gray-900 hover:text-sleepsia-700">{question}</p>
          </button>
        ))}
      </div>

      <div className="card h-96 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-center">
              <div>
                <p className="text-gray-600 mb-2">No messages yet</p>
                <p className="text-sm text-gray-500">Select a suggested question or type your own</p>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg ${
                    msg.role === 'user'
                      ? 'bg-sleepsia-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{msg.content}</p>
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-2 rounded-lg">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask about your business..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sleepsia-500"
            />
            <button
              onClick={handleSendMessage}
              disabled={loading || !input.trim()}
              className="btn-primary flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
