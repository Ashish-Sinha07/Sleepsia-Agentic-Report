import { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle, Sparkles } from 'lucide-react';

const AIAssistant = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m the Sleepsia AI Business Assistant. Ask me anything about your business metrics, sales performance, or recommendations.' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/ai-assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMessage })
      });

      if (!response.ok) throw new Error('Failed to get response');
      const data = await response.json();

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response || 'I could not generate a response. Please try again.'
      }]);
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-white to-slate-50 h-full flex flex-col relative overflow-hidden">
      {/* Animated background blobs */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 right-1/3 w-80 h-80 bg-violet-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-fuchsia-300/10 rounded-full mix-blend-multiply filter blur-3xl animate-blob animation-delay-2000"></div>
      </div>

      <div className="relative z-10 flex flex-col h-full">
        {/* Header */}
        <div className="mb-8 group">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-1 h-8 bg-gradient-to-b from-violet-600 to-fuchsia-600 rounded-full"></div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-violet-700 via-fuchsia-600 to-violet-800 bg-clip-text text-transparent group-hover:from-violet-800 group-hover:via-fuchsia-700 group-hover:to-violet-900 transition-all duration-300 flex items-center gap-2">
              <Sparkles className="w-8 h-8 text-violet-600" />
              AI Business Assistant
            </h1>
          </div>
          <p className="text-gray-600 mt-3 group-hover:text-gray-800 transition-colors text-sm ml-4">💬 Ask business questions and get AI-powered insights</p>
        </div>

        {/* Chat Container */}
        <div className="flex-1 bg-gradient-to-br from-white via-violet-50/30 to-white rounded-3xl shadow-2xl shadow-violet-300/30 border-2 border-violet-200/50 overflow-hidden flex flex-col backdrop-blur-sm"
          style={{ animation: 'fadeInUp 0.8s ease-out 0.2s both' }}
        >
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-8 space-y-5">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeInMessage`}
                style={{
                  animation: `fadeInUp 0.4s ease-out ${0.05 * i}s both`
                }}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-6 py-4 rounded-2xl transition-all duration-300 shadow-lg ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white shadow-violet-300/40 hover:shadow-violet-400/60 hover:scale-105'
                      : 'bg-gradient-to-br from-gray-100 via-slate-100 to-gray-100 text-gray-900 border border-gray-200/60 shadow-gray-300/40 hover:shadow-gray-400/60 hover:scale-105'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                  <div className={`text-xs mt-2 opacity-70 ${msg.role === 'user' ? 'text-violet-100' : 'text-gray-600'}`}>
                    {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start animate-fadeInMessage">
                <div className="bg-gradient-to-r from-gray-100 to-slate-100 text-gray-900 px-6 py-4 rounded-2xl shadow-lg shadow-gray-300/40 border border-gray-200/60 backdrop-blur-sm">
                  <div className="flex space-x-3">
                    <div className="w-3 h-3 bg-violet-600 rounded-full animate-bounce"></div>
                    <div className="w-3 h-3 bg-violet-600 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                    <div className="w-3 h-3 bg-violet-600 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form onSubmit={handleSendMessage} className="border-t-2 border-violet-200/50 p-6 flex gap-3 bg-gradient-to-r from-violet-50/50 via-white to-fuchsia-50/50 backdrop-blur-sm">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything about your business..."
              className="flex-1 px-5 py-3 border-2 border-violet-200/60 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-violet-500 transition-all duration-300 bg-white/80 placeholder-gray-500 text-gray-900 font-medium"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-xl flex items-center gap-2 transition-all duration-300 transform hover:scale-110 hover:shadow-lg shadow-violet-400/40 font-bold disabled:cursor-not-allowed"
            >
              <Send className="w-5 h-5" />
              <span className="hidden sm:inline">Send</span>
            </button>
          </form>
        </div>

        {/* Quick Tips */}
        {messages.length === 1 && (
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { emoji: '📊', title: 'Sales Performance', desc: 'Ask about sales trends and metrics' },
              { emoji: '💹', title: 'Profit Analysis', desc: 'Inquire about profitability data' },
              { emoji: '🎯', title: 'Recommendations', desc: 'Get actionable insights' }
            ].map((tip, i) => (
              <div
                key={i}
                className="bg-gradient-to-br from-white via-violet-50/30 to-white rounded-2xl p-4 border-2 border-violet-200/50 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 cursor-pointer group"
                style={{
                  animation: `fadeInUp 0.6s ease-out ${0.1 + i * 0.1}s both`
                }}
              >
                <p className="text-2xl mb-2 group-hover:scale-125 transition-transform">{tip.emoji}</p>
                <p className="font-bold text-gray-900 text-sm">{tip.title}</p>
                <p className="text-xs text-gray-600 mt-1">{tip.desc}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <style>{`
        @keyframes fadeInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animate-fadeInMessage {
          animation: fadeInUp 0.4s ease-out both;
        }
      `}</style>
    </div>
  );
};

export default AIAssistant;
