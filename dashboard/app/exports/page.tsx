'use client';

import { useState, useEffect } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import { FileText, ExternalLink, Download } from 'lucide-react';

interface Export {
  id: string;
  type: string;
  title: string;
  league: string;
  storyType: string;
  externalUrl: string | null;
  createdAt: string;
}

const mockStory = {
  title: 'NFL Week 10 Power Rankings Analysis',
  content: `# NFL Week 10 Power Rankings

## Top Movers

**Philadelphia Eagles** 🦅
The Eagles continue their dominant run...

**San Francisco 49ers** 🏈
Defense remains elite...

## Analysis
[Detailed analysis here...]`,
  league: 'NFL',
  storyType: 'digest',
};

export default function Exports() {
  const [exports, setExports] = useState<Export[]>([]);
  const [loading, setLoading] = useState(false);
  const [exportType, setExportType] = useState<'google' | 'apple'>('google');

  const fetchExports = async () => {
    try {
      const response = await fetch('/api/exports');
      const data = await response.json();
      if (data.exports) {
        setExports(data.exports);
      }
    } catch (error) {
      console.error('Error fetching exports:', error);
    }
  };

  useEffect(() => {
    fetchExports();
  }, []);

  const handleExport = async () => {
    setLoading(true);
    try {
      const endpoint = exportType === 'google' ? '/api/exports/google' : '/api/exports/apple';
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockStory),
      });

      const data = await response.json();
      if (data.success) {
        await fetchExports();
        if (data.export?.url) {
          window.open(data.export.url, '_blank');
        }
      }
    } catch (error) {
      console.error('Error exporting:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          title="Exports"
          description="Export stories to Google Docs and Apple Notes"
        />
        <main className="flex-1 overflow-y-auto p-8">
          {/* Export Form */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-800 p-6 mb-8">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Export Story
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Export Destination
                </label>
                <select
                  value={exportType}
                  onChange={(e) => setExportType(e.target.value as 'google' | 'apple')}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="google">Google Docs</option>
                  <option value="apple">Apple Notes</option>
                </select>
              </div>
              <div className="flex items-end">
                <button
                  onClick={handleExport}
                  disabled={loading}
                  className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Download className="mr-2 h-5 w-5" />
                  {loading ? 'Exporting...' : 'Export Now'}
                </button>
              </div>
            </div>
            <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-md">
              <p className="text-sm text-gray-600 dark:text-gray-400">
                <strong>Preview:</strong> {mockStory.title}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                {mockStory.league} · {mockStory.storyType}
              </p>
            </div>
          </div>

          {/* Exports History */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-800">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Export History
              </h2>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-800">
              {exports.length === 0 ? (
                <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                  No exports yet. Try exporting a story above!
                </div>
              ) : (
                exports.map((exp) => (
                  <div key={exp.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <FileText className="h-5 w-5 text-gray-400 mt-1" />
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white">
                              {exp.title}
                            </h3>
                            <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                              {exp.league}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {exp.type === 'google_docs' ? 'Google Docs' : 'Apple Notes'} · {exp.storyType}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                            {new Date(exp.createdAt).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      {exp.externalUrl && (
                        <a
                          href={exp.externalUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors"
                        >
                          <ExternalLink className="h-5 w-5 text-gray-400" />
                        </a>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
