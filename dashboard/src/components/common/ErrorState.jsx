import { AlertCircle } from 'lucide-react';

export default function ErrorState({ message = 'An error occurred while loading data.', onRetry }) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
      <AlertCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
      <p className="text-red-700 font-medium mb-2">{message}</p>
      <p className="text-red-600 text-sm mb-4">Please try again later or contact support if the issue persists.</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn-primary bg-red-600 hover:bg-red-700"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
