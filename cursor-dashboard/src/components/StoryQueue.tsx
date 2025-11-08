import React from 'react';
import { useDashboardStore } from '@/store/useDashboardStore';
import { format } from 'date-fns';
import { FileText, Clock, CheckCircle, Edit3, Trash2 } from 'lucide-react';

function StoryQueue() {
  const { storyQueue, setCurrentStory, toggleTemplateModal } = useDashboardStore();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'text-green-500';
      case 'in_progress': return 'text-yellow-500';
      case 'published': return 'text-blue-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ready': return <CheckCircle size={16} />;
      case 'in_progress': return <Clock size={16} />;
      case 'published': return <FileText size={16} />;
      default: return <Edit3 size={16} />;
    }
  };

  if (storyQueue.length === 0) {
    return (
      <div className="text-center py-12">
        <FileText size={64} className="mx-auto mb-4 text-gray-600" />
        <h3 className="text-xl font-semibold text-gray-300 mb-2">No stories in queue</h3>
        <p className="text-gray-500 mb-6">
          Create your first story using a template
        </p>
        <button
          onClick={toggleTemplateModal}
          className="px-6 py-3 bg-accent hover:bg-blue-600 rounded-md"
        >
          Create New Story
        </button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-200">Story Queue</h2>
        <button
          onClick={toggleTemplateModal}
          className="px-4 py-2 bg-accent hover:bg-blue-600 rounded-md text-sm"
        >
          + New Story
        </button>
      </div>

      <div className="grid gap-4">
        {storyQueue.map((story) => (
          <div
            key={story.id}
            className="bg-sidebar-bg border border-gray-700 rounded-lg p-6 hover:border-accent transition-colors cursor-pointer"
            onClick={() => setCurrentStory(story)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-200 mb-1">
                  {story.title}
                </h3>
                <div className="flex items-center gap-3 text-sm text-gray-400">
                  <span className="capitalize">{story.template}</span>
                  <span>•</span>
                  <span>{story.sport}</span>
                  <span>•</span>
                  <span>{story.wordCount} words</span>
                </div>
              </div>
              <div className={`flex items-center gap-2 ${getStatusColor(story.status)}`}>
                {getStatusIcon(story.status)}
                <span className="text-sm capitalize">{story.status.replace('_', ' ')}</span>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-gray-500">
              <span>Created {format(story.createdAt, 'MMM d, yyyy')}</span>
              <span>•</span>
              <span>Updated {format(story.updatedAt, 'MMM d, yyyy h:mm a')}</span>
            </div>

            <div className="mt-4 flex items-center gap-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setCurrentStory(story);
                }}
                className="px-3 py-1.5 bg-accent hover:bg-blue-600 rounded text-xs"
              >
                Edit
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  console.log('Delete story:', story.id);
                }}
                className="px-3 py-1.5 bg-red-600 hover:bg-red-700 rounded text-xs flex items-center gap-1"
              >
                <Trash2 size={12} />
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default StoryQueue;
