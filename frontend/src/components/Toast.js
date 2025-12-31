import React, { useEffect } from 'react';
import { CheckCircle, XCircle, X } from 'lucide-react';

const Toast = ({ message, type = 'success' }) => {
  useEffect(() => {
    // Auto-remove after 3 seconds (handled by parent, but this is a backup)
  }, []);

  const bgColor = type === 'success' ? 'bg-green-500' : 'bg-red-500';
  const Icon = type === 'success' ? CheckCircle : XCircle;

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-slide-up">
      <div
        className={`${bgColor} text-white px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 min-w-[300px] max-w-md`}
      >
        <Icon size={20} className="flex-shrink-0" />
        <p className="flex-1">{message}</p>
      </div>
    </div>
  );
};

export default Toast;

