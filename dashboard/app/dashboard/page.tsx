'use client';

import { useEffect, useState } from 'react';
import Header from '@/components/Header';
import Sidebar from '@/components/Sidebar';
import { FileText, TrendingUp, Clock, ExternalLink } from 'lucide-react';

interface Digest {
  id: string;
  league: string;
  type: string;
  title: string;
  summary: string;
  date: string;
}

export default function Dashboard() {
  const [digests, setDigests] = useState<Digest[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching recent digests
    // In production, fetch from API
    const mockDigests: Digest[] = [
      {
        id: '1',
        league: 'NFL',
        type: 'digest',
        title: 'Week 10 Power Rankings Shift',
        summary: 'Major movements in the top 10 as playoff picture takes shape...',
        date: new Date().toISOString(),
      },
      {
        id: '2',
        league: 'NBA',
        type: 'feature',
        title: 'Rising Stars: Rookies Making Impact',
        summary: 'In-depth analysis of this year\'s standout rookie class...',
        date: new Date().toISOString(),
      },
      {
        id: '3',
        league: 'MLB',
        type: 'report',
        title: 'Offseason Moves Analysis',
        summary: 'Breaking down the biggest trades and signings...',
        date: new Date().toISOString(),
      },
    ];

    setTimeout(() => {
      setDigests(mockDigests);
      setLoading(false);
    }, 500);
  }, []);

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-950">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header
          title="Dashboard"
          description="Your latest sports intelligence reports"
        />
        <main className="flex-1 overflow-y-auto p-8">
          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-800">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900/20">
                  <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Total Reports
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {digests.length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-800">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-green-100 dark:bg-green-900/20">
                  <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Active Leagues
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {new Set(digests.map(d => d.league)).size}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-900 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-800">
              <div className="flex items-center">
                <div className="p-3 rounded-full bg-purple-100 dark:bg-purple-900/20">
                  <Clock className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    Last Updated
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    Today
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Digests */}
          <div className="bg-white dark:bg-gray-900 rounded-lg shadow border border-gray-200 dark:border-gray-800">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Recent Reports
              </h2>
            </div>
            <div className="divide-y divide-gray-200 dark:divide-gray-800">
              {loading ? (
                <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                  Loading...
                </div>
              ) : digests.length === 0 ? (
                <div className="p-6 text-center text-gray-500 dark:text-gray-400">
                  No reports available
                </div>
              ) : (
                digests.map((digest) => (
                  <div key={digest.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300">
                            {digest.league}
                          </span>
                          <span className="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                            {digest.type}
                          </span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                          {digest.title}
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {digest.summary}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                          {new Date(digest.date).toLocaleDateString()}
                        </p>
                      </div>
                      <button className="ml-4 p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-md transition-colors">
                        <ExternalLink className="h-5 w-5 text-gray-400" />
                      </button>
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
