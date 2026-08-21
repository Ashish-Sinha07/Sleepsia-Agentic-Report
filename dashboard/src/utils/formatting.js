export const formatCurrency = (value) => {
  if (value == null) return '₹0';
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
  return `₹${value.toLocaleString('en-IN')}`;
};

export const formatPercentage = (value) => {
  if (value == null) return '0.00%';
  return `${parseFloat(value).toFixed(2)}%`;
};

export const formatROAS = (value) => {
  if (value == null) return '-';
  return `${parseFloat(value).toFixed(2)}x`;
};

export const formatACOS = (value) => {
  if (value == null) return '-';
  return `${parseFloat(value).toFixed(2)}%`;
};

export const formatUnits = (value) => {
  if (value == null) return '0';
  if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(2)}K`;
  return `${value}`;
};

export const formatNumber = (value) => {
  if (value == null) return '0';
  return value.toLocaleString('en-IN');
};

export const getChangeIndicator = (currentValue, previousValue) => {
  if (!currentValue || !previousValue) return { value: 0, direction: 'neutral', display: '0%' };
  const change = ((currentValue - previousValue) / previousValue) * 100;
  return {
    value: change,
    direction: change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral',
    display: `${change > 0 ? '+' : ''}${change.toFixed(1)}%`,
  };
};

export const getStatusColor = (status) => {
  const statusMap = {
    HEALTHY: 'success',
    EXCELLENT: 'success',
    LOW_MARGIN: 'warning',
    LOW: 'warning',
    LOSS: 'error',
    CRITICAL: 'error',
    STOCKOUT: 'error',
    INEFFICIENT: 'error',
    REVIEW: 'warning',
    EFFICIENT: 'success',
  };
  return statusMap[status] || 'info';
};
