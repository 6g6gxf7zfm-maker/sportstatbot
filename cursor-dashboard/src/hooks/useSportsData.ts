import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { fetchSportsData, generateStory, getAIsuggestions, getWritingFeedback } from '@/services/api';
import { useDashboardStore } from '@/store/useDashboardStore';

export function useSportsData(sport: string) {
  return useQuery({
    queryKey: ['sports-data', sport],
    queryFn: () => fetchSportsData(sport),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // Refresh every 10 minutes
  });
}

export function useGenerateStory() {
  const queryClient = useQueryClient();
  const { addAgentLog } = useDashboardStore();

  return useMutation({
    mutationFn: ({ template, sport }: { template: string; sport: string }) =>
      generateStory(template, sport),
    onSuccess: () => {
      addAgentLog({
        id: `log-${Date.now()}`,
        agent: 'writer',
        action: 'Story generated',
        details: 'Successfully generated story content',
        timestamp: new Date(),
      });
    },
  });
}

export function useAISuggestions(content: string, sport: string) {
  return useQuery({
    queryKey: ['ai-suggestions', content, sport],
    queryFn: () => getAIsuggestions(content, sport),
    enabled: content.length > 100, // Only fetch suggestions if there's content
    staleTime: 30 * 1000, // 30 seconds
  });
}

export function useWritingFeedback(content: string) {
  return useQuery({
    queryKey: ['writing-feedback', content],
    queryFn: () => getWritingFeedback(content),
    enabled: content.length > 0,
    staleTime: 10 * 1000, // 10 seconds
  });
}
