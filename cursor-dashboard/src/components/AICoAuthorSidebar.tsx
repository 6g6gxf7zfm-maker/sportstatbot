import React, { useState } from 'react';
import { AICoAuthorSuggestion } from '@/types';
import { Sparkles, ThumbsUp, ThumbsDown, RefreshCw } from 'lucide-react';

function AICoAuthorSidebar() {
  const [suggestions] = useState<AICoAuthorSuggestion[]>([
    {
      id: '1',
      paragraph: "The Lakers' recent three-game winning streak has been fueled by Anthony Davis's dominant performance, averaging 28.7 points and 12.3 rebounds while shooting 58% from the field. His defensive presence has also been crucial, with 2.7 blocks per game during this stretch.",
      reasoning: 'Building on the hot streak data with specific performance metrics',
      dataPoints: ['Anthony Davis stats', 'Lakers winning streak', 'Defensive metrics'],
      confidence: 0.92,
    },
    {
      id: '2',
      paragraph: "Meanwhile, the Warriors face uncertainty as Stephen Curry's ankle injury could sideline him for the upcoming matchup. The team has struggled without their star guard this season, posting a 2-5 record in games he's missed.",
      reasoning: 'Connecting injury report with team performance context',
      dataPoints: ['Curry injury status', 'Warriors record without Curry'],
      confidence: 0.85,
    },
  ]);

  const [loading, setLoading] = useState(false);

  const handleRefresh = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 1000);
  };

  const handleAccept = (suggestion: AICoAuthorSuggestion) => {
    console.log('Accepting suggestion:', suggestion);
    // This would insert the paragraph into the editor
  };

  const handleReject = (suggestion: AICoAuthorSuggestion) => {
    console.log('Rejecting suggestion:', suggestion);
  };

  return (
    <div className="h-full bg-sidebar-bg flex flex-col">
      <div className="border-b border-gray-700 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles size={18} className="text-accent" />
          <h3 className="font-semibold text-gray-200">AI Co-Author</h3>
        </div>
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="p-1.5 hover:bg-gray-700 rounded transition-colors disabled:opacity-50"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        {suggestions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Sparkles size={48} className="mx-auto mb-3 opacity-50" />
            <p className="text-sm">No suggestions yet</p>
            <p className="text-xs mt-1">Start writing to get AI suggestions</p>
          </div>
        ) : (
          suggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className="bg-editor-bg border border-gray-700 rounded-lg p-4 hover:border-accent transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <span className="text-xs font-semibold text-accent uppercase">
                  Suggested Paragraph
                </span>
                <div className="flex items-center gap-1 text-xs text-gray-400">
                  <span>{Math.round(suggestion.confidence * 100)}%</span>
                </div>
              </div>

              <p className="text-sm text-gray-300 leading-relaxed mb-3">
                {suggestion.paragraph}
              </p>

              <div className="mb-3">
                <p className="text-xs text-gray-500 mb-2">
                  <span className="font-semibold">Reasoning:</span> {suggestion.reasoning}
                </p>
                <div className="flex flex-wrap gap-1">
                  {suggestion.dataPoints.map((point, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-gray-700 px-2 py-1 rounded"
                    >
                      {point}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleAccept(suggestion)}
                  className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-xs flex items-center justify-center gap-1"
                >
                  <ThumbsUp size={12} />
                  Accept
                </button>
                <button
                  onClick={() => handleReject(suggestion)}
                  className="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded text-xs flex items-center justify-center gap-1"
                >
                  <ThumbsDown size={12} />
                  Reject
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="border-t border-gray-700 px-4 py-3">
        <button className="w-full px-4 py-2 bg-accent hover:bg-blue-600 rounded text-sm">
          Generate Next Paragraph
        </button>
      </div>
    </div>
  );
}

export default AICoAuthorSidebar;
