# Quick Start: Agent Integration

Get the Sleepsia Agentic Reporting System up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL 8+ (for full functionality)
- Git

## Step 1: Setup Environment

```bash
# Clone/navigate to project
cd "path/to/Sleepsia-Agentic-Report"

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=mysql+pymysql://your_user:your_pass@localhost:3306/sleepsia_reporting
```

## Step 2: Setup Backend

```bash
# Create Python virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

## Step 3: Setup Frontend (New Terminal)

```bash
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

## Step 4: Access the System

Open your browser:

- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API ReDoc**: http://localhost:8000/redoc

## Step 5: Test the Integration

### Test 1: Check API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Sleepsia Agentic Reporting System"
}
```

### Test 2: Get KPIs
```bash
curl "http://localhost:8000/api/kpis"
```

### Test 3: Check Dashboard
Navigate to http://localhost:5173 - you should see the dashboard with sample data.

## Architecture at a Glance

```
Dashboard (React)
    ↓ HTTP Requests ↓
FastAPI Backend
    ↓ Calls ↓
Agent Orchestrator
    ├── Validation Agent
    ├── Metrics Engine
    ├── Analysis Agent
    ├── Insight Recommendation Agent
    ├── LLM Analysis Agent
    └── Report Agent
    ↓ Queries/Updates ↓
MySQL Database
```

## File Structure

```
backend/
├── app.py                    # FastAPI application
├── config.py               # Configuration
├── routes/                 # API endpoint handlers
│   ├── kpis.py
│   ├── platform_performance.py
│   ├── product_performance.py
│   ├── advertising.py
│   ├── profitability.py
│   ├── inventory.py
│   ├── warehouses.py
│   ├── alerts.py
│   ├── ai_assistant.py
│   └── reports.py
└── services/
    └── agent_orchestrator.py  # Coordinates all agents

agents/                        # Agent implementations
├── validation_agent.py
├── analysis_agent.py
├── insight_recommendation_agent.py
├── llm_analysis_agent.py
└── report_agent.py

dashboard/                     # React frontend
├── src/
│   ├── pages/             # Page components
│   ├── components/        # Reusable components
│   ├── services/          # API client services
│   └── App.jsx
└── vite.config.js
```

## What's Integrated Now

✅ **FastAPI Backend** - Ready to serve API requests
✅ **Agent Orchestrator** - Coordinates all agents
✅ **API Routes** - All endpoints defined with proper structure
✅ **Frontend Config** - Dashboard configured to call backend
✅ **Documentation** - Full integration guide and API docs

## What Needs Implementation

The skeleton is in place. Complete these to fully integrate agents:

1. **Database Connection** (backend/database.py)
   - Connect to MySQL
   - Implement data fetch functions
   - Add query builders

2. **Agent Integration** (backend/services/agent_orchestrator.py)
   - Call agents with real data
   - Process agent outputs
   - Aggregate results

3. **Error Handling**
   - Database errors
   - Agent failures
   - Data validation errors

4. **AI Features** (LLM Integration)
   - Connect to OpenAI/Anthropic
   - Implement question parsing
   - Add conversation state

5. **Report Generation**
   - Render PDF/Excel reports
   - Email distribution
   - Report storage

## Common Issues

### Backend won't start
```
Error: Module 'backend' not found
```
**Solution**: Make sure you're in the root directory, not in the backend folder.

### Frontend can't connect to backend
```
Error: Network error connecting to http://localhost:8000
```
**Solution**: 
1. Check backend is running on port 8000
2. Check CORS is enabled in backend/app.py
3. Reload frontend (F5)

### Port already in use
```
Address already in use
```
**Solution**: Use different port
```bash
# Backend on 8001
python -m uvicorn backend.app:app --port 8001

# Frontend - update .env
VITE_API_URL=http://localhost:8001
```

### Database connection fails
```
MySQL connection refused
```
**Solution**:
1. Check MySQL is running
2. Check credentials in .env
3. Check database exists: `CREATE DATABASE sleepsia_reporting;`

## Next Steps

1. **Load Data**: Run ETL to load sample data into MySQL
2. **Connect Database**: Implement database queries in orchestrator
3. **Test Agents**: Run agent tests to verify functionality
4. **Integrate AI**: Connect LLMAnalysisAgent to OpenAI/Anthropic
5. **Deploy**: Set up production environment

## API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /health | GET | Health check |
| /api/kpis | GET | Executive KPIs |
| /api/platform-performance | GET | Platform metrics |
| /api/product-performance | GET | Product analysis |
| /api/advertising | GET | Ad metrics |
| /api/profitability | GET | Margin analysis |
| /api/inventory | GET | Stock levels |
| /api/warehouses | GET | Warehouse info |
| /api/alerts | GET | Business alerts |
| /api/ai/ask | POST | Ask question |
| /api/reports/generate | POST | Generate report |

See `AGENT_INTEGRATION_GUIDE.md` for detailed documentation.

## Support

For issues or questions:
1. Check the logs (look for ERROR messages)
2. Visit http://localhost:8000/docs for API documentation
3. Review `AGENT_INTEGRATION_GUIDE.md` for architecture details
4. Check agent documentation in `AGENTS.md`

## Production Ready?

Not yet. Before going to production:

- [ ] All database queries implemented
- [ ] All agents fully integrated
- [ ] Error handling for all edge cases
- [ ] Authentication/authorization
- [ ] API rate limiting
- [ ] Request logging and monitoring
- [ ] Performance optimization
- [ ] Load testing
- [ ] Security audit
- [ ] Database backup strategy

Current status: **MVP Foundation - Ready for Development**
