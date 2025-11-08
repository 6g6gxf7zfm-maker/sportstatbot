import React, { useState } from 'react';
import { useDashboardStore } from '@/store/useDashboardStore';
import { AgentLogEntry } from '@/types';
import { format } from 'date-fns';
import { Activity, Database, BarChart3, FileText, Code } from 'lucide-react';

function AgentLogViewer() {
  const { agentLogs } = useDashboardStore();
  const [filter, setFilter] = useState<string>('all');

  const getAgentIcon = (agent: AgentLogEntry['agent']) => {
    switch (agent) {
      case 'fetcher': return <Database size={16} className="text-blue-500" />;
      case 'analyzer': return <BarChart3 size={16} className="text-green-500" />;
      case 'formatter': return <FileText size={16} className="text-yellow-500" />;
      case 'writer': return <Code size={16} className="text-purple-500" />;
    }
  };

  const filteredLogs = filter === 'all'
    ? agentLogs
    : agentLogs.filter(log => log.agent === filter);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-200">Agent Activity Log</h2>
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 bg-sidebar-bg border border-gray-700 rounded-md text-sm"
        >
          <option value="all">All Agents</option>
          <option value="fetcher">Data Fetcher</option>
          <option value="analyzer">Analyzer</option>
          <option value="formatter">Formatter</option>
          <option value="writer">Writer</option>
        </select>
      </div>

      {filteredLogs.length === 0 ? (
        <div className="text-center py-12">
          <Activity size={64} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-xl font-semibold text-gray-300 mb-2">No agent activity yet</h3>
          <p className="text-gray-500">
            Agent logs will appear here as they process data and generate stories
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {filteredLogs.map((log) => (
            <div
              key={log.id}
              className="bg-sidebar-bg border border-gray-700 rounded-lg p-4 hover:border-accent transition-colors"
            >
              <div className="flex items-start gap-3">
                <div className="mt-1">{getAgentIcon(log.agent)}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-gray-200 capitalize">
                      {log.agent}
                    </span>
                    <span className="text-xs text-gray-500">
                      {format(log.timestamp, 'MMM d, h:mm:ss a')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-300 mb-1">{log.action}</p>
                  <p className="text-xs text-gray-400">{log.details}</p>
                  {log.data && (
                    <details className="mt-2">
                      <summary className="text-xs text-accent cursor-pointer hover:underline">
                        View data
                      </summary>
                      <pre className="mt-2 p-2 bg-editor-bg rounded text-xs text-gray-400 overflow-x-auto">
                        {JSON.stringify(log.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AgentLogViewer;
