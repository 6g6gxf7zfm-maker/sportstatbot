import React, { useState, useCallback } from 'react';
import { Command } from 'cmdk';
import { useDashboardStore } from '@/store/useDashboardStore';
import { CommandItem } from '@/types';
import {
  FileText,
  Download,
  RefreshCw,
  Settings,
  Play,
  Eye,
  FileSpreadsheet,
  Zap,
} from 'lucide-react';

function CommandPalette() {
  const { toggleCommandPalette, toggleTemplateModal } = useDashboardStore();
  const [search, setSearch] = useState('');

  const commands: CommandItem[] = [
    {
      id: 'generate-digest',
      label: 'Generate Digest',
      description: 'Create a comprehensive sports digest',
      icon: 'file-text',
      shortcut: '⌘G D',
      category: 'generate',
      action: async () => {
        toggleTemplateModal();
        toggleCommandPalette();
      },
    },
    {
      id: 'generate-preview',
      label: 'Generate Game Preview',
      description: 'Create an upcoming game preview',
      icon: 'eye',
      shortcut: '⌘G P',
      category: 'generate',
      action: async () => {
        console.log('Generate preview');
        toggleCommandPalette();
      },
    },
    {
      id: 'generate-betting',
      label: 'Generate Betting Snapshot',
      description: 'Create betting insights report',
      icon: 'zap',
      shortcut: '⌘G B',
      category: 'generate',
      action: async () => {
        console.log('Generate betting snapshot');
        toggleCommandPalette();
      },
    },
    {
      id: 'export-docs',
      label: 'Export to Google Docs',
      description: 'Export current story to Google Docs',
      icon: 'download',
      shortcut: '⌘G',
      category: 'export',
      action: async () => {
        console.log('Export to Google Docs');
        toggleCommandPalette();
      },
    },
    {
      id: 'export-markdown',
      label: 'Export as Markdown',
      description: 'Download story as markdown file',
      icon: 'file-spreadsheet',
      category: 'export',
      action: async () => {
        console.log('Export as markdown');
        toggleCommandPalette();
      },
    },
    {
      id: 'run-simulation',
      label: 'Run Game Simulation',
      description: 'Simulate game outcomes with current data',
      icon: 'play',
      shortcut: '⌘R',
      category: 'data',
      action: async () => {
        console.log('Run simulation');
        toggleCommandPalette();
      },
    },
    {
      id: 'refresh-data',
      label: 'Refresh Sports Data',
      description: 'Fetch latest stats and scores',
      icon: 'refresh-cw',
      shortcut: '⌘⇧R',
      category: 'data',
      action: async () => {
        console.log('Refresh data');
        toggleCommandPalette();
      },
    },
    {
      id: 'settings',
      label: 'Open Settings',
      description: 'Configure dashboard preferences',
      icon: 'settings',
      category: 'settings',
      action: () => {
        console.log('Open settings');
        toggleCommandPalette();
      },
    },
  ];

  const getIcon = (iconName: string) => {
    const icons: Record<string, React.ReactNode> = {
      'file-text': <FileText size={16} />,
      download: <Download size={16} />,
      'refresh-cw': <RefreshCw size={16} />,
      settings: <Settings size={16} />,
      play: <Play size={16} />,
      eye: <Eye size={16} />,
      'file-spreadsheet': <FileSpreadsheet size={16} />,
      zap: <Zap size={16} />,
    };
    return icons[iconName] || <FileText size={16} />;
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-start justify-center pt-[20vh] z-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) toggleCommandPalette();
      }}
    >
      <Command
        className="command-palette-enter bg-sidebar-bg rounded-lg shadow-2xl border border-gray-700 w-full max-w-2xl overflow-hidden"
        onKeyDown={(e) => {
          if (e.key === 'Escape') toggleCommandPalette();
        }}
      >
        <div className="flex items-center border-b border-gray-700 px-4">
          <Command.Input
            value={search}
            onValueChange={setSearch}
            placeholder="Type a command or search..."
            className="flex-1 bg-transparent border-0 outline-none py-4 text-gray-200 placeholder-gray-500"
          />
        </div>

        <Command.List className="max-h-96 overflow-auto p-2">
          <Command.Empty className="py-6 text-center text-sm text-gray-500">
            No results found.
          </Command.Empty>

          {['generate', 'export', 'data', 'settings'].map((category) => (
            <Command.Group
              key={category}
              heading={category.charAt(0).toUpperCase() + category.slice(1)}
              className="mb-2"
            >
              {commands
                .filter((cmd) => cmd.category === category)
                .map((command) => (
                  <Command.Item
                    key={command.id}
                    value={command.label}
                    onSelect={() => command.action()}
                    className="flex items-center justify-between px-4 py-3 rounded-md cursor-pointer hover:bg-gray-700 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-accent">
                        {getIcon(command.icon || 'file-text')}
                      </span>
                      <div>
                        <div className="text-sm font-medium text-gray-200">
                          {command.label}
                        </div>
                        <div className="text-xs text-gray-500">
                          {command.description}
                        </div>
                      </div>
                    </div>
                    {command.shortcut && (
                      <kbd className="kbd">{command.shortcut}</kbd>
                    )}
                  </Command.Item>
                ))}
            </Command.Group>
          ))}
        </Command.List>
      </Command>
    </div>
  );
}

export default CommandPalette;
