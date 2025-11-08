import React, { useEffect } from 'react';
import { useHotkeys } from 'react-hotkeys-hook';
import { useDashboardStore } from './store/useDashboardStore';
import Dashboard from './components/Dashboard';
import CommandPalette from './components/CommandPalette';
import TemplateModal from './components/TemplateModal';
import { Toaster } from './components/ui/Toaster';

function App() {
  const { showCommandPalette, toggleCommandPalette } = useDashboardStore();

  // Global keyboard shortcuts
  useHotkeys('mod+k', (e) => {
    e.preventDefault();
    toggleCommandPalette();
  });

  useHotkeys('mod+g', (e) => {
    e.preventDefault();
    // Export to Google Docs - will be implemented
    console.log('Export to Google Docs');
  });

  return (
    <div className="min-h-screen bg-editor-bg text-gray-200">
      <Dashboard />
      {showCommandPalette && <CommandPalette />}
      <TemplateModal />
      <Toaster />
    </div>
  );
}

export default App;
