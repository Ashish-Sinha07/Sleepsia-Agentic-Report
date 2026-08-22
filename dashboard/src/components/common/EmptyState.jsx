import { Database } from 'lucide-react';

export default function EmptyState({ message = 'No data available for the selected filters.' }) {
  return (
    <div className="text-center py-12">
      <Database className="w-12 h-12 text-gray-400 mx-auto mb-3" />
      <p className="text-gray-600 font-medium mb-1">{message}</p>
      <p className="text-gray-500 text-sm">Try adjusting your date range or filters.</p>
    </div>
  );
}
