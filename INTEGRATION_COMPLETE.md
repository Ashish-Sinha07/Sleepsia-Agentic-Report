# Agent Integration Complete - Setup & Testing Guide

## ✅ What's Been Integrated

### Backend Components
1. **AI Assistant Service** (`backend/app/services/ai_assistant_service.py`)
   - Natural language question processing
   - Intent detection for business queries
   - Metric explanations
   - Suggested questions

2. **AI Assistant Routes** (`backend/app/api/routes/ai_assistant.py`)
   - POST `/api/ai/ask` - Answer business questions
   - GET `/api/ai/suggestions` - Get suggested questions
   - POST `/api/ai/explain-metric` - Explain metrics

3. **Report Service** (`backend/app/services/report_service.py`)
   - Executive summary reports
   - Platform analysis reports
   - Product profitability reports
   - Advertising ROI analysis
   - Inventory analysis
   - Management monthly reports

4. **Report Routes** (`backend/app/api/routes/reports.py`)
   - GET `/api/reports` - List reports
   - POST `/api/reports` - Generate new report
   - GET `/api/reports/{id}` - Get report details
   - GET `/api/reports/{id}/download` - Download report
   - POST `/api/reports/{id}/email` - Email report

### Frontend Components
1. **AI Assistant API Service** (`dashboard/src/services/aiAssistantApi.js`)
   - `askQuestion(question, context)` - Send question to backend
   - `getSuggestions()` - Fetch suggested questions
   - `explainMetric(metric)` - Get metric explanation

2. **Enhanced AI Assistant Page** (`dashboard/src/pages/AIAssistant.jsx`)
   - Real API integration (no more mocks)
   - Dynamic suggested questions loading
   - Error handling and display
   - Message formatting with recommendations
   - Confidence scores and data sources

3. **Environment Configuration** (`dashboard/.env.local`)
   - API URL: `http://localhost:8000`
   - Mock data disabled: `VITE_USE_MOCK_DATA=false`

## 🚀 Quick Start

### 1. Start the Backend

**Windows (PowerShell):**
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Start backend on port 8000
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

**macOS/Linux:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Start backend
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend

```bash
cd dashboard
npm install  # if not already done
npm run dev
```

Frontend will be available at: `http://localhost:5173`

### 3. Verify the System

**Check Backend Health:**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}
```

**Check Database Connection:**
```bash
curl http://localhost:8000/ready
# Expected: {"ready": true, "timestamp": "..."}
```

**Check API Documentation:**
Open `http://localhost:8000/docs` in browser (Swagger UI)

## 🧪 Testing the AI Assistant

### Test 1: Load Suggested Questions
```bash
curl http://localhost:8000/api/ai/suggestions
```

Expected Response:
```json
[
  {
    "question": "Which platform is most profitable?",
    "category": "platform_analysis",
    "description": "Compare profit margins across all platforms"
  },
  ...
]
```

### Test 2: Ask a Question
```bash
curl -X POST http://localhost:8000/api/ai/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which products are losing money?",
    "context": null
  }'
```

Expected Response:
```json
{
  "question": "Which products are losing money?",
  "answer": "Your best performing product is ...",
  "confidence": 0.85,
  "data_sources": ["vw_daily_kpi_summary", "Product Performance Data"],
  "recommendations": [
    "Scale leading products",
    "Review cost structure"
  ]
}
```

### Test 3: Explain a Metric
```bash
curl -X POST http://localhost:8000/api/ai/explain-metric \
  -H "Content-Type: application/json" \
  -d '{"metric": "ROAS"}'
```

Expected Response:
```json
{
  "metric": "ROAS",
  "definition": "Return on Ad Spend - revenue generated per rupee spent on ads",
  "formula": "Ad-Attributed Sales / Ad Spend",
  "interpretation": "ROAS > 3 is good. ROAS > 5 is excellent..."
}
```

### Test 4: Generate a Report
```bash
curl -X POST http://localhost:8000/api/reports \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "executive_summary",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "format": "json",
    "include_recommendations": true
  }'
```

Expected Response:
```json
{
  "report_id": "REP-XXXXX",
  "report_type": "executive_summary",
  "created_at": "2024-01-31T...",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "status": "completed",
  "file_size": 12345,
  "download_url": "/api/reports/REP-XXXXX/download?format=json"
}
```

### Test 5: List Reports
```bash
curl http://localhost:8000/api/reports
```

## 🌐 Frontend Testing

### 1. Open AI Assistant Page
- Navigate to: `http://localhost:5173/assistant`
- Should see "AI Business Assistant" heading
- Should see suggested questions loaded from backend

### 2. Click a Suggested Question
- Click "Which platform is most profitable?"
- Should see the question in the input field
- Click "Send"
- Should see AI response with recommendations

### 3. Ask a Custom Question
- Type: "What is my profit margin?"
- Press Enter or click Send
- Should see AI response analyzing your data

### 4. View Metric Explanation
- Type: "explain ROAS"
- Should get explanation of what ROAS is

## 📊 Testing All Dashboard Features

### Executive Dashboard (KPIs)
```bash
curl "http://localhost:8000/api/kpis?start_date=2024-01-01&end_date=2024-01-31"
```

### Platform Performance
```bash
curl "http://localhost:8000/api/platforms?start_date=2024-01-01&end_date=2024-01-31"
```

### Product Performance
```bash
curl "http://localhost:8000/api/product-performance?start_date=2024-01-01&end_date=2024-01-31"
```

### Top Products
```bash
curl "http://localhost:8000/api/product-performance/top?limit=10&sort_by=revenue"
```

### Bottom Products
```bash
curl "http://localhost:8000/api/product-performance/bottom?limit=10"
```

### Inventory
```bash
curl "http://localhost:8000/api/inventory"
```

### Warehouses
```bash
curl "http://localhost:8000/api/warehouses"
```

### Alerts
```bash
curl "http://localhost:8000/api/alerts"
```

## 🔧 Troubleshooting

### Issue: "API request failed" in frontend
**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Check CORS is enabled (it is in the code)
3. Check `.env.local` has correct API URL
4. Check browser console for detailed error

### Issue: "Database connection failed"
**Solution:**
1. Verify MySQL is running: `mysql -u root -p`
2. Check `.env` has correct DATABASE_URL
3. Run: `curl http://localhost:8000/ready`
4. Check backend logs for connection errors

### Issue: "No data returned from API"
**Solution:**
1. Verify data exists in database
2. Check date filters are correct
3. Check platform filters exist in data
4. Run SQL query directly in MySQL to verify data

### Issue: AI Assistant returns placeholder response
**Solution:**
1. Check database views exist:
   - `vw_daily_kpi_summary`
   - `inventory`
   - `sales`
2. Run ETL loader to populate data: `python backend/etl/run_etl.py`
3. Check database logs for errors

## 📁 New Files Created

```
backend/app/
├── api/routes/
│   ├── ai_assistant.py       ✨ NEW
│   └── reports.py            ✨ NEW
├── services/
│   ├── ai_assistant_service.py   ✨ NEW
│   └── report_service.py         ✨ NEW

dashboard/src/
├── services/
│   └── aiAssistantApi.js     ✨ NEW
└── .env.local               ✨ NEW
```

## 🔄 Data Flow Examples

### AI Question Flow
```
User types "Which products are losing money?"
  ↓
Frontend: aiAssistantApi.askQuestion(question)
  ↓
Backend: POST /api/ai/ask
  ↓
AIAssistantService.answer_question()
  ├─ Detect intent: product question
  ├─ Query database for product metrics
  ├─ Analyze profitability
  └─ Generate recommendations
  ↓
Response with answer, confidence, sources, recommendations
  ↓
Frontend displays answer with formatting
```

### Report Generation Flow
```
User clicks "Generate Executive Summary"
  ↓
Frontend: POST /api/reports
  ├─ report_type: "executive_summary"
  ├─ start_date, end_date
  └─ format: "json"
  ↓
Backend: ReportService.generate_report()
  ├─ Collect all KPI data
  ├─ Analyze by platform
  ├─ Analyze by product
  ├─ Generate insights
  └─ Save to reports/REP-XXXXX.json
  ↓
Response with report_id and download URL
  ↓
Frontend can download or email the report
```

## 🎯 Next Steps

1. **Load Real Data**
   - Run ETL: `python backend/etl/run_etl.py`
   - Verify: `curl http://localhost:8000/api/kpis`

2. **Test End-to-End**
   - Open dashboard at `http://localhost:5173`
   - Navigate to each page
   - Test filters and date ranges
   - Ask AI Assistant questions

3. **Integrate More Agents** (Future)
   - Validation Agent for data quality
   - Analysis Agent for anomaly detection
   - Recommendation Agent for optimization
   - Custom reporting agents

4. **Add Report Formatting**
   - PDF generation (reportlab, weasyprint)
   - Excel export (openpyxl, pandas)
   - Email distribution (sendgrid, outlook)

5. **Performance Optimization**
   - Add caching for expensive queries
   - Implement pagination
   - Add background job processing
   - Monitor database performance

## 📞 Support

- **API Docs**: http://localhost:8000/docs
- **Backend Logs**: Check console output
- **Frontend Logs**: Browser console (F12)
- **Database**: MySQL console

## ✨ Architecture Summary

```
┌─────────────────────────────────────────────────┐
│  React Dashboard (http://localhost:5173)       │
│  ├─ AI Assistant                              │
│  ├─ Executive Dashboard                       │
│  ├─ Platform Analysis                         │
│  ├─ Product Performance                       │
│  ├─ Advertising                               │
│  ├─ Inventory                                 │
│  └─ Reports                                   │
└─────────────────────┬───────────────────────────┘
                      │ HTTP/REST
                      ↓
┌─────────────────────────────────────────────────┐
│  FastAPI Backend (http://localhost:8000)       │
│  ├─ /api/ai/* (AI Assistant)                  │
│  ├─ /api/reports/* (Report Generation)        │
│  ├─ /api/kpis (Executive KPIs)                │
│  ├─ /api/platforms (Platform Analysis)        │
│  ├─ /api/product-performance (Products)       │
│  ├─ /api/inventory (Inventory)                │
│  ├─ /api/warehouses (Warehouse Map)           │
│  └─ /api/alerts (Business Alerts)             │
└─────────────────────┬───────────────────────────┘
                      │ SQL Queries
                      ↓
┌─────────────────────────────────────────────────┐
│  MySQL Database                                │
│  ├─ Sales Data                                │
│  ├─ Products                                  │
│  ├─ Advertising                               │
│  ├─ Inventory                                 │
│  ├─ Warehouses                                │
│  └─ Views (KPI Summaries)                     │
└─────────────────────────────────────────────────┘
```

---

**Status**: ✅ Full Agent Integration Complete
**Last Updated**: August 23, 2026
**Ready for**: Testing and deployment
