# Sleepsia AI Business Assistant Guide

## Overview

The Sleepsia AI Business Assistant is an intelligent, conversational interface powered by Claude AI that helps you analyze business data, answer questions, and get actionable insights from your e-commerce analytics.

**Key Features:**
- 🤖 Natural language understanding with Claude AI
- 💬 Multi-turn conversations with context awareness
- 📊 Real-time data analysis and insights
- 🎯 Actionable recommendations
- 🔄 Fallback support when Claude is unavailable

## Setup

### 1. Install Dependencies

First, ensure you have the required Python packages installed:

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Claude API Key

The AI assistant requires an Anthropic API key to function. Get your key from [https://console.anthropic.com/](https://console.anthropic.com/)

Add to your `.env` file:

```env
ANTHROPIC_API_KEY=sk_your_api_key_here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

### 3. Start the Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the Frontend

```bash
cd dashboard
npm install
npm run dev
```

## Features

### Natural Language Questions

Ask business questions in plain English. The AI assistant understands intent and provides data-driven answers.

**Example Questions:**
- "Which platform is most profitable?"
- "Which products are losing money?"
- "What is my average profit margin trend?"
- "Which warehouse needs replenishment?"
- "Compare Amazon and Flipkart performance"
- "How are my advertising metrics looking?"
- "What's driving my return rate?"

### Available Analysis Tools

The AI assistant has access to the following analysis tools:

#### 1. Platform Performance (`get_platform_metrics`)
- Revenue by platform
- Profit margins by platform
- Sales volume comparison
- Supported platforms: Amazon, Flipkart, Blinkit, Myntra, JioMart

#### 2. Product Analysis (`get_product_metrics`)
- Top profitable products
- Revenue by product
- Product count by platform
- Loss-making products identification

#### 3. Profitability Analysis (`get_profitability_analysis`)
- Average profit margins
- Profit trends
- Cost structure breakdown
- Margin ranges (min/max)

#### 4. Advertising Metrics (`get_advertising_metrics`)
- Return on Ad Spend (ROAS)
- Advertising Cost of Sale (ACOS)
- Ad spend allocation
- Platform-wise advertising performance

#### 5. Inventory Status (`get_inventory_status`)
- Stock levels by warehouse
- Days of cover forecast
- SKU counts by location
- Warehouse health assessment
- Locations: Delhi NCR, Jaipur, Mumbai, Bengaluru, Hyderabad

#### 6. Quality Metrics (`get_quality_metrics`)
- Return rates
- Cancellation rates
- Quality trends
- Impact on customer satisfaction

#### 7. KPI Summary (`get_kpi_summary`)
- Overall business metrics
- Total revenue and profit
- Order and unit counts
- Performance indicators

### Conversation Context

Sessions maintain conversation history for up to 10 messages. This allows the AI to understand follow-up questions without losing context.

**Example Flow:**
```
User: "Which products are losing money?"
AI: "Your bottom performers are... [details]"

User: "Can you recommend how to fix this?"
AI: [AI remembers the previous context and provides targeted recommendations]
```

### Confidence Scores

Each response includes a confidence score (0-1) indicating how reliable the answer is based on:
- Data availability
- Question clarity
- Query complexity

### Data Sources

All recommendations cite their sources:
- `Sleepsia Analytics Database` - Real business data
- `vw_daily_kpi_summary` - KPI views
- `vw_platform_performance` - Platform metrics
- `vw_product_performance` - Product metrics
- `vw_inventory_health` - Inventory data

## Usage Tips

### 1. Be Specific
**Better:** "Which platform has the best ROAS and how does it compare?"
**Not as good:** "Tell me about platforms"

### 2. Ask Follow-up Questions
Use the AI's understanding of previous context:
```
Q1: "Which warehouse has the least inventory?"
Q2: "How many days until it stockouts?"  ← AI remembers the warehouse
Q3: "Should I prioritize this one?"
```

### 3. Use Suggested Questions
The UI provides pre-loaded suggested questions to get started:
- Click any suggested question to auto-fill the input
- Modify it if you need variations

### 4. Clear Chat When Needed
Click "Clear Chat" to start a fresh conversation without context from previous questions.

### 5. Copy Answers
Hover over an AI response and click the copy icon to copy the answer to your clipboard.

## Architecture

### Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── ai_assistant.py          # API endpoints
│   ├── services/
│   │   └── ai_assistant_service.py      # Core AI logic
│   ├── config.py                         # Configuration
│   └── database.py                       # Database connection
└── requirements.txt
```

### AI Processing Pipeline

```
User Question
    ↓
API Endpoint (/api/ai/ask)
    ↓
Session Management (conversation history)
    ↓
Claude Intent Understanding
    ↓
Tool Selection & Execution
    ↓
Database Queries
    ↓
Claude Response Synthesis
    ↓
Recommendation Extraction
    ↓
Response to User
```

## Error Handling

### No Claude API Key
If `ANTHROPIC_API_KEY` is not configured, the system automatically falls back to keyword-based analysis.

**Detection:**
```python
CLAUDE_AVAILABLE = bool(settings.ANTHROPIC_API_KEY)
```

### Tool Execution Errors
Each tool has error handling and returns structured results:
```json
{
  "error": "Error message",
  "data": null
}
```

### Database Connection Issues
The AI assistant gracefully handles database errors and provides user-friendly messages.

## Performance Considerations

### Response Times
- Simple queries: 1-3 seconds
- Complex multi-tool queries: 5-10 seconds
- With conversation history: Minimal overhead (< 1 second)

### Token Usage
Claude 3.5 Sonnet is cost-efficient for business analytics:
- System prompt: ~800 tokens
- Average question: 100-200 tokens
- Average response: 300-500 tokens

### Conversation History
- Stores last 10 messages per session
- Automatically managed to prevent token bloat
- Session IDs are unique per browser tab

## Troubleshooting

### Issue: "I don't have sufficient data"
**Cause:** The question isn't matching any of the available data domains
**Solution:** Rephrase using keywords like "platform", "product", "profit", "advertising", "inventory"

### Issue: Low confidence score (< 50%)
**Cause:** Complex or ambiguous question
**Solution:** 
- Break into multiple questions
- Be more specific about what you want to analyze
- Use suggested questions as templates

### Issue: Backend API connection error
**Cause:** Backend server not running
**Solution:**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Issue: Claude API error
**Cause:** Invalid or expired API key
**Solution:**
1. Generate new key at https://console.anthropic.com/
2. Update `.env` file
3. Restart backend

## Advanced Usage

### Custom Tools Extension

To add new analysis tools:

1. **Define the tool in `_get_tool_definitions()`:**
```python
{
    "name": "my_custom_tool",
    "description": "What this tool does",
    "input_schema": { ... }
}
```

2. **Implement the executor:**
```python
@staticmethod
def _execute_tool(db: Session, tool_name: str, tool_input: Dict) -> Dict:
    elif tool_name == "my_custom_tool":
        return AIAssistantService._my_custom_tool(db, tool_input)
```

3. **Implement the tool logic:**
```python
@staticmethod
def _my_custom_tool(db: Session, tool_input: Dict) -> Dict:
    # Your implementation
    return { ... }
```

### Session Management

Sessions maintain conversation history for contextual awareness:

```javascript
// Frontend: Session ID is automatically generated
const sessionId = `session-${Date.now()}-${random()}`;

// Pass to API
const response = await aiAssistantApi.askQuestion(
    question, 
    context, 
    sessionId  // Enable conversation history
);
```

## Best Practices

### For Users
1. **Start broad, then narrow down** - "Tell me about platform performance" → "Focus on Amazon"
2. **Ask for specific metrics** - Better: "profit margin" vs "how are we doing"
3. **Use follow-ups for depth** - Build on previous answers
4. **Check confidence scores** - High confidence (>80%) for critical decisions

### For Implementation
1. **Always validate database responses** - Check for NULL/empty results
2. **Provide context in Claude prompts** - Include schema information
3. **Test with real data** - Use actual business scenarios
4. **Monitor token usage** - Track API costs
5. **Keep conversation history lean** - Prevent token overflow

## Metrics Reference

### Profitability Metrics
- **Revenue**: Total sales value
- **Profit**: Revenue minus all costs
- **Profit Margin**: Profit as % of revenue
  - Healthy: 15-30%
  - Concerning: < 10%

### Advertising Metrics
- **ROAS** (Return on Ad Spend): Revenue generated per rupee spent
  - Excellent: > 5x
  - Good: 3-5x
  - Poor: < 2x
- **ACOS** (Ad Cost of Sale): Ad spend as % of ad sales
  - Good: < 30%
  - Problematic: > 50%

### Inventory Metrics
- **Days of Cover**: How many days inventory will last
- **Low Stock**: < 5 days
- **Critical**: < 2 days

### Quality Metrics
- **Return Rate**: % of sold units returned
  - Healthy: 5-15%
  - High: > 20%
- **Cancellation Rate**: % of orders cancelled
  - Healthy: < 5%
  - High: > 10%

## Support

For issues or feature requests:
1. Check the troubleshooting section above
2. Review API logs in backend console
3. Check Claude API status at https://status.anthropic.com/
4. Verify database connection and schema

## Future Enhancements

Planned features for the AI assistant:
- [ ] Custom metric definitions
- [ ] Scheduled reports with AI insights
- [ ] Competitor analysis
- [ ] Anomaly detection and alerts
- [ ] Predictive recommendations
- [ ] Multi-language support
- [ ] Mobile app integration
- [ ] Export conversations to PDF
