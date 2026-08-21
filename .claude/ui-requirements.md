# Sleepsia Agentic Reporting System
# UI Requirements

## 1. Frontend Technology

The frontend must be built using:

- React.js
- Tailwind CSS
- Vite
- React Router
- Axios or Fetch API
- Recharts or Apache ECharts for charts
- Leaflet / React Leaflet for warehouse map
- Lucide React for icons

The frontend must NOT use Streamlit.

The frontend must communicate with the backend through REST APIs.

Architecture:

React.js
    ↓
REST API
    ↓
FastAPI
    ↓
Analytics Services
    ↓
MySQL


---

# 2. UI Design Goal

The application should look like a professional enterprise Business Intelligence and Financial Analytics platform.

The design should prioritize:

- Management readability
- Financial visibility
- Interactive analytics
- Fast navigation
- Clear alerts
- Actionable insights
- Consistent visual hierarchy

The UI should not look like a basic CRUD application.

It should resemble a modern analytics product/dashboard.

---

# 3. Frontend Project Structure

Recommended structure:

frontend/

├── src/
│   ├── components/
│   │   ├── layout/
│   │   ├── common/
│   │   ├── charts/
│   │   ├── tables/
│   │   ├── filters/
│   │   ├── kpi/
│   │   ├── alerts/
│   │   ├── warehouse/
│   │   └── ai/
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── PlatformAnalysis.jsx
│   │   ├── ProductAnalysis.jsx
│   │   ├── Advertising.jsx
│   │   ├── Profitability.jsx
│   │   ├── Inventory.jsx
│   │   ├── Alerts.jsx
│   │   ├── AIAssistant.jsx
│   │   └── Reports.jsx
│   │
│   ├── services/
│   │   ├── api.js
│   │   ├── analyticsApi.js
│   │   ├── inventoryApi.js
│   │   ├── reportsApi.js
│   │   └── aiApi.js
│   │
│   ├── hooks/
│   ├── context/
│   ├── utils/
│   ├── constants/
│   ├── App.jsx
│   └── main.jsx
│
├── public/
├── package.json
├── tailwind.config.js
└── vite.config.js


---

# 4. Application Layout

Use a persistent application shell.

Recommended layout:

┌──────────────────────────────────────────────────────┐
│ Header                                               │
│ Sleepsia Analytics    Date Range    User             │
├──────────────┬───────────────────────────────────────┤
│              │                                       │
│ Sidebar      │ Main Content                          │
│              │                                       │
│ Dashboard    │ Page                                  │
│ Platforms    │                                       │
│ Products     │                                       │
│ Advertising  │                                       │
│ Profitability│                                       │
│ Inventory    │                                       │
│ Alerts       │                                       │
│ AI Assistant │                                       │
│ Reports      │                                       │
│              │                                       │
└──────────────┴───────────────────────────────────────┘


---

# 5. Navigation

Required navigation items:

1. Executive Dashboard
2. Platform Analysis
3. Product Analysis
4. Advertising
5. Profitability
6. Inventory & Warehouses
7. Alerts & Opportunities
8. AI Business Assistant
9. Reports

Use React Router.

Routes:

/
 /platforms
 /products
 /advertising
 /profitability
 /inventory
 /alerts
 /assistant
 /reports


---

# 6. Header

The header should contain:

- Sleepsia logo/brand
- Current page name
- Date range selector
- Notification/alert indicator
- AI Assistant shortcut
- User/profile area

Optional:

- Last data refresh timestamp
- Data quality status

Example:

Sleepsia Analytics

Last Updated:
21 Aug 2026, 12:35 PM

[ Date Range ] [ Alerts ] [ AI Assistant ]


---

# 7. Global Filters

Provide reusable filter components.

Required filters:

- Date From
- Date To
- Platform
- Product
- SKU
- Region
- Warehouse

Filters should be available globally where applicable.

Use:

- Dropdown
- Multi-select
- Date picker
- Searchable dropdown

Provide:

Apply Filters
Reset Filters

Filters should update the relevant API requests.

Do not perform filtering only on the frontend when the dataset is large.

Use backend query parameters where appropriate.

Example:

GET /api/kpis?start_date=2026-08-01&end_date=2026-08-21&platform=Amazon


---

# 8. Executive Dashboard

The executive dashboard is the primary management screen.

## KPI Cards

Display:

- Total Revenue
- Net Revenue
- Profit / Contribution
- Profit Margin
- Units Sold
- Orders
- Advertising Spend
- ROAS
- Return Rate
- Cancellation Rate

Each KPI card may show:

- Current value
- Previous-period value
- Percentage change
- Trend indicator
- Short explanation

Example:

Revenue

₹42.5L

↑ 12.4%

vs previous period


---

# 9. Executive Dashboard Charts

Required visualizations:

### Revenue Trend

Line chart.

X-axis:

Date

Y-axis:

Revenue


### Profit Trend

Line/area chart.

Show:

Revenue
Contribution


### Platform Revenue

Bar chart.

Compare:

Amazon
Blinkit
Flipkart
Myntra
JioMart


### Platform Profitability

Bar chart showing:

Platform
Contribution
Profit Margin


### Top Products

Horizontal bar chart.

Show:

Top 10 products by revenue.


### Bottom Products

Horizontal bar chart.

Show:

Bottom 10 products by contribution.


### Revenue Composition

Donut chart:

Organic Sales
Inorganic / Ad-attributed Sales


---

# 10. Platform Analysis Page

Purpose:

Compare the performance of all e-commerce platforms.

Platforms:

- Amazon
- Blinkit
- Flipkart
- Myntra
- JioMart

## KPI Metrics

Display:

- Revenue
- Units
- Orders
- Ad Spend
- Ad Sales
- ROAS
- ACOS
- Contribution
- Profit Margin
- Return Rate
- Cancellation Rate

## Visualizations

Include:

1. Revenue by Platform
2. Profit by Platform
3. ROAS by Platform
4. Margin by Platform
5. Organic vs Inorganic Sales
6. Platform trend

## Comparison Table

Columns:

Platform
Revenue
Units
Orders
Ad Spend
ROAS
ACOS
Contribution
Margin
Returns
Cancellations

Allow sorting.

Allow clicking a platform to drill down.


---

# 11. Product Analysis Page

Purpose:

Understand product-level performance across platforms.

## Filters

- Product
- SKU
- Platform
- Date range

## Metrics

- Revenue
- Units Sold
- Orders
- Product Cost
- Platform Fees
- Advertising Spend
- Contribution
- Profit Margin
- ROAS
- Return Rate
- Cancellation Rate
- Organic Share

## Product Performance Table

Columns:

SKU
Product
Platform
Revenue
Units
Profit
Margin
ROAS
Returns
Cancellations
Status


## Product Opportunity Matrix

Create an interactive scatter plot.

X-axis:

Revenue

Y-axis:

Profit Margin

Bubble size:

Units Sold

Use quadrant interpretation:

High Revenue + High Margin
→ STAR

High Revenue + Low Margin
→ OPTIMIZE

Low Revenue + High Margin
→ GROW

Low Revenue + Low Margin
→ REVIEW


---

# 12. Advertising Page

Purpose:

Understand advertising effectiveness.

## KPIs

- Advertising Spend
- Attributed Sales
- ROAS
- ACOS
- Impressions
- Clicks
- Attributed Orders
- CTR

## Charts

1. Ad Spend Trend
2. Ad Sales Trend
3. ROAS Trend
4. ROAS by Platform
5. ROAS by Product
6. Spend vs Revenue

## Advertising Efficiency Table

Columns:

Platform
SKU
Product
Ad Spend
Ad Sales
ROAS
ACOS
Orders
Status


## Status

Efficient
Review
Inefficient


---

# 13. Profitability Page

Purpose:

Identify profitable and unprofitable products and platforms.

## KPI Cards

- Total Revenue
- Total Cost
- Contribution
- Profit Margin
- Profitable Products
- Loss-Making Products

## Charts

- Revenue vs Profit
- Profit by Platform
- Profit by Product
- Margin distribution
- Cost breakdown

## Cost Breakdown

Display:

Product Cost
Platform Fees
Shipping
Payment Fees
Advertising
Other Variable Costs


## Profitability Table

Columns:

SKU
Product
Platform
Revenue
Total Cost
Contribution
Margin
Status


Statuses:

HEALTHY
LOW_MARGIN
LOSS


---

# 14. Inventory & Warehouse Page

Purpose:

Provide operational visibility into stock availability and warehouse health.

## KPI Cards

- Total Inventory
- Stockout SKUs
- Low Stock SKUs
- Critical Warehouses
- Average Days of Cover
- Reorder Required

---

# 15. India Warehouse Map

Use:

React Leaflet + OpenStreetMap

or another lightweight map provider if required.

Display all warehouses using latitude and longitude.

Each warehouse marker should provide hover/click information.

Popup should contain:

Warehouse Name
City
Region
Total Stock
SKU Count
Low Stock SKUs
Stockout SKUs
Average Days of Cover
Warehouse Status


Example:

Warehouse:
Gurgaon Warehouse

Inventory:
24,520 Units

SKUs:
132

Low Stock:
8

Stockout:
2

Days of Cover:
6.4

Status:
LOW


---

# 16. Warehouse Map Interactions

The map should support:

- Zoom
- Pan
- Warehouse selection
- Popup
- Hover tooltip where supported
- Status filtering
- City filtering

Filters:

All
Healthy
Low Stock
Critical
Stockout


Marker behavior:

Healthy:
normal marker

Low:
warning marker

Critical:
critical marker

Stockout:
critical/high-priority marker


---

# 17. Warehouse Detail Panel

When a warehouse is selected, show:

Warehouse information

Inventory summary

Top products

Low-stock products

Stockout products

Days of cover

Recent inventory trend

Replenishment recommendations


---

# 18. Inventory Table

Columns:

Warehouse
City
SKU
Product
Current Stock
Average Daily Demand
Days of Cover
Reorder Point
Recommended Reorder Quantity
Status


Allow:

- Sorting
- Search
- Filtering
- Pagination
- Export


---

# 19. Alerts & Opportunities Page

The page should act as an action center.

Sections:

Critical Alerts
High Priority
Warnings
Opportunities


## Alert Table

Columns:

Severity
Alert Type
Entity
Platform/Warehouse
Metric
Current Value
Threshold
Recommendation
Created At


Example:

CRITICAL

Stockout

SKU:
SLEEP-001

Warehouse:
Gurgaon

Stock:
0

Action:

Replenish immediately.


---

# 20. Alert Cards

Critical alerts should also appear on the Executive Dashboard.

Display:

Critical Alerts: 4

High Priority: 7

Warnings: 12


Clicking an alert should navigate to the relevant analysis page.


---

# 21. AI Business Assistant

The AI Assistant is a core feature of the system.

Create a dedicated page:

/assistant

Also provide a shortcut from the global header.

---

# 22. AI Chat UI

Use a modern conversational interface.

Layout:

┌────────────────────────────────────────────┐
│ AI Business Assistant                      │
├────────────────────────────────────────────┤
│                                            │
│ User: Which platform is most profitable?  │
│                                            │
│ AI: Amazon has the highest contribution... │
│                                            │
│ Evidence                                   │
│ Revenue: ₹42.5L                            │
│ Contribution: ₹8.2L                        │
│ Margin: 19.3%                              │
│                                            │
│ Recommendation                             │
│ Focus on maintaining Amazon profitability. │
│                                            │
├────────────────────────────────────────────┤
│ Ask about your business...          [Send] │
└────────────────────────────────────────────┘


---

# 23. Suggested AI Questions

Display clickable prompts:

- Which platform is most profitable?
- Which products are losing money?
- Which platform has the best ROAS?
- Which warehouse needs replenishment?
- What are today's critical alerts?
- Compare Amazon and Flipkart.
- Which products have declining sales?
- Summarize business performance.
- Why is profitability declining?
- Generate management recommendations.


---

# 24. AI Response UI

AI responses should support:

- Text
- KPI highlights
- Tables
- Recommendations
- Source metrics
- Follow-up questions

Example:

Finding

Amazon has the highest contribution.

Evidence

Revenue: ₹42.5L
Contribution: ₹8.2L
Margin: 19.3%

Recommendation

Prioritize Amazon while monitoring advertising efficiency.


---

# 25. AI Loading State

While the AI is processing:

Show:

Analyzing business data...

Optional stages:

Understanding question
↓
Analyzing business data
↓
Generating recommendation


---

# 26. Reports Page

The Reports page should allow management to:

- Generate Management Report
- Download PDF
- Download Excel
- View report history
- View generation status

Report types:

Management Summary
Platform Report
Product Report
Profitability Report
Inventory Report
Exception Report


---

# 27. Report Generation UI

Example:

Report Type:
[ Management Summary ]

Date Range:
[ 01 Aug 2026 ] - [ 21 Aug 2026 ]

Platform:
[ All ]

[ Generate Report ]


After generation:

Report generated successfully.

[ Download PDF ]
[ Download Excel ]


---

# 28. Data Freshness

Show data freshness information.

Example:

Data Last Updated:

21 Aug 2026
12:35 PM

Status:

Data Available

Optional:

Last successful ingestion
Last validation
Last report generation


---

# 29. Data Quality Indicator

Display a small data quality indicator.

Examples:

Data Quality:
98.7%

or:

✓ Data validated

If issues exist:

⚠ 12 records require attention


---

# 30. Responsive Design

The application must work on:

- Desktop
- Laptop
- Tablet

Desktop is the primary target.

Mobile support is secondary for the MVP.

Use Tailwind responsive utilities.

Avoid fixed widths that break layouts.


---

# 31. Tailwind CSS Guidelines

Use Tailwind CSS for:

- Layout (flexbox, grid)
- Spacing (margins, padding)
- Typography (sizes, weights, colors)
- Cards and containers
- Buttons and interactive elements
- Forms and inputs
- Tables and data display
- Navigation and menus
- Responsive behavior
- Status indicators and badges
- Dark mode support

Tailwind configuration:

- Use `tailwind.config.js` to extend default theme
- Define custom colors matching Sleepsia branding
- Configure spacing scale for consistency
- Set up responsive breakpoints (sm, md, lg, xl, 2xl)
- Enable dark mode if required

Do not:

- Duplicate Tailwind classes across components
- Use inline styles for Tailwind-solvable problems
- Mix Tailwind with custom CSS unless necessary

Create reusable components instead of duplicating classes.

Recommended reusable components:

KpiCard
ChartCard
FilterBar
DataTable
StatusBadge
AlertCard
MetricCard
PageHeader
EmptyState
LoadingState
ErrorState
WarehouseMap
AIChat
RecommendationCard
FormInput
FormSelect
Modal
Dropdown
Tooltip
Spinner


---

# 32. React Component Design

Components should be:

- Small and focused
- Reusable across pages
- Data-driven (props-based)
- Independent and encapsulated
- Easy to test and maintain
- Functional components with hooks

React component patterns:

Use functional components with hooks:

```jsx
function KpiCard({ title, value, change, icon }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-2xl font-bold mt-2">{value}</p>
        </div>
        <div className="text-blue-500">{icon}</div>
      </div>
    </div>
  );
}
```

Use custom hooks for repeated logic:

```jsx
function useFilters() {
  const [filters, setFilters] = useState({});
  // Filter logic here
  return { filters, setFilters };
}
```

Use React Context for global state (filters, auth):

```jsx
const FilterContext = createContext();
function FilterProvider({ children }) {
  const [filters, setFilters] = useState({});
  return (
    <FilterContext.Provider value={{ filters, setFilters }}>
      {children}
    </FilterContext.Provider>
  );
}
```

Avoid putting large amounts of business logic inside UI components.

Business calculations belong to the backend.

---

# 33. React Hooks Usage

Recommended hooks:

- useState: For component state
- useEffect: For side effects (API calls)
- useContext: For global filters/auth
- useCallback: For memoized callbacks
- useMemo: For expensive calculations
- useRef: For DOM references (rare)

Example:

```jsx
function PlatformAnalysis() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { filters } = useContext(FilterContext);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        const response = await analyticsApi.getPlatformPerformance(filters);
        setData(response);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [filters]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <EmptyState />;

  return (
    <div className="space-y-6">
      {/* Component content */}
    </div>
  );
}
```

---

# 34. Component Design

# 35. API Integration

The frontend must communicate with FastAPI via REST endpoints.

Recommended structure:

services/
    api.js (base config, axios instance)
    analyticsApi.js
    inventoryApi.js
    reportsApi.js
    aiApi.js

API base configuration:

```jsx
// services/api.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

apiClient.interceptors.response.use(
  response => response.data,
  error => Promise.reject(error.response?.data || error)
);

export default apiClient;
```

Example API module:

```jsx
// services/analyticsApi.js
import apiClient from './api';

export const analyticsApi = {
  getKPIs: (filters) => 
    apiClient.get('/api/kpis', { params: filters }),
  
  getPlatformPerformance: (filters) => 
    apiClient.get('/api/platform-performance', { params: filters }),
  
  getProductPerformance: (filters) => 
    apiClient.get('/api/product-performance', { params: filters }),
};
```

---

# 36. React State Management

For the MVP:

Prefer simple React state with custom hooks.

State management approach:

1. Component-level state: useState
2. Shared state across pages: Context API
3. Complex async state: TanStack Query (if needed later)

Global filters example:

```jsx
// context/FilterContext.jsx
import { createContext, useState } from 'react';

export const FilterContext = createContext();

export function FilterProvider({ children }) {
  const [filters, setFilters] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    endDate: new Date(),
    platform: 'all',
    product: 'all',
    region: 'all',
  });

  const updateFilters = (newFilters) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  const resetFilters = () => {
    setFilters({
      startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      endDate: new Date(),
      platform: 'all',
      product: 'all',
      region: 'all',
    });
  };

  return (
    <FilterContext.Provider value={{ filters, updateFilters, resetFilters }}>
      {children}
    </FilterContext.Provider>
  );
}
```

For more complex scenarios, optionally use:

TanStack Query for:

- API caching
- Automatic loading/error states
- Background refetching
- Query invalidation
- Optimistic updates


---

# 37. Loading States

Every API-driven component must handle all states:

```jsx
if (loading) return <LoadingState />;
if (error) return <ErrorState message={error} />;
if (!data || data.length === 0) return <EmptyState />;
return <YourContent data={data} />;
```

Loading state patterns:

- Skeleton loaders for structure preview
- Spinners with text for operations
- Progressive loading for large datasets
- Lazy loading for below-fold content

Example:

```jsx
function DataTable({ data, loading, error }) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-12 bg-gray-200 rounded animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {error}
      </div>
    );
  }

  if (!data?.length) {
    return (
      <div className="text-center py-12 text-gray-500">
        No data available for the selected filters.
      </div>
    );
  }

  return <table>{/* Table content */}</table>;
}
```


---

# 38. Error Handling

API failures must display user-friendly messages in React components.

```jsx
async function fetchData() {
  try {
    setLoading(true);
    const response = await analyticsApi.getKPIs(filters);
    setData(response);
    setError(null);
  } catch (err) {
    const message = err?.message || 'Unable to load data. Please try again.';
    setError(message);
    setData(null);
  } finally {
    setLoading(false);
  }
}
```

Error display:

```jsx
function ErrorState({ message, onRetry }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
      <p className="text-red-700 mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
```

Do not expose raw backend stack traces or error details to users.

---

# 39. Empty Data

If a filter produces no results:

Display empty state component:

```jsx
function EmptyState() {
  return (
    <div className="text-center py-12">
      <p className="text-gray-500">
        No data available for the selected filters.
      </p>
      <p className="text-gray-400 text-sm mt-2">
        Try adjusting your date range or filters.
      </p>
    </div>
  );
}
```

Do not render broken charts or incomplete UI when data is unavailable.


---

# 40. React Router Setup

Recommended routing structure:

```jsx
// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import PlatformAnalysis from './pages/PlatformAnalysis';
// ... other imports

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/platforms" element={<PlatformAnalysis />} />
          <Route path="/products" element={<ProductAnalysis />} />
          <Route path="/advertising" element={<Advertising />} />
          <Route path="/profitability" element={<Profitability />} />
          <Route path="/inventory" element={<Inventory />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/assistant" element={<AIAssistant />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

Layout component (persistent header and sidebar):

```jsx
// components/layout/Layout.jsx
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Header />
        <main className="flex-1 overflow-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
```

---

# 41. Forms and Inputs

Form components should use controlled inputs:

```jsx
function FilterBar() {
  const { filters, updateFilters } = useContext(FilterContext);

  const handleChange = (name, value) => {
    updateFilters({ [name]: value });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4 space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <input
          type="date"
          value={filters.startDate}
          onChange={(e) => handleChange('startDate', e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <input
          type="date"
          value={filters.endDate}
          onChange={(e) => handleChange('endDate', e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <select
        value={filters.platform}
        onChange={(e) => handleChange('platform', e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="all">All Platforms</option>
        <option value="amazon">Amazon</option>
        <option value="flipkart">Flipkart</option>
        <option value="blinkit">Blinkit</option>
      </select>
      <div className="flex gap-2">
        <button
          onClick={() => window.location.reload()}
          className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Apply Filters
        </button>
        <button
          onClick={() => updateFilters({})}
          className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
        >
          Reset Filters
        </button>
      </div>
    </div>
  );
}
```

---

# 42. Financial Formatting

Create utility functions for consistent formatting:

```jsx
// utils/formatting.js
export const formatCurrency = (value) => {
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
  return `₹${value.toLocaleString('en-IN')}`;
};

export const formatPercentage = (value) => {
  return `${parseFloat(value).toFixed(2)}%`;
};

export const formatROAS = (value) => {
  return `${parseFloat(value).toFixed(2)}x`;
};

export const formatUnits = (value) => {
  if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(2)}K`;
  return `${value}`;
};
```

Usage in components:

```jsx
import { formatCurrency, formatROAS } from '../utils/formatting';

function KpiCard({ value, type }) {
  const displayValue = type === 'currency' 
    ? formatCurrency(value)
    : type === 'roas'
    ? formatROAS(value)
    : value;

  return <p className="text-2xl font-bold">{displayValue}</p>;
}
```

Large values should be human-readable.

---

# 43. Tables

All important tables should support sorting, search, filtering, and pagination.

React table component pattern:

```jsx
function DataTable({ data, columns, loading }) {
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const sorted = [...data].sort((a, b) => {
    const aVal = a[sortBy] || '';
    const bVal = b[sortBy] || '';
    return sortOrder === 'asc' 
      ? aVal.toString().localeCompare(bVal.toString())
      : bVal.toString().localeCompare(aVal.toString());
  });

  const paginated = sorted.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  if (loading) return <LoadingState />;

  return (
    <div>
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-100 border-b">
            {columns.map(col => (
              <th
                key={col.key}
                onClick={() => handleSort(col.key)}
                className="px-4 py-2 text-left cursor-pointer hover:bg-gray-200"
              >
                {col.label} {sortBy === col.key && (sortOrder === 'asc' ? '↑' : '↓')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {paginated.map((row, idx) => (
            <tr key={idx} className="border-b hover:bg-gray-50">
              {columns.map(col => (
                <td key={col.key} className="px-4 py-3">
                  {col.render ? col.render(row[col.key]) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      <Pagination 
        current={currentPage} 
        total={Math.ceil(sorted.length / itemsPerPage)}
        onChange={setCurrentPage}
      />
    </div>
  );
}
```

For large datasets:

Use server-side pagination with query parameters.

Do not load entire database into browser.

---

# 44. Drill-Down

Implement drill-down navigation using React Router and state:

```jsx
function PlatformAnalysis() {
  const [selectedPlatform, setSelectedPlatform] = useState(null);

  if (selectedPlatform) {
    return (
      <div>
        <button 
          onClick={() => setSelectedPlatform(null)}
          className="mb-4 text-blue-600 hover:underline"
        >
          ← Back to Platforms
        </button>
        <ProductAnalysis platform={selectedPlatform} />
      </div>
    );
  }

  return (
    <div>
      <PlatformGrid 
        onSelectPlatform={setSelectedPlatform}
      />
    </div>
  );
}
```

Drill-down hierarchy:

Platform → Product → SKU → Date

Warehouse → SKU → Inventory Trend

---

# 45. Interactive Features

Recommended interactive features using React:

- Hover tooltips (Recharts/ECharts built-in)
- Click handlers on charts to filter
- Drill-down navigation
- Date range picker (react-datepicker or native)
- Cross-filtering with Context API
- Sortable tables with onClick handlers
- Search with onChange listeners
- Pagination with state
- Expandable rows with conditional rendering
- Warehouse map markers with onClick
- AI follow-up questions as clickable buttons
- Download reports with fetch/blob

Example chart with click-to-filter:

```jsx
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts';

function RevenueChart({ data, onDateClick }) {
  const handleClick = (data) => {
    onDateClick(data.date);
  };

  return (
    <LineChart data={data} onClick={handleClick}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis />
      <Tooltip />
      <Legend />
      <Line type="monotone" dataKey="revenue" stroke="#8884d8" />
    </LineChart>
  );
}
```

---

# 46. Dashboard Performance

Do not fetch unnecessary data.

Use:

- API-level filtering
- Pagination
- Aggregated queries
- Lazy loading
- Query caching where appropriate

Do not query raw transaction-level data for every dashboard component if an analytical aggregation is available.


---

# 47. Accessibility

Use semantic HTML and accessibility best practices:

```jsx
function FilterBar() {
  return (
    <nav className="bg-white shadow p-4" aria-label="Filters">
      <fieldset>
        <legend className="text-lg font-bold">Apply Filters</legend>
        
        <label htmlFor="platform-select">Platform:</label>
        <select id="platform-select" className="...">
          {/* Options */}
        </select>

        <button 
          type="button"
          aria-label="Apply filters"
          className="..."
        >
          Apply
        </button>
      </fieldset>
    </nav>
  );
}
```

Do not rely only on color to communicate status - use text, icons, or patterns.

Use ARIA labels for screen readers:

- `aria-label` for icons
- `aria-describedby` for descriptions
- `role` attributes where semantic HTML is insufficient

Ensure sufficient color contrast (WCAG AA minimum).

---

# 48. Security

Never store in React source code:

- Database credentials
- API keys
- LLM keys
- Secrets

Use environment variables for configuration:

```
# .env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

Access in code:

```jsx
const API_URL = process.env.REACT_APP_API_URL;
```

Frontend environment variables (REACT_APP_*) must only contain values safe for browser exposure.

Backend secrets must remain on the server.

Sanitize user input to prevent XSS:

```jsx
import DOMPurify from 'dompurify';

function Comment({ text }) {
  return <p dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(text) }} />;
}
```

---

# 49. Important Architecture Rule

The React frontend must NOT:

- Connect directly to MySQL
- Execute SQL queries
- Calculate financial metrics
- Apply business rules
- Generate AI responses
- Store sensitive data

The React frontend only:

- Displays data from API
- Collects user filters
- Sends API requests
- Displays charts and analytics
- Displays AI responses
- Initiates report generation
- Handles user interactions

All business logic and calculations must be on the backend.

---

# 50. Frontend-to-Backend Architecture

```
React + Tailwind + Vite
       │
       │ REST API (Axios/Fetch)
       ▼
FastAPI Backend
       │
       ├── Analytics Services
       ├── AI Assistant
       ├── Report Service
       ├── Alert Engine
       ├── Validation Layer
       │
       ▼
MySQL Database
```

---

# 51. Build and Development Setup

Vite configuration:

```javascript
// vite.config.js
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
```

Development commands:

```bash
npm run dev      # Start Vite dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Lint code (ESLint)
npm run format   # Format code (Prettier)
```

---

# 52. Testing React Components

For component testing, use Vitest + React Testing Library:

```jsx
// components/__tests__/KpiCard.test.jsx
import { render, screen } from '@testing-library/react';
import KpiCard from '../KpiCard';

describe('KpiCard', () => {
  it('renders KPI data correctly', () => {
    render(<KpiCard title="Revenue" value="₹42.5L" change="+12.4%" />);
    expect(screen.getByText('Revenue')).toBeInTheDocument();
    expect(screen.getByText('₹42.5L')).toBeInTheDocument();
  });
});
```

Test important UI interactions:

- Filter changes
- API calls and loading states
- Error handling
- Chart rendering
- Navigation

---

# 53. Performance Optimization

React-specific optimizations:

Use React.memo for memoized components:

```jsx
const KpiCard = React.memo(({ value, title }) => (
  <div>
    <p>{title}</p>
    <p>{value}</p>
  </div>
));
```

Use useCallback for event handlers:

```jsx
const handleFilterChange = useCallback((newFilters) => {
  updateFilters(newFilters);
}, [updateFilters]);
```

Use useMemo for expensive computations:

```jsx
const sortedData = useMemo(() => {
  return data.sort((a, b) => a.value - b.value);
}, [data]);
```

Lazy load pages with React.lazy:

```jsx
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Reports = React.lazy(() => import('./pages/Reports'));
```

---

# 54. Dependencies

Core React dependencies:

- react: ^18
- react-dom: ^18
- react-router-dom: ^6
- axios: ^1
- recharts or echarts: for charts
- react-leaflet and leaflet: for maps
- lucide-react: for icons
- tailwindcss: ^3
- vite: ^5

Optional (for complex features):

- @tanstack/react-query: for advanced caching
- zustand: for additional state management
- react-datepicker: for date ranges
- dompurify: for sanitizing HTML

Keep dependencies minimal and update regularly.