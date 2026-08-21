# Sleepsia Agent Architecture

## System Overview

Architecture:

```
React Frontend (React.js + Tailwind CSS + Vite)
        ↓
REST API Endpoints
        ↓
Agent/Service Layer (Python FastAPI)
  ├── Validation Agent
  ├── Analytics Services
  ├── Alert Engine
  ├── Report Agent
  └── AI Business Assistant
        ↓
MySQL Database
```

---

## 1. Agent Philosophy

Use agents where reasoning or natural-language interpretation adds value.

Use deterministic services for calculations and business rules.

Do not convert every service into an LLM agent.

Agents are backend components that the React frontend calls via REST APIs.

The frontend is purely a presentation layer that requests data and displays results.

---

# 2. Validation Agent

## Responsibility

Validate incoming business data before analytics.

## Input

- Excel/CSV/API dataset

## Checks

- Required columns
- Data types
- Missing values
- Duplicate records
- Invalid dates
- Invalid SKU
- Invalid platform
- Negative values
- Referential integrity
- Reconciliation

## Output

Structured result:

{
    "status": "PASS|FAIL|WARNING",
    "errors": [],
    "warnings": [],
    "records_processed": 0,
    "records_rejected": 0
}

The validation agent must not perform business recommendations.

---

# 3. Analytics Agent

## Responsibility

Coordinate business analytics.

Capabilities:

- Product performance
- Platform performance
- Sales trends
- Profitability
- Advertising
- Returns
- Cancellations
- Inventory
- Regional performance
- Cross-platform comparison

The actual calculations should be deterministic.

The agent may select the appropriate analytical tool.

---

# 4. Alert Engine

The Alert Engine should primarily be deterministic.

It checks:

- Negative contribution
- Low margin
- Low ROAS
- High ACOS
- High return rate
- High cancellation rate
- Low stock
- Stockout
- Warehouse issues

Output:

{
    "alert_type": "",
    "severity": "",
    "entity": "",
    "metric": "",
    "value": 0,
    "threshold": 0,
    "recommendation": ""
}

---

# 5. Report Agent

## Responsibility

Convert validated analytical results into a management report.

Sections:

1. Executive Summary
2. Overall KPIs
3. Platform Performance
4. Product Performance
5. Advertising
6. Profitability
7. Inventory
8. Warehouse
9. Alerts
10. Recommendations

The report agent must use actual analytics results.

It must not invent metrics.

---

# 6. AI Business Assistant

## Responsibility

Answer runtime natural-language business questions.

Provide business insights and recommendations.

## Frontend Component

React page: `/assistant`

UI Component: `AIAssistant.jsx`

Features:

- Chat-like conversational interface
- Suggested questions displayed as buttons
- Real-time response streaming (optional)
- Evidence display (tables, KPIs)
- Follow-up question suggestions
- Loading states and error handling

## Supported Questions

- What is total revenue?
- Which platform is most profitable?
- Which products are losing money?
- Which product has the best ROAS?
- Which warehouse has low inventory?
- What changed compared with the previous period?
- Which platform should management focus on?
- Why did profitability decline?
- Generate a management summary.
- Summarize inventory health.
- Which products should we focus on?
- What are the top risks?

---

# 7. React Frontend Integration

The React frontend does NOT contain agent logic.

The frontend only:

- Collects user input (questions, filters, selections)
- Displays loading states
- Makes HTTP requests to backend agent endpoints
- Displays agent results in React components
- Handles errors and empty states

API Services in React:

```javascript
// services/aiApi.js
import apiClient from './api';

export const aiApi = {
  askQuestion: (question, filters = {}) =>
    apiClient.post('/api/ai/ask', { question, filters }),
  
  getSuggestedQuestions: () =>
    apiClient.get('/api/ai/suggested-questions'),
  
  getFollowUpQuestions: (context) =>
    apiClient.post('/api/ai/follow-up', { context }),
};

// services/analyticsApi.js
export const analyticsApi = {
  getKPIs: (filters) =>
    apiClient.get('/api/kpis', { params: filters }),
  
  getPlatformPerformance: (filters) =>
    apiClient.get('/api/platform-performance', { params: filters }),
  
  getProductPerformance: (filters) =>
    apiClient.get('/api/product-performance', { params: filters }),
};
```

React component calling AI agent:

```jsx
// pages/AIAssistant.jsx
import { useState, useContext } from 'react';
import { FilterContext } from '../context/FilterContext';
import { aiApi } from '../services/aiApi';

export default function AIAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const { filters } = useContext(FilterContext);

  async function handleAsk() {
    if (!input.trim()) return;

    setLoading(true);
    try {
      const response = await aiApi.askQuestion(input, filters);
      setMessages([
        ...messages,
        { role: 'user', content: input },
        { role: 'assistant', content: response },
      ]);
      setInput('');
    } catch (error) {
      setMessages([
        ...messages,
        { role: 'error', content: 'Failed to get response. Try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h1 className="text-2xl font-bold mb-6">AI Business Assistant</h1>
      
      <div className="mb-6 space-y-4 max-h-96 overflow-y-auto">
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === 'assistant' ? 'bg-blue-50' : 'bg-gray-50'}>
            {/* Message display */}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="Ask about your business..."
          disabled={loading}
          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg"
        />
        <button
          onClick={handleAsk}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {loading ? 'Thinking...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
```

---

# 8. Controlled AI Tools

The assistant should use tools:

get_kpis
get_platform_performance
get_product_performance
get_profitability
get_advertising_performance
get_inventory_health
get_warehouse_details
get_alerts
compare_platforms
compare_products
get_sales_trend
get_management_summary

---

# 9. AI Query Flow

User (React Frontend):

"Which platform is most profitable?"

↓

React component sends HTTP POST to `/api/ai/ask`

↓

FastAPI AI Assistant endpoint

↓

AI understands intent: "get_platform_performance"

↓

Select controlled tool: `get_platform_performance(filters)`

↓

Analytics service (deterministic Python)

↓

SQL query execution

↓

MySQL result

↓

Structured result (JSON)

↓

LLM generates explanation and recommendation

↓

Response sent to React Frontend

↓

React displays response in chat interface

---

# 10. No Unrestricted SQL

The AI must NOT:

- Generate arbitrary SQL and execute it directly
- Modify database records
- Delete records
- Update financial data
- Change business rules
- Modify schemas

The AI should only call approved read-only analytical tools.

---

# 11. Follow-up Questions

The AI should maintain conversation context in the React chat interface.

Example:

User:

"Which platform has the highest revenue?"

Assistant:

"Amazon."

User:

"What about profit?"

The assistant should understand that the comparison is still between the same platforms/date context unless the user changes it.

---

# 12. Unknown Data

If required data is unavailable:

AI response: "I don't have sufficient data to answer that accurately."

This error message is displayed to the user in the React chat interface.

Do not guess or fabricate metrics.

---

# 13. Recommendation Format

Recommendations should contain:

- Finding
- Evidence
- Business Impact
- Recommended Action

Example:

Finding:
ROAS for Product X on Amazon declined.

Evidence:
ROAS decreased from 4.2 to 2.7.

Impact:
Advertising efficiency has deteriorated.

Action:
Review campaign targeting and spend allocation.

Do not claim causality unless the data supports it.

---

# 14. Frontend Pages and Agent Integration

Each React page calls specific backend services/agents:

## Dashboard Page (/)

Calls:

- `/api/kpis` → Analytics Service
- `/api/alerts` → Alert Engine
- `/api/warehouse-summary` → Analytics Service

## Platform Analysis Page (/platforms)

Calls:

- `/api/platform-performance` → Analytics Service
- `/api/platform-comparison` → Analytics Service

## Product Analysis Page (/products)

Calls:

- `/api/product-performance` → Analytics Service
- `/api/product-profitability` → Analytics Service
- `/api/product-matrix` → Analytics Service

## Advertising Page (/advertising)

Calls:

- `/api/advertising/performance` → Analytics Service
- `/api/advertising/roas-analysis` → Analytics Service

## Profitability Page (/profitability)

Calls:

- `/api/profitability` → Analytics Service
- `/api/cost-breakdown` → Analytics Service

## Inventory & Warehouse Page (/inventory)

Calls:

- `/api/inventory/health` → Analytics Service
- `/api/warehouses` → Analytics Service
- `/api/warehouse/<id>/details` → Analytics Service

## Alerts Page (/alerts)

Calls:

- `/api/alerts` → Alert Engine
- `/api/alerts/history` → Alert Engine

## AI Assistant Page (/assistant)

Calls:

- `/api/ai/ask` → AI Business Assistant
- `/api/ai/suggested-questions` → AI Business Assistant
- `/api/ai/follow-up` → AI Business Assistant

## Reports Page (/reports)

Calls:

- `/api/reports/generate` → Report Agent
- `/api/reports/history` → Report Agent
- `/api/reports/<id>/download` → Report Agent

---

# 15. Backend Service Responsibilities

### Validation Agent

- Input: Raw data from Excel/CSV
- Processing: Schema validation, data quality checks
- Output: Validation report
- Called by: Data ingestion pipeline (not user-facing)

### Analytics Services (Deterministic)

- Input: Filters (date, platform, product, etc.)
- Processing: SQL queries, aggregations, metrics calculation
- Output: JSON data structures
- Called by: React dashboard pages, AI Assistant

### Alert Engine (Deterministic)

- Input: Analytics results
- Processing: Threshold checks, alert rule evaluation
- Output: Alert JSON objects
- Called by: Dashboard, Alerts page, Report Agent

### Report Agent

- Input: Selected filters, report type
- Processing: Aggregates analytics results into sections
- Output: Report structure (PDF/Excel)
- Called by: Reports page

### AI Business Assistant

- Input: User question + conversation context
- Processing: Intent understanding, tool selection, response generation
- Output: Natural language response + structured evidence
- Called by: React AI Assistant page

---

# 16. Error Handling in Frontend

React components handle errors from agents/services:

```jsx
async function fetchData() {
  try {
    setLoading(true);
    const response = await analyticsApi.getKPIs(filters);
    setData(response);
  } catch (error) {
    setError(error.message || 'Failed to load data');
  } finally {
    setLoading(false);
  }
}

// Display error to user
if (error) return <ErrorState message={error} />;
```

Error responses from backend should include:

```json
{
  "error": "true",
  "message": "User-friendly error message",
  "code": "ERROR_CODE"
}
```

---

# 17. Authentication (Future)

When authentication is required:

- React Frontend: Store JWT token securely
- API calls: Include Authorization header
- Backend: Validate token before processing

Filter context should include user scope (if multi-tenant).

---

# 18. Monitoring and Observability

Backend agents should log:

- Incoming requests
- Data validation steps
- Tool execution
- Response generation
- Errors and warnings

React Frontend should:

- Log API calls and responses
- Track user interactions
- Monitor loading times
- Report errors to backend logging service (future)