import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { FilterProvider } from './context/FilterContext';
import Layout from './components/layout/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import PlatformAnalysis from './pages/PlatformAnalysis';
import ProductAnalysis from './pages/ProductAnalysis';
import Advertising from './pages/Advertising';
import Profitability from './pages/Profitability';
import Inventory from './pages/Inventory';
import Alerts from './pages/Alerts';
import AIAssistant from './pages/AIAssistant';
import Reports from './pages/Reports';

function App() {
  return (
    <FilterProvider>
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
          </Route>
        </Routes>
      </BrowserRouter>
    </FilterProvider>
  );
}

export default App;
