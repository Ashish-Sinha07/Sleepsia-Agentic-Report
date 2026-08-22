# Sleepsia Analytics Dashboard

A professional enterprise React-based business intelligence dashboard for unified e-commerce and quick-commerce analytics.

## Setup

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
cd dashboard
npm install
```

### Development

Start the Vite dev server:

```bash
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

Production-ready files will be in `dist/`

## Project Structure

```
src/
├── components/
│   ├── layout/          # Header, Sidebar, Layout
│   ├── common/          # Reusable components (KpiCard, LoadingState, etc.)
│   ├── charts/          # Recharts visualizations
│   ├── filters/         # Filter components
│   └── alerts/          # Alert-related components
├── pages/               # Page components (Dashboard, PlatformAnalysis, etc.)
├── services/            # API clients and mock data
│   ├── api.js           # Axios configuration
│   ├── analyticsApi.js  # Analytics API integration
│   └── mockData.js      # Mock data for development
├── context/             # React Context (FilterContext)
├── utils/               # Utility functions (formatting, etc.)
├── constants/           # Constants
├── App.jsx              # Main app with routing
├── main.jsx             # Entry point
└── index.css            # Global Tailwind styles
```

## Features

### Pages

1. **Executive Dashboard** - KPIs, trends, and key visualizations
2. **Platform Analysis** - Compare performance across Amazon, Flipkart, Myntra, Blinkit, JioMart
3. **Product Analysis** - Product-wise performance breakdown
4. **Advertising** - Advertising effectiveness and ROI analysis
5. **Profitability** - Profit analysis by product and platform
6. **Inventory & Warehouse** - Warehouse status and inventory management
7. **Alerts & Opportunities** - Critical alerts and action items
8. **AI Business Assistant** - AI-powered question answering
9. **Reports** - Report generation and download

### Design

- **Light-first premium enterprise design**
- White/off-white backgrounds with white cards
- Dark navy/charcoal text on light backgrounds
- Sleepsia teal accent color (#4a9fbd)
- Green for positive metrics, amber for warnings, red for critical
- Subtle borders and soft shadows
- Professional typography and spacing

### Components

- **KpiCard** - Display metrics with trend indicators
- **ChartCard** - Wrapper for chart visualizations
- **RevenueChart** - Line and area charts
- **BarChart** - Horizontal and vertical bar charts
- **DonutChart** - Donut/pie chart for composition
- **FilterBar** - Date range and platform filters
- **LoadingState** - Loading indicator
- **ErrorState** - Error message display
- **EmptyState** - No data state
- **StatusBadge** - Status indicators

## API Integration

### Mock Data vs Real API

Currently, the dashboard uses mock data in development. To switch to real FastAPI endpoints:

1. Set `USE_MOCK = false` in `src/services/analyticsApi.js`
2. Ensure FastAPI backend is running on `http://localhost:8000`
3. Update environment variable `REACT_APP_API_URL` in `.env`

### API Endpoints

The frontend expects these FastAPI endpoints:

- `GET /api/kpis` - KPI metrics
- `GET /api/platform-performance` - Platform analytics
- `GET /api/product-performance` - Product analytics
- `GET /api/revenue-chart` - Revenue trend data
- `GET /api/top-products` - Top performing products
- `GET /api/bottom-products` - Lowest performing products
- `GET /api/alerts` - Business alerts
- `GET /api/warehouses` - Warehouse information
- `GET /api/inventory` - Inventory data

Query parameters supported:
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `platform` - Platform filter
- `product` - Product filter
- `sku` - SKU filter
- `region` - Region filter
- `warehouse` - Warehouse filter

## Technologies

- **React 18** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router 6** - Routing
- **Recharts** - Data visualization
- **React Leaflet** - Maps (for warehouse visualization)
- **Lucide React** - Icons
- **Axios** - HTTP client
- **date-fns** - Date utilities

## Key Features

### Global Filters

Filters in the header/sidebar control data across all pages:
- Date range (from/to dates)
- Platform (Amazon, Flipkart, Myntra, Blinkit, JioMart)
- Product
- SKU
- Region
- Warehouse

Filters are managed via React Context and automatically passed to all API calls.

### Responsive Design

- Mobile-first responsive layout
- Desktop optimized (primary target)
- Tailwind responsive utilities

### Performance

- Code splitting ready (Vite)
- Lazy-loaded pages
- Memoized components
- Efficient re-renders with Context API

### Accessibility

- Semantic HTML
- ARIA labels for icons
- Keyboard navigation
- Sufficient color contrast

## Development Notes

### Adding New Pages

1. Create a new `.jsx` file in `src/pages/`
2. Import FilterContext for global filters
3. Import analyticsApi for data fetching
4. Add route to `src/App.jsx`
5. Add navigation item to `src/components/layout/Sidebar.jsx`

### Adding New Components

1. Create component in appropriate `src/components/` subdirectory
2. Use Tailwind classes for styling
3. Import icons from lucide-react
4. Make components reusable and data-driven

### Formatting Values

Use utility functions from `src/utils/formatting.js`:
- `formatCurrency(value)` - ₹ format with Cr/L abbreviations
- `formatPercentage(value)` - Percentage format
- `formatROAS(value)` - ROAS format (x)
- `formatUnits(value)` - Unit abbreviations (M/K)
- `formatNumber(value)` - Localized number format

## Environment Variables

Create `.env` file:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## Testing

Currently, mock data is used for testing. Real API integration testing will be done once FastAPI backend is ready.

## Known Limitations

- Warehouse map visualization not yet implemented (React Leaflet)
- AI Assistant uses placeholder responses
- Some analytics pages are placeholder implementations
- No authentication/authorization currently implemented

## Next Steps

1. Integrate real FastAPI backend
2. Implement warehouse map visualization
3. Implement AI assistant with real backend
4. Add advanced charting features
5. Implement report generation and download
6. Add data export functionality
7. Implement user authentication
8. Add analytics events tracking

## Author

Frontend developed for Sleepsia Agentic Reporting System.
