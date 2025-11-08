// Core data types matching SportStatBot models
export interface GameData {
  homeTeam: string;
  awayTeam: string;
  homeScore: number;
  awayScore: number;
  time: string;
  status: string;
  classification?: 'blowout' | 'close_game' | 'overtime' | 'upset';
  leaders?: {
    homeTopPerformer?: string;
    awayTopPerformer?: string;
  };
}

export interface TrendData {
  team: string;
  type: 'hot_streak' | 'cold_streak';
  wins: number;
  losses: number;
  streakLength: number;
  details: string;
}

export interface PlayerPerformance {
  name: string;
  team: string;
  stats: Record<string, number>;
  description: string;
}

export interface InjuryData {
  team: string;
  player: string;
  status: string;
  impact: string;
}

export interface BettingInsight {
  game: string;
  homeTeam: string;
  awayTeam: string;
  homeOdds: number;
  awayOdds: number;
  analysis: string;
  recommendation?: string;
}

export interface MustWatchMatchup {
  game: string;
  reason: string;
  significance: string;
}

export interface SportData {
  sport: string;
  games: GameData[];
  trends: TrendData[];
  standoutPerformers: PlayerPerformance[];
  injuries: InjuryData[];
  bettingInsights: BettingInsight[];
  mustWatchMatchups: MustWatchMatchup[];
}

// UI-specific types
export type StoryTemplate = 'digest' | 'preview' | 'feature' | 'betting';
export type DataState = 'missing' | 'verified' | 'stale';

export interface StoryQueueItem {
  id: string;
  title: string;
  template: StoryTemplate;
  sport: string;
  status: 'draft' | 'in_progress' | 'ready' | 'published';
  content: string;
  dataState: Record<string, DataState>;
  createdAt: Date;
  updatedAt: Date;
  wordCount: number;
}

export interface CommandItem {
  id: string;
  label: string;
  description: string;
  icon?: string;
  shortcut?: string;
  action: () => void | Promise<void>;
  category: 'generate' | 'export' | 'edit' | 'data' | 'settings';
}

export interface WritingFeedback {
  id: string;
  type: 'sentence_length' | 'missing_data' | 'grammar' | 'structure' | 'style';
  message: string;
  severity: 'error' | 'warning' | 'info';
  position: { start: number; end: number };
  suggestion?: string;
}

export interface FactCheckNote {
  id: string;
  text: string;
  source: string;
  sourceUrl: string;
  verified: boolean;
  timestamp: Date;
}

export interface AgentLogEntry {
  id: string;
  agent: 'fetcher' | 'analyzer' | 'formatter' | 'writer';
  action: string;
  details: string;
  timestamp: Date;
  data?: any;
}

export interface AICoAuthorSuggestion {
  id: string;
  paragraph: string;
  reasoning: string;
  dataPoints: string[];
  confidence: number;
}

export interface WritingHistoryEntry {
  id: string;
  date: Date;
  storyCount: number;
  wordCount: number;
  sports: string[];
  templates: StoryTemplate[];
}

// Store types
export interface DashboardState {
  activeLeague: string;
  storyQueue: StoryQueueItem[];
  currentStory: StoryQueueItem | null;
  showCommandPalette: boolean;
  showTemplateModal: boolean;
  agentLogs: AgentLogEntry[];
  writingHistory: WritingHistoryEntry[];
  setActiveLeague: (league: string) => void;
  addToQueue: (story: StoryQueueItem) => void;
  updateStory: (id: string, updates: Partial<StoryQueueItem>) => void;
  setCurrentStory: (story: StoryQueueItem | null) => void;
  toggleCommandPalette: () => void;
  toggleTemplateModal: () => void;
  addAgentLog: (log: AgentLogEntry) => void;
}
