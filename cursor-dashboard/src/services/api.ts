import axios from 'axios';
import { SportData, AgentLogEntry, AICoAuthorSuggestion, WritingFeedback } from '@/types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Sports Data
export async function fetchSportsData(sport: string): Promise<SportData> {
  const response = await api.get(`/api/sports/data?sport=${sport}`);
  return response.data.data;
}

// Story Generation
export async function generateStory(template: string, sport: string): Promise<{
  content: string;
  wordCount: number;
}> {
  const response = await api.post('/api/stories/generate', { template, sport });
  return response.data;
}

export async function expandParagraph(
  paragraph: string,
  context?: Record<string, any>
): Promise<{ expanded: string; wordCount: number }> {
  const response = await api.post('/api/stories/expand', { paragraph, context });
  return response.data;
}

// Writing Feedback
export async function getWritingFeedback(content: string): Promise<WritingFeedback[]> {
  const response = await api.post('/api/writing/feedback', { content });
  return response.data.feedback;
}

export async function proofreadContent(content: string): Promise<any[]> {
  const response = await api.post('/api/writing/proofread', { content });
  return response.data.suggestions;
}

// AI Co-Author
export async function getAIsuggestions(
  content: string,
  sport: string
): Promise<AICoAuthorSuggestion[]> {
  const response = await api.post('/api/ai/coauthor/suggest', { content, sport });
  return response.data.suggestions;
}

// Export
export async function exportToGoogleDocs(
  content: string,
  title: string
): Promise<{ docUrl: string }> {
  const response = await api.post('/api/export/google-docs', { content, title });
  return response.data;
}

export async function exportToMarkdown(
  content: string,
  title: string
): Promise<{ content: string; filename: string }> {
  const response = await api.post('/api/export/markdown', { content, title });
  return response.data;
}

// Logs
export async function getAgentLogs(
  limit?: number,
  agent?: string
): Promise<AgentLogEntry[]> {
  const params = new URLSearchParams();
  if (limit) params.append('limit', limit.toString());
  if (agent) params.append('agent', agent);

  const response = await api.get(`/api/logs?${params.toString()}`);
  return response.data.logs;
}

// Fact Checking
export async function factCheck(text: string): Promise<{
  verified: boolean;
  source: string;
  sourceUrl: string;
}> {
  const response = await api.post('/api/fact-check', { text });
  return response.data;
}

// Health Check
export async function healthCheck(): Promise<{ status: string }> {
  const response = await api.get('/api/health');
  return response.data;
}

export default api;
