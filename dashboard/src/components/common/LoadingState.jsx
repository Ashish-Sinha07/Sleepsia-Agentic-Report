import { Loader } from 'lucide-react';

export default function LoadingState({ message = 'Loading data...' }) {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="text-center">
        <Loader className="w-8 h-8 text-sleepsia-600 animate-spin mx-auto mb-3" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
}
