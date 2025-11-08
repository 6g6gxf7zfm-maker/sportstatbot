import React from 'react';
import { StoryQueueItem } from '@/types';
import { X, Download, FileText, Copy, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { exportStoryToGoogleDocs, downloadAsMarkdown, copyToClipboard } from '@/services/googleDocs';

interface Props {
  story: StoryQueueItem | null;
  isOpen: boolean;
  onClose: () => void;
}

function PreviewModal({ story, isOpen, onClose }: Props) {
  const [exporting, setExporting] = React.useState(false);

  if (!isOpen || !story) return null;

  const handleExportToGoogleDocs = async () => {
    setExporting(true);
    try {
      const docUrl = await exportStoryToGoogleDocs(story.content, story.title);
      window.open(docUrl, '_blank');
      // Show success toast
      console.log('Exported to Google Docs:', docUrl);
    } catch (error) {
      console.error('Export failed:', error);
      // Show error toast
    } finally {
      setExporting(false);
    }
  };

  const handleDownloadMarkdown = async () => {
    try {
      await downloadAsMarkdown(story.content, story.title);
      // Show success toast
      console.log('Downloaded as markdown');
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  const handleCopyToClipboard = async () => {
    try {
      await copyToClipboard(story.content);
      // Show success toast
      console.log('Copied to clipboard');
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-sidebar-bg rounded-lg shadow-2xl border border-gray-700 w-full max-w-5xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="border-b border-gray-700 px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-200">{story.title}</h2>
            <p className="text-sm text-gray-400 mt-1">
              {story.sport} • {story.template} • {story.wordCount} words
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-700 rounded-md transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Preview Content */}
        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-4xl mx-auto prose prose-invert">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {story.content || '*No content yet*'}
            </ReactMarkdown>
          </div>
        </div>

        {/* Footer with Actions */}
        <div className="border-t border-gray-700 px-6 py-4 flex items-center justify-between">
          <div className="text-sm text-gray-400">
            Last updated: {story.updatedAt.toLocaleString()}
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleCopyToClipboard}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm flex items-center gap-2"
            >
              <Copy size={16} />
              Copy
            </button>

            <button
              onClick={handleDownloadMarkdown}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm flex items-center gap-2"
            >
              <FileText size={16} />
              Markdown
            </button>

            <button
              onClick={handleExportToGoogleDocs}
              disabled={exporting}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-md text-sm flex items-center gap-2"
            >
              {exporting ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                  Exporting...
                </>
              ) : (
                <>
                  <ExternalLink size={16} />
                  Export to Google Docs
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PreviewModal;
