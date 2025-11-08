"""
Context Manager - Manage story context and narrative continuity
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


class ContextManager:
    """
    Manage story context for narrative continuity

    Features:
    - Track team/player narratives across stories
    - Maintain historical context
    - Enable "Narrative Bridge" between stories
    - Store key storylines and arcs
    """

    def __init__(self, context_path: str = 'story_context'):
        """
        Initialize context manager

        Args:
            context_path: Path to store context data
        """
        self.context_path = Path(context_path)
        self.context_path.mkdir(parents=True, exist_ok=True)

        self.team_context = defaultdict(list)
        self.player_context = defaultdict(list)
        self.storylines = defaultdict(list)

    def add_story_context(
        self,
        story: Dict[str, Any],
        sport: str,
        context_data: Dict[str, Any]
    ) -> str:
        """
        Add context from a story

        Args:
            story: Story dictionary
            sport: Sport name
            context_data: Context extracted from sport data

        Returns:
            Context ID
        """
        timestamp = datetime.now()
        context_id = timestamp.strftime('%Y%m%d_%H%M%S')

        # Extract and store team context
        self._extract_team_context(context_data, sport, timestamp)

        # Extract and store player context
        self._extract_player_context(context_data, sport, timestamp)

        # Extract and store storylines
        self._extract_storylines(story, context_data, sport, timestamp)

        # Save context snapshot
        self._save_context_snapshot(context_id, sport)

        return context_id

    def get_narrative_bridge(
        self,
        sport: str,
        lookback_days: int = 7
    ) -> Optional[str]:
        """
        Get narrative bridge from previous stories

        Args:
            sport: Sport name
            lookback_days: Days to look back for context

        Returns:
            Narrative bridge text or None
        """
        # Load recent context
        recent_context = self._load_recent_context(sport, lookback_days)

        if not recent_context:
            return None

        # Generate bridge narrative
        bridge = self._generate_bridge(recent_context, sport)

        return bridge

    def get_team_storyline(
        self,
        team: str,
        sport: str,
        max_events: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get storyline for a team

        Args:
            team: Team name
            sport: Sport name
            max_events: Maximum events to return

        Returns:
            List of storyline events
        """
        team_key = self._team_key(team, sport)
        events = self.team_context.get(team_key, [])

        # Sort by timestamp (most recent first)
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return events[:max_events]

    def get_player_storyline(
        self,
        player: str,
        sport: str,
        max_events: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get storyline for a player

        Args:
            player: Player name
            sport: Sport name
            max_events: Maximum events to return

        Returns:
            List of storyline events
        """
        player_key = self._player_key(player, sport)
        events = self.player_context.get(player_key, [])

        # Sort by timestamp (most recent first)
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return events[:max_events]

    def find_continuing_storylines(
        self,
        context_data: Dict[str, Any],
        sport: str
    ) -> List[str]:
        """
        Find storylines that continue in current data

        Args:
            context_data: Current context data
            sport: Sport name

        Returns:
            List of continuing storyline descriptions
        """
        continuing = []

        # Check for continuing streaks
        trends = context_data.get('trends', [])
        for trend in trends:
            team = trend.get('team', '')
            if team:
                team_storyline = self.get_team_storyline(team, sport, max_events=2)
                if len(team_storyline) >= 2:
                    # Check if streak continues
                    if 'streak' in trend.get('type', ''):
                        continuing.append(
                            f"{team} continues their {trend.get('type', 'streak')}"
                        )

        # Check for continuing player performances
        players = context_data.get('standout_players', [])
        for player_data in players:
            player = player_data.get('player', '')
            if player:
                player_storyline = self.get_player_storyline(player, sport, max_events=2)
                if len(player_storyline) >= 2:
                    continuing.append(
                        f"{player} maintains strong performance"
                    )

        return continuing

    def _extract_team_context(
        self,
        context_data: Dict[str, Any],
        sport: str,
        timestamp: datetime
    ):
        """Extract and store team context"""
        # Store trends
        trends = context_data.get('trends', [])
        for trend in trends:
            team = trend.get('team', '')
            if team:
                team_key = self._team_key(team, sport)
                self.team_context[team_key].append({
                    'timestamp': timestamp.isoformat(),
                    'type': 'trend',
                    'data': trend
                })

        # Store game results
        games = context_data.get('recent_games', [])
        for game in games:
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')

            if home_team:
                team_key = self._team_key(home_team, sport)
                self.team_context[team_key].append({
                    'timestamp': timestamp.isoformat(),
                    'type': 'game',
                    'data': game
                })

            if away_team:
                team_key = self._team_key(away_team, sport)
                self.team_context[team_key].append({
                    'timestamp': timestamp.isoformat(),
                    'type': 'game',
                    'data': game
                })

    def _extract_player_context(
        self,
        context_data: Dict[str, Any],
        sport: str,
        timestamp: datetime
    ):
        """Extract and store player context"""
        # Store standout performances
        players = context_data.get('standout_players', [])
        for player_data in players:
            player = player_data.get('player', '')
            if player:
                player_key = self._player_key(player, sport)
                self.player_context[player_key].append({
                    'timestamp': timestamp.isoformat(),
                    'type': 'performance',
                    'data': player_data
                })

        # Store injuries
        injuries = context_data.get('injuries', [])
        for injury in injuries:
            # Try to extract player name from headline
            headline = injury.get('headline', '')
            # Simple extraction - could be improved
            if headline:
                player_key = self._player_key(headline.split()[0], sport)
                self.player_context[player_key].append({
                    'timestamp': timestamp.isoformat(),
                    'type': 'injury',
                    'data': injury
                })

    def _extract_storylines(
        self,
        story: Dict[str, Any],
        context_data: Dict[str, Any],
        sport: str,
        timestamp: datetime
    ):
        """Extract and store storylines"""
        storyline_key = f"{sport}_storylines"

        # Extract from headline if available
        if story.get('headline'):
            self.storylines[storyline_key].append({
                'timestamp': timestamp.isoformat(),
                'type': 'headline',
                'text': story['headline']
            })

        # Extract from trends
        trends = context_data.get('trends', [])
        for trend in trends:
            if 'streak' in trend.get('type', ''):
                self.storylines[storyline_key].append({
                    'timestamp': timestamp.isoformat(),
                    'type': 'streak',
                    'text': trend.get('description', '')
                })

    def _generate_bridge(
        self,
        recent_context: List[Dict[str, Any]],
        sport: str
    ) -> str:
        """Generate narrative bridge from recent context"""
        if not recent_context:
            return ""

        bridge = "**Continuing Stories:**\n\n"

        # Group by storyline type
        streaks = [c for c in recent_context if c.get('type') == 'streak']
        performances = [c for c in recent_context if c.get('type') == 'performance']

        # Add streak continuations
        if streaks:
            latest_streaks = streaks[:2]
            for streak in latest_streaks:
                bridge += f"• {streak.get('text', '')}\n"

        # Add performance continuations
        if performances:
            bridge += f"\n_Building on {len(performances)} ongoing storylines_\n"

        return bridge

    def _load_recent_context(
        self,
        sport: str,
        lookback_days: int
    ) -> List[Dict[str, Any]]:
        """Load context from recent days"""
        cutoff = datetime.now() - timedelta(days=lookback_days)
        recent = []

        storyline_key = f"{sport}_storylines"
        storylines = self.storylines.get(storyline_key, [])

        for storyline in storylines:
            timestamp_str = storyline.get('timestamp', '')
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if timestamp >= cutoff:
                    recent.append(storyline)
            except Exception:
                continue

        return recent

    def _save_context_snapshot(self, context_id: str, sport: str):
        """Save context snapshot to disk"""
        snapshot_dir = self.context_path / sport.lower()
        snapshot_dir.mkdir(exist_ok=True)

        snapshot_file = snapshot_dir / f"{context_id}.json"

        snapshot = {
            'context_id': context_id,
            'timestamp': datetime.now().isoformat(),
            'sport': sport,
            'team_context': dict(self.team_context),
            'player_context': dict(self.player_context),
            'storylines': dict(self.storylines)
        }

        snapshot_file.write_text(json.dumps(snapshot, indent=2), encoding='utf-8')

    def _team_key(self, team: str, sport: str) -> str:
        """Generate team context key"""
        return f"{sport}:{team}".lower()

    def _player_key(self, player: str, sport: str) -> str:
        """Generate player context key"""
        return f"{sport}:{player}".lower()

    def load_context_snapshot(self, context_id: str, sport: str) -> bool:
        """Load a context snapshot"""
        snapshot_dir = self.context_path / sport.lower()
        snapshot_file = snapshot_dir / f"{context_id}.json"

        if not snapshot_file.exists():
            return False

        try:
            snapshot = json.loads(snapshot_file.read_text(encoding='utf-8'))

            self.team_context = defaultdict(list, snapshot.get('team_context', {}))
            self.player_context = defaultdict(list, snapshot.get('player_context', {}))
            self.storylines = defaultdict(list, snapshot.get('storylines', {}))

            return True
        except Exception:
            return False

    def cleanup_old_context(self, sport: str, keep_days: int = 30) -> int:
        """Clean up old context data"""
        cutoff = datetime.now() - timedelta(days=keep_days)
        deleted = 0

        snapshot_dir = self.context_path / sport.lower()
        if not snapshot_dir.exists():
            return 0

        for snapshot_file in snapshot_dir.glob('*.json'):
            try:
                data = json.loads(snapshot_file.read_text(encoding='utf-8'))
                timestamp = datetime.fromisoformat(data['timestamp'])

                if timestamp < cutoff:
                    snapshot_file.unlink()
                    deleted += 1
            except Exception:
                continue

        return deleted
