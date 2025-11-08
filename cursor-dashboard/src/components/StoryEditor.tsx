import React, { useState, useMemo, useCallback } from 'react';
import { useDashboardStore } from '@/store/useDashboardStore';
import { Descendant, createEditor } from 'slate';
import { Slate, Editable, withReact, RenderLeafProps } from 'slate-react';
import { withHistory } from 'slate-history';
import { useHotkeys } from 'react-hotkeys-hook';
import { DataState, WritingFeedback } from '@/types';
import {
  Save,
  Download,
  Maximize2,
  Minimize2,
  AlertCircle,
  CheckCircle,
  Clock,
} from 'lucide-react';
import WritingFeedbackPanel from './WritingFeedbackPanel';
import FactCheckTooltip from './FactCheckTooltip';

const initialValue: Descendant[] = [
  {
    type: 'paragraph',
    children: [{ text: 'Start writing your story here...' }],
  },
];

function StoryEditor() {
  const { currentStory, updateStory } = useDashboardStore();
  const [editor] = useState(() => withHistory(withReact(createEditor())));
  const [value, setValue] = useState<Descendant[]>(initialValue);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showFeedback, setShowFeedback] = useState(true);
  const [wordLimit, setWordLimit] = useState<number | null>(null);

  // Mock feedback for demonstration
  const [feedback] = useState<WritingFeedback[]>([
    {
      id: '1',
      type: 'sentence_length',
      message: 'Sentence is too long (45 words). Consider breaking it up.',
      severity: 'warning',
      position: { start: 0, end: 100 },
    },
    {
      id: '2',
      type: 'missing_data',
      message: 'Missing data window for this statistic',
      severity: 'error',
      position: { start: 120, end: 150 },
    },
  ]);

  const wordCount = useMemo(() => {
    const text = value.map((n) => (n as any).children?.map((c: any) => c.text).join('')).join(' ');
    return text.split(/\s+/).filter((w) => w.length > 0).length;
  }, [value]);

  const renderLeaf = useCallback((props: RenderLeafProps) => {
    const { leaf, attributes, children } = props;

    // Apply data state styling
    let className = '';
    const dataState = (leaf as any).dataState as DataState | undefined;

    if (dataState === 'missing') className = 'data-missing';
    else if (dataState === 'verified') className = 'data-verified';
    else if (dataState === 'stale') className = 'data-stale';

    return (
      <span {...attributes} className={className}>
        {children}
      </span>
    );
  }, []);

  // Auto-expand paragraph
  const expandParagraph = useCallback(() => {
    // This would integrate with AI to expand the current paragraph
    console.log('Expanding paragraph...');
  }, []);

  useHotkeys('mod+s', (e) => {
    e.preventDefault();
    // Save current story
    if (currentStory) {
      const text = value.map((n) => (n as any).children?.map((c: any) => c.text).join('')).join('\n');
      updateStory(currentStory.id, {
        content: text,
        wordCount,
      });
    }
  });

  useHotkeys('mod+e', (e) => {
    e.preventDefault();
    expandParagraph();
  });

  if (!currentStory) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <FileText size={64} className="mx-auto mb-4 opacity-50" />
          <p className="text-lg">No story selected</p>
          <p className="text-sm mt-2">
            Create a new story from the template picker or select one from the queue
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex flex-col h-full ${isExpanded ? 'fixed inset-0 z-40 bg-editor-bg' : ''}`}>
      {/* Editor Toolbar */}
      <div className="bg-sidebar-bg border-b border-gray-700 px-6 py-3 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-200">{currentStory.title}</h2>
          <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
            <span>
              {wordCount} {wordLimit && `/ ${wordLimit}`} words
            </span>
            <span className="flex items-center gap-1">
              {currentStory.status === 'ready' ? (
                <>
                  <CheckCircle size={14} className="text-green-500" />
                  Ready
                </>
              ) : currentStory.status === 'in_progress' ? (
                <>
                  <Clock size={14} className="text-yellow-500" />
                  In Progress
                </>
              ) : (
                <>
                  <AlertCircle size={14} className="text-gray-500" />
                  Draft
                </>
              )}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowFeedback(!showFeedback)}
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm"
          >
            {showFeedback ? 'Hide' : 'Show'} Feedback
          </button>

          <select
            value={wordLimit || ''}
            onChange={(e) => setWordLimit(e.target.value ? parseInt(e.target.value) : null)}
            className="px-3 py-2 bg-gray-700 rounded-md text-sm border-0"
          >
            <option value="">No word limit</option>
            <option value="300">300 words</option>
            <option value="500">500 words</option>
            <option value="800">800 words</option>
            <option value="1200">1200 words</option>
          </select>

          <button
            onClick={expandParagraph}
            className="px-3 py-2 bg-accent hover:bg-blue-600 rounded-md text-sm"
            title="Expand paragraph (⌘E)"
          >
            Expand
          </button>

          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-2 bg-gray-700 hover:bg-gray-600 rounded-md"
          >
            {isExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>

          <button
            className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm flex items-center gap-2"
            title="Save (⌘S)"
          >
            <Save size={16} />
            Save
          </button>

          <button
            className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded-md text-sm flex items-center gap-2"
            title="Export (⌘G)"
          >
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Editor Area */}
        <div className="flex-1 overflow-auto">
          <div className="max-w-4xl mx-auto p-8">
            <Slate editor={editor} initialValue={value} onChange={setValue}>
              <Editable
                renderLeaf={renderLeaf}
                placeholder="Start writing your story..."
                className="editor-content focus:outline-none min-h-[500px]"
                spellCheck
              />
            </Slate>

            {/* Color-coded legend */}
            <div className="mt-8 p-4 bg-sidebar-bg rounded-lg border border-gray-700">
              <h4 className="text-sm font-semibold text-gray-300 mb-3">Data State Indicators</h4>
              <div className="flex gap-4 text-sm">
                <div className="flex items-center gap-2">
                  <span className="data-missing px-2 py-1">Missing</span>
                  <span className="text-gray-400">Data not yet added</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="data-verified px-2 py-1">Verified</span>
                  <span className="text-gray-400">Data confirmed accurate</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="data-stale px-2 py-1">Stale</span>
                  <span className="text-gray-400">Data needs updating</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Writing Feedback Panel */}
        {showFeedback && (
          <div className="w-80 border-l border-gray-700">
            <WritingFeedbackPanel feedback={feedback} />
          </div>
        )}
      </div>
    </div>
  );
}

function FileText(props: { size: number; className?: string }) {
  return <svg {...props}><text>📄</text></svg>;
}

export default StoryEditor;
