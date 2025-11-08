import { create } from 'zustand';
import { DashboardState, StoryQueueItem, AgentLogEntry } from '@/types';

export const useDashboardStore = create<DashboardState>((set) => ({
  activeLeague: 'NFL',
  storyQueue: [],
  currentStory: null,
  showCommandPalette: false,
  showTemplateModal: false,
  agentLogs: [],
  writingHistory: [],

  setActiveLeague: (league) => set({ activeLeague: league }),

  addToQueue: (story) =>
    set((state) => ({
      storyQueue: [...state.storyQueue, story],
    })),

  updateStory: (id, updates) =>
    set((state) => ({
      storyQueue: state.storyQueue.map((story) =>
        story.id === id ? { ...story, ...updates, updatedAt: new Date() } : story
      ),
      currentStory:
        state.currentStory?.id === id
          ? { ...state.currentStory, ...updates, updatedAt: new Date() }
          : state.currentStory,
    })),

  setCurrentStory: (story) => set({ currentStory: story }),

  toggleCommandPalette: () =>
    set((state) => ({ showCommandPalette: !state.showCommandPalette })),

  toggleTemplateModal: () =>
    set((state) => ({ showTemplateModal: !state.showTemplateModal })),

  addAgentLog: (log) =>
    set((state) => ({
      agentLogs: [log, ...state.agentLogs].slice(0, 100), // Keep last 100 logs
    })),
}));
