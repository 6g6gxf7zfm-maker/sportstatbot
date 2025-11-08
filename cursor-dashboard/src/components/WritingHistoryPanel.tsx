import React from 'react';
import { useDashboardStore } from '@/store/useDashboardStore';
import { format, startOfWeek, endOfWeek, eachDayOfInterval } from 'date-fns';
import { BarChart3, TrendingUp, FileText, Award } from 'lucide-react';

function WritingHistoryPanel() {
  const { writingHistory } = useDashboardStore();

  // Mock data for demonstration
  const mockHistory = [
    { date: new Date('2024-01-01'), stories: 3, words: 2400 },
    { date: new Date('2024-01-02'), stories: 5, words: 3800 },
    { date: new Date('2024-01-03'), stories: 2, words: 1600 },
    { date: new Date('2024-01-04'), stories: 4, words: 3200 },
    { date: new Date('2024-01-05'), stories: 6, words: 4500 },
    { date: new Date('2024-01-06'), stories: 3, words: 2700 },
    { date: new Date('2024-01-07'), stories: 4, words: 3100 },
  ];

  const totalStories = mockHistory.reduce((sum, day) => sum + day.stories, 0);
  const totalWords = mockHistory.reduce((sum, day) => sum + day.words, 0);
  const avgStoriesPerDay = (totalStories / mockHistory.length).toFixed(1);
  const avgWordsPerStory = (totalWords / totalStories).toFixed(0);

  const maxStories = Math.max(...mockHistory.map(d => d.stories));

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-200 mb-2">Writing History</h2>
        <p className="text-gray-400">Track your daily story production and progress</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-sidebar-bg border border-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <FileText size={18} className="text-blue-500" />
            <span className="text-sm text-gray-400">Total Stories</span>
          </div>
          <p className="text-3xl font-bold text-gray-200">{totalStories}</p>
        </div>

        <div className="bg-sidebar-bg border border-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 size={18} className="text-green-500" />
            <span className="text-sm text-gray-400">Total Words</span>
          </div>
          <p className="text-3xl font-bold text-gray-200">{totalWords.toLocaleString()}</p>
        </div>

        <div className="bg-sidebar-bg border border-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={18} className="text-yellow-500" />
            <span className="text-sm text-gray-400">Avg/Day</span>
          </div>
          <p className="text-3xl font-bold text-gray-200">{avgStoriesPerDay}</p>
        </div>

        <div className="bg-sidebar-bg border border-gray-700 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Award size={18} className="text-purple-500" />
            <span className="text-sm text-gray-400">Avg Words</span>
          </div>
          <p className="text-3xl font-bold text-gray-200">{avgWordsPerStory}</p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-sidebar-bg border border-gray-700 rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold text-gray-200 mb-4">Daily Story Count</h3>
        <div className="flex items-end gap-2 h-48">
          {mockHistory.map((day, idx) => (
            <div key={idx} className="flex-1 flex flex-col items-center gap-2">
              <div className="flex-1 flex items-end w-full">
                <div
                  className="w-full bg-accent rounded-t transition-all hover:bg-blue-600"
                  style={{
                    height: `${(day.stories / maxStories) * 100}%`,
                    minHeight: day.stories > 0 ? '8px' : '0',
                  }}
                  title={`${day.stories} stories, ${day.words} words`}
                />
              </div>
              <span className="text-xs text-gray-500">
                {format(day.date, 'EEE')}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-sidebar-bg border border-gray-700 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-200 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {mockHistory.slice().reverse().slice(0, 5).map((day, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-700 last:border-0">
              <div>
                <p className="text-sm font-medium text-gray-200">
                  {format(day.date, 'EEEE, MMMM d')}
                </p>
                <p className="text-xs text-gray-400">
                  {day.stories} {day.stories === 1 ? 'story' : 'stories'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-200">
                  {day.words.toLocaleString()} words
                </p>
                <p className="text-xs text-gray-400">
                  {Math.round(day.words / day.stories)} avg
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default WritingHistoryPanel;
