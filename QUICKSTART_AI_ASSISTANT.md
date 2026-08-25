# Quick Start - AI Business Assistant

## ⚡ 5-Minute Setup

### Step 1: Get Claude API Key (2 minutes)
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Copy your API key
4. Save it - you'll need it in Step 2

### Step 2: Configure the System (2 minutes)

**On Windows:**
```bash
# Navigate to project directory
cd "c:\Agile\Sleepsia Project\Sleepsia-Agentic-Report"

# Create .env file or update existing one
# Add this line:
# ANTHROPIC_API_KEY=sk_your_api_key_here

# Or use PowerShell to set it:
$env:ANTHROPIC_API_KEY = "sk_your_api_key_here"
```

### Step 3: Install Dependencies (1 minute)

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend (if not already done)
cd ..\dashboard
npm install
```

## 🚀 Running the System

### Terminal 1 - Start Backend
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
Uvicorn running on http://0.0.0.0:8000
Press CTRL+C to quit
```

### Terminal 2 - Start Frontend
```bash
cd dashboard
npm run dev
```

You should see:
```
VITE v... ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Open in Browser
Go to: **http://localhost:5173/**

Navigate to **AI Business Assistant** from the sidebar

## 💬 Try It Out

### Test Questions (Copy & Paste)

1. **Simplest Question:**
   ```
   Which platform is most profitable?
   ```

2. **Platform Comparison:**
   ```
   Compare Amazon and Flipkart - which one makes more money?
   ```

3. **Product Analysis:**
   ```
   What are my top 3 most profitable products?
   ```

4. **Problem Identification:**
   ```
   Which products are losing money?
   ```

5. **Ad Performance:**
   ```
   How's my advertising performance? What's my ROAS?
   ```

6. **Inventory Check:**
   ```
   Which warehouse needs urgent restocking?
   ```

7. **Quality Issues:**
   ```
   What's my return rate and should I be worried?
   ```

8. **Follow-up (Test Conversation Memory):**
   ```
   First: "What's my profit margin?"
   Then: "How can I improve this?"
   ```

## ✅ What You Should See

### For Each Question:
✓ **AI Response** - Natural language answer with insights
✓ **Confidence Score** - Trust indicator (should be 80-90%)
✓ **Data Sources** - Where the data came from
✓ **Recommendations** - Actionable next steps

### Example Response:
```
Answer:
Based on your recent data, Amazon is your top platform by 
revenue with ₹2,450,000 in sales. Flipkart has the highest 
profit margin at 22.5%.

Confidence: 87%
Sources: Sleepsia Analytics Database
Recommendations:
• Scale up Amazon campaigns - it's your revenue driver
• Focus marketing efforts on Flipkart for profitability
• Consider the cost-revenue tradeoff for other platforms
```

## 🔍 Testing Features

### Feature 1: Suggested Questions
- See "Suggested Questions" at top
- Click any question to auto-fill the input
- Modify and ask

### Feature 2: Copy Answers
- Hover over AI response
- Click copy icon
- Paste in email, documents, etc.

### Feature 3: Clear Chat
- Click "Clear Chat" button (top right)
- Starts fresh conversation

### Feature 4: Multi-turn Conversation
- Ask a question
- Ask a follow-up without re-context
- AI remembers what you asked before

### Feature 5: Error Handling
- Try asking something unclear: "Tell me everything"
- AI will ask for clarification or suggest better questions

## ⚠️ Troubleshooting

### Backend Not Starting?
```
Error: ModuleNotFoundError: No module named 'anthropic'
→ Solution: pip install anthropic>=0.20.0
```

### Claude API Error?
```
Error: Invalid API key or authentication failed
→ Solution: Check ANTHROPIC_API_KEY in .env or environment
```

### Frontend Connection Error?
```
Error: Failed to connect to http://localhost:8000
→ Solution: Ensure backend is running (see Terminal 1)
```

### Empty/Slow Responses?
```
→ Backend is making database queries
→ Wait 3-5 seconds for response
→ Check backend logs for errors
```

## 📊 What Data Is Available?

The AI can analyze:
- **5 Platforms:** Amazon, Flipkart, Blinkit, Myntra, JioMart
- **Multiple Products:** All SKUs in your database
- **5 Warehouses:** Delhi NCR, Jaipur, Mumbai, Bengaluru, Hyderabad
- **13+ Metrics:** Revenue, Profit, ROAS, ACOS, Return Rate, etc.

## 🎯 Next Steps

After confirming it works:

1. **Review the Guides:**
   - `AI_ASSISTANT_GUIDE.md` - Complete documentation
   - `AI_ASSISTANT_CHANGES.md` - Technical details

2. **Customize for Your Business:**
   - Update suggested questions in code
   - Add custom business rules
   - Integrate with your reporting system

3. **Deploy to Production:**
   - Set up HTTPS
   - Configure CORS for your domain
   - Set up environment variables securely
   - Monitor API usage and costs

4. **Advanced Usage:**
   - Export conversations
   - Build custom dashboards
   - Integrate with alerts system
   - Schedule daily AI reports

## 💡 Pro Tips

1. **Be Specific**: "Show me profitable products on Amazon" works better than "Products"

2. **Use Follow-ups**: "Which warehouse?" → "Show inventory" → "When will it run out?"

3. **Ask Why**: "Why is this losing money?" gets you analysis

4. **Request Format**: "List as bullet points" for structured output

5. **Cross-Tab**: Keep dashboard open, test questions there

## 📞 Getting Help

If something doesn't work:
1. Check backend terminal for error messages
2. Review `AI_ASSISTANT_GUIDE.md` troubleshooting section
3. Verify ANTHROPIC_API_KEY is set correctly
4. Try a simple question like "Which platform is most profitable?"

## 🎉 You're Ready!

The AI Business Assistant is now running. Start asking your business questions naturally!
