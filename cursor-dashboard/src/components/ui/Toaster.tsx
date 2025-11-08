import React from 'react';

export function Toaster() {
  // This is a placeholder - in production you'd use a library like react-hot-toast or sonner
  return <div id="toast-container" className="fixed top-4 right-4 z-50" />;
}

export function toast(message: string) {
  console.log('Toast:', message);
  // Implementation would create and display toast notifications
}
