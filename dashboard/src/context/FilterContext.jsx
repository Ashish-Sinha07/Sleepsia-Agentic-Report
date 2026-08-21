import { createContext, useState, useCallback, useMemo } from 'react';
import { subDays } from 'date-fns';

export const FilterContext = createContext();

export function FilterProvider({ children }) {
  const { startDate, endDate } = useMemo(() => {
    const end = new Date();
    return { startDate: subDays(end, 30), endDate: end };
  }, []);

  const [filters, setFilters] = useState({
    startDate,
    endDate,
    platform: 'all',
    product: 'all',
    sku: 'all',
    region: 'all',
    warehouse: 'all',
  });

  const updateFilters = useCallback((newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({
      startDate,
      endDate,
      platform: 'all',
      product: 'all',
      sku: 'all',
      region: 'all',
      warehouse: 'all',
    });
  }, [startDate, endDate]);

  return (
    <FilterContext.Provider value={{ filters, updateFilters, resetFilters }}>
      {children}
    </FilterContext.Provider>
  );
}
