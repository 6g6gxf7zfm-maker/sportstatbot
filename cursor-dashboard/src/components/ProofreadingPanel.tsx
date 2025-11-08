import React, { useEffect, useState } from 'react';
import { proofreadContent } from '@/services/api';
import { CheckCircle, AlertCircle, Loader } from 'lucide-react';

interface ProofreadingSuggestion {
  id: string;
  type: 'grammar' | 'spelling' | 'style' | 'clarity';
  message: string;
  original: string;
  suggestion: string;
  position: { start: number; end: number };
}

interface Props {
  content: string;
  onApplySuggestion?: (suggestion: ProofreadingSuggestion) => void;
}

function ProofreadingPanel({ content, onApplySuggestion }: Props) {
  const [suggestions, setSuggestions] = useState<ProofreadingSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastCheck, setLastCheck] = useState<Date | null>(null);

  useEffect(() => {
    // Debounce proofreading checks
    const timer = setTimeout(() => {
      if (content.length > 0) {
        checkContent();
      }
    }, 2000);

    return () => clearTimeout(timer);
  }, [content]);

  const checkContent = async () => {
    setLoading(true);
    try {
      const results = await proofreadContent(content);
      setSuggestions(results);
      setLastCheck(new Date());
    } catch (error) {
      console.error('Proofreading failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type: ProofreadingSuggestion['type']) => {
    switch (type) {
      case 'grammar': return 'text-red-500';
      case 'spelling': return 'text-yellow-500';
      case 'style': return 'text-blue-500';
      case 'clarity': return 'text-purple-500';
    }
  };

  return (
    <div className="h-full bg-sidebar-bg flex flex-col border-l border-gray-700">
      <div className="border-b border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between mb-1">
          <h3 className="font-semibold text-gray-200">Real-time Proofreading</h3>
          {loading && <Loader size={16} className="animate-spin text-accent" />}
        </div>
        {lastCheck && (
          <p className="text-xs text-gray-400">
            Last checked: {lastCheck.toLocaleTimeString()}
          </p>
        )}
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-3">
        {suggestions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CheckCircle size={48} className="mx-auto mb-3 text-green-500 opacity-50" />
            <p className="text-sm">No issues found</p>
            <p className="text-xs mt-1">Your writing is looking good!</p>
          </div>
        ) : (
          suggestions.map((suggestion) => (
            <div
              key={suggestion.id}
              className="border border-gray-700 rounded-lg p-3 hover:border-accent transition-colors"
            >
              <div className="flex items-start gap-2 mb-2">
                <AlertCircle size={16} className={`mt-0.5 ${getTypeColor(suggestion.type)}`} />
                <div className="flex-1">
                  <p className={`text-sm font-medium capitalize ${getTypeColor(suggestion.type)}`}>
                    {suggestion.type}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">{suggestion.message}</p>
                </div>
              </div>

              {suggestion.original && (
                <div className="mt-2 space-y-2">
                  <div className="p-2 bg-red-500/10 rounded text-xs text-gray-300 line-through">
                    {suggestion.original}
                  </div>
                  <div className="p-2 bg-green-500/10 rounded text-xs text-gray-300">
                    {suggestion.suggestion}
                  </div>
                </div>
              )}

              {onApplySuggestion && (
                <button
                  onClick={() => onApplySuggestion(suggestion)}
                  className="mt-2 w-full px-3 py-1.5 bg-accent hover:bg-blue-600 rounded text-xs"
                >
                  Apply Suggestion
                </button>
              )}
            </div>
          ))
        )}
      </div>

      {suggestions.length > 0 && (
        <div className="border-t border-gray-700 px-4 py-3">
          <button
            onClick={checkContent}
            disabled={loading}
            className="w-full px-4 py-2 bg-accent hover:bg-blue-600 disabled:opacity-50 rounded text-sm"
          >
            {loading ? 'Checking...' : 'Recheck Content'}
          </button>
        </div>
      )}
    </div>
  );
}

export default ProofreadingPanel;
