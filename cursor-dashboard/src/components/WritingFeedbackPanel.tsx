import React from 'react';
import { WritingFeedback } from '@/types';
import { AlertCircle, AlertTriangle, Info } from 'lucide-react';

interface Props {
  feedback: WritingFeedback[];
}

function WritingFeedbackPanel({ feedback }: Props) {
  const getIcon = (severity: WritingFeedback['severity']) => {
    switch (severity) {
      case 'error': return <AlertCircle size={16} className="text-red-500" />;
      case 'warning': return <AlertTriangle size={16} className="text-yellow-500" />;
      case 'info': return <Info size={16} className="text-blue-500" />;
    }
  };

  const getSeverityColor = (severity: WritingFeedback['severity']) => {
    switch (severity) {
      case 'error': return 'border-red-500 bg-red-500/10';
      case 'warning': return 'border-yellow-500 bg-yellow-500/10';
      case 'info': return 'border-blue-500 bg-blue-500/10';
    }
  };

  return (
    <div className="h-full bg-sidebar-bg flex flex-col">
      <div className="border-b border-gray-700 px-4 py-3">
        <h3 className="font-semibold text-gray-200">Writing Feedback</h3>
        <p className="text-xs text-gray-400 mt-1">
          {feedback.length} {feedback.length === 1 ? 'issue' : 'issues'} found
        </p>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-3">
        {feedback.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Info size={48} className="mx-auto mb-3 opacity-50" />
            <p className="text-sm">No issues found</p>
            <p className="text-xs mt-1">Your writing looks good!</p>
          </div>
        ) : (
          feedback.map((item) => (
            <div
              key={item.id}
              className={`border-l-2 rounded-r-lg p-3 ${getSeverityColor(item.severity)}`}
            >
              <div className="flex items-start gap-2 mb-2">
                {getIcon(item.severity)}
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-200 capitalize">
                    {item.type.replace('_', ' ')}
                  </p>
                </div>
              </div>

              <p className="text-sm text-gray-300 mb-2">{item.message}</p>

              {item.suggestion && (
                <div className="mt-2 p-2 bg-editor-bg rounded text-xs text-gray-400">
                  <span className="font-semibold">Suggestion:</span> {item.suggestion}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default WritingFeedbackPanel;
