import { getStatusColor } from '../../utils/formatting';

export default function StatusBadge({ status, label }) {
  const statusColor = getStatusColor(status);

  const colorMap = {
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-error',
    info: 'badge-info',
  };

  return (
    <span className={colorMap[statusColor]}>
      {label || status}
    </span>
  );
}
