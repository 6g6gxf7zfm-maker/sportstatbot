import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/Tabs';
import { useDashboardStore } from '@/store/useDashboardStore';
import StoryQueue from './StoryQueue';
import StoryEditor from './StoryEditor';
import AgentLogViewer from './AgentLogViewer';
import AICoAuthorSidebar from './AICoAuthorSidebar';
import WritingHistoryPanel from './WritingHistoryPanel';
import { LayoutDashboard, FileText, Activity, BarChart3 } from 'lucide-react';

const LEAGUES = ['NFL', 'NBA', 'MLB', 'NHL', 'MLS', 'Soccer', 'Golf'];

function Dashboard() {
  const { activeLeague, setActiveLeague, currentStory } = useDashboardStore();
  const [activeTab, setActiveTab] = useState('editor');
  const [showSidebar, setShowSidebar] = useState(true);

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header with League Tabs */}
        <header className="bg-sidebar-bg border-b border-gray-700 px-6 py-4">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-accent">SportStatBot</h1>
            <div className="flex items-center gap-4">
              <button
                onClick={() => setShowSidebar(!showSidebar)}
                className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-md text-sm"
              >
                {showSidebar ? 'Hide' : 'Show'} AI Co-Author
              </button>
            </div>
          </div>

          {/* League Tabs */}
          <div className="flex gap-2 overflow-x-auto pb-2">
            {LEAGUES.map((league) => (
              <button
                key={league}
                onClick={() => setActiveLeague(league)}
                className={`px-4 py-2 rounded-md whitespace-nowrap transition-colors ${
                  activeLeague === league
                    ? 'bg-accent text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                {league}
              </button>
            ))}
          </div>
        </header>

        {/* Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
          <TabsList className="bg-sidebar-bg border-b border-gray-700 px-6">
            <TabsTrigger value="editor" className="flex items-center gap-2">
              <FileText size={16} />
              Editor
            </TabsTrigger>
            <TabsTrigger value="queue" className="flex items-center gap-2">
              <LayoutDashboard size={16} />
              Story Queue
            </TabsTrigger>
            <TabsTrigger value="logs" className="flex items-center gap-2">
              <Activity size={16} />
              Agent Logs
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <BarChart3 size={16} />
              Writing History
            </TabsTrigger>
          </TabsList>

          <div className="flex-1 overflow-auto">
            <TabsContent value="editor" className="h-full m-0">
              <div className="flex h-full">
                <div className={showSidebar ? 'flex-1' : 'w-full'}>
                  <StoryEditor />
                </div>
                {showSidebar && (
                  <div className="w-96 border-l border-gray-700">
                    <AICoAuthorSidebar />
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="queue" className="p-6">
              <StoryQueue />
            </TabsContent>

            <TabsContent value="logs" className="p-6">
              <AgentLogViewer />
            </TabsContent>

            <TabsContent value="history" className="p-6">
              <WritingHistoryPanel />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  );
}

export default Dashboard;
