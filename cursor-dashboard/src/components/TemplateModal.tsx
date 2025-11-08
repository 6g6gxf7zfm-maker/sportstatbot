import React from 'react';
import { useDashboardStore } from '@/store/useDashboardStore';
import { StoryTemplate } from '@/types';
import { FileText, Eye, Newspaper, TrendingUp } from 'lucide-react';

const templates: Array<{
  id: StoryTemplate;
  name: string;
  description: string;
  icon: React.ReactNode;
  estimatedLength: string;
}> = [
  {
    id: 'digest',
    name: 'Daily Digest',
    description: 'Comprehensive overview of all games, trends, and key performances',
    icon: <Newspaper size={32} />,
    estimatedLength: '800-1200 words',
  },
  {
    id: 'preview',
    name: 'Game Preview',
    description: 'Detailed preview of upcoming matchups with key storylines',
    icon: <Eye size={32} />,
    estimatedLength: '400-600 words',
  },
  {
    id: 'feature',
    name: 'Feature Story',
    description: 'In-depth analysis of a trend, player, or team storyline',
    icon: <FileText size={32} />,
    estimatedLength: '600-900 words',
  },
  {
    id: 'betting',
    name: 'Betting Snapshot',
    description: 'Betting insights, odds analysis, and recommendations',
    icon: <TrendingUp size={32} />,
    estimatedLength: '300-500 words',
  },
];

function TemplateModal() {
  const {
    showTemplateModal,
    toggleTemplateModal,
    activeLeague,
    addToQueue,
  } = useDashboardStore();

  if (!showTemplateModal) return null;

  const handleSelectTemplate = (template: StoryTemplate) => {
    const newStory = {
      id: `story-${Date.now()}`,
      title: `New ${template} - ${activeLeague}`,
      template,
      sport: activeLeague,
      status: 'draft' as const,
      content: '',
      dataState: {},
      createdAt: new Date(),
      updatedAt: new Date(),
      wordCount: 0,
    };
    addToQueue(newStory);
    toggleTemplateModal();
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) toggleTemplateModal();
      }}
    >
      <div className="bg-sidebar-bg rounded-lg shadow-2xl border border-gray-700 w-full max-w-4xl p-8">
        <h2 className="text-2xl font-bold text-gray-200 mb-2">
          Choose Story Template
        </h2>
        <p className="text-gray-400 mb-6">
          Select a template to start creating your {activeLeague} story
        </p>

        <div className="grid grid-cols-2 gap-4">
          {templates.map((template) => (
            <button
              key={template.id}
              onClick={() => handleSelectTemplate(template.id)}
              className="flex flex-col items-start p-6 bg-editor-bg hover:bg-gray-800 border border-gray-700 hover:border-accent rounded-lg transition-all text-left group"
            >
              <div className="text-accent mb-4 group-hover:scale-110 transition-transform">
                {template.icon}
              </div>
              <h3 className="text-lg font-semibold text-gray-200 mb-2">
                {template.name}
              </h3>
              <p className="text-sm text-gray-400 mb-3">
                {template.description}
              </p>
              <span className="text-xs text-gray-500">
                {template.estimatedLength}
              </span>
            </button>
          ))}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={toggleTemplateModal}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

export default TemplateModal;
