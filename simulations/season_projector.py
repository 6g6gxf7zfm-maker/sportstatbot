"""Season projection dashboard for win totals and playoff odds."""
from typing import Dict, List, Optional
from datetime import datetime
import json
import os


class SeasonProjector:
    """
    Projects season outcomes including win totals, playoff odds, and division standings.

    Uses Monte Carlo simulations to generate probability distributions for
    season-long outcomes.
    """

    def __init__(self, monte_carlo_engine=None, storage_path: str = './data/projections'):
        """
        Initialize season projector.

        Args:
            monte_carlo_engine: MonteCarloEngine instance
            storage_path: Path to store projection data
        """
        self.monte_carlo = monte_carlo_engine
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def project_season(
        self,
        sport: str,
        teams: List[str],
        team_ratings: Dict[str, float],
        remaining_schedule: List[Dict],
        current_records: Dict[str, Dict]
    ) -> Dict:
        """
        Project rest of season outcomes.

        Args:
            sport: Sport type
            teams: List of team names
            team_ratings: Current power ratings
            remaining_schedule: List of remaining games
            current_records: Current win/loss records

        Returns:
            Dictionary with season projections for all teams
        """
        if not self.monte_carlo:
            return self._basic_projection(teams, current_records)

        # Prepare schedule tuples
        schedule_tuples = [
            (game['home_team'], game['away_team'])
            for game in remaining_schedule
        ]

        # Run season simulation
        season_sims = self.monte_carlo.simulate_season(
            teams, team_ratings, schedule_tuples, sport
        )

        # Combine with current records
        projections = {}
        for team in teams:
            current = current_records.get(team, {'wins': 0, 'losses': 0, 'ties': 0})
            sim = season_sims.get(team, {})

            final_wins = current['wins'] + sim.get('projected_wins', 0)
            final_losses = current['losses'] + sim.get('projected_losses', 0)
            final_ties = current.get('ties', 0) + sim.get('projected_ties', 0)

            projections[team] = {
                'team': team,
                'current_record': f"{current['wins']}-{current['losses']}" +
                                (f"-{current.get('ties', 0)}" if current.get('ties') else ""),
                'projected_wins': round(final_wins, 1),
                'projected_losses': round(final_losses, 1),
                'projected_ties': round(final_ties, 1) if final_ties > 0 else 0,
                'playoff_probability': sim.get('playoff_probability', 0),
                'division_title_odds': self._calculate_division_odds(team, projections, sport),
                'championship_odds': self._calculate_championship_odds(
                    sim.get('playoff_probability', 0)
                ),
                'win_distribution': sim.get('win_distribution', []),
                'projection_date': datetime.now().isoformat(),
                'sport': sport
            }

        # Save projections
        self._save_projections(sport, projections)

        return projections

    def get_playoff_race(
        self,
        sport: str,
        projections: Dict[str, Dict],
        division: Optional[str] = None
    ) -> List[Dict]:
        """
        Get current playoff race standings with probabilities.

        Args:
            sport: Sport type
            projections: Season projections
            division: Optional division filter

        Returns:
            List of teams sorted by playoff probability
        """
        playoff_contenders = []

        for team, proj in projections.items():
            if division and not self._team_in_division(team, division):
                continue

            playoff_contenders.append({
                'team': team,
                'current_record': proj['current_record'],
                'projected_wins': proj['projected_wins'],
                'playoff_probability': proj['playoff_probability'],
                'magic_number': self._calculate_magic_number(proj, sport),
                'elimination_number': self._calculate_elimination_number(proj, sport)
            })

        # Sort by playoff probability
        playoff_contenders.sort(key=lambda x: x['playoff_probability'], reverse=True)

        return playoff_contenders

    def get_win_total_markets(
        self,
        projections: Dict[str, Dict],
        market_lines: Dict[str, float]
    ) -> List[Dict]:
        """
        Compare projections to win total betting markets.

        Args:
            projections: Season projections
            market_lines: Market win total lines

        Returns:
            List of value plays on win totals
        """
        value_plays = []

        for team, proj in projections.items():
            market_line = market_lines.get(team)
            if not market_line:
                continue

            projected_wins = proj['projected_wins']
            edge = projected_wins - market_line

            if abs(edge) >= 2.0:  # 2+ win edge
                value_plays.append({
                    'team': team,
                    'market_line': market_line,
                    'projected_wins': projected_wins,
                    'edge': round(edge, 1),
                    'recommendation': 'OVER' if edge > 0 else 'UNDER',
                    'confidence': min(abs(edge) / 5, 1.0)  # Scale to 0-1
                })

        # Sort by edge magnitude
        value_plays.sort(key=lambda x: abs(x['edge']), reverse=True)

        return value_plays

    def track_projection_accuracy(
        self,
        sport: str,
        actual_results: Dict[str, Dict]
    ) -> Dict:
        """
        Track accuracy of past projections.

        Args:
            sport: Sport type
            actual_results: Actual season results

        Returns:
            Dictionary with accuracy metrics
        """
        historical_projections = self._load_historical_projections(sport)
        if not historical_projections:
            return {'error': 'No historical projections found'}

        errors = []
        playoff_predictions = {'correct': 0, 'total': 0}

        for team, actual in actual_results.items():
            if team not in historical_projections:
                continue

            projected = historical_projections[team]
            actual_wins = actual.get('wins', 0)
            projected_wins = projected.get('projected_wins', 0)

            error = abs(actual_wins - projected_wins)
            errors.append(error)

            # Check playoff prediction
            made_playoffs = actual.get('made_playoffs', False)
            playoff_prob = projected.get('playoff_probability', 0)
            predicted_playoffs = playoff_prob > 0.5

            playoff_predictions['total'] += 1
            if predicted_playoffs == made_playoffs:
                playoff_predictions['correct'] += 1

        if not errors:
            return {'error': 'No matching data'}

        import statistics
        return {
            'mean_absolute_error': round(statistics.mean(errors), 2),
            'median_error': round(statistics.median(errors), 2),
            'max_error': max(errors),
            'playoff_accuracy': round(
                playoff_predictions['correct'] / playoff_predictions['total'], 3
            ) if playoff_predictions['total'] > 0 else 0,
            'teams_evaluated': len(errors),
            'sport': sport
        }

    def _basic_projection(self, teams: List[str], current_records: Dict) -> Dict:
        """Basic projection without Monte Carlo simulation."""
        projections = {}
        for team in teams:
            record = current_records.get(team, {'wins': 0, 'losses': 0})
            games_played = record['wins'] + record['losses']
            win_pct = record['wins'] / games_played if games_played > 0 else 0.5

            # Simple projection: current pace
            total_games = 82 if games_played > 50 else 17  # NBA vs NFL estimate
            projected_wins = win_pct * total_games

            projections[team] = {
                'team': team,
                'projected_wins': round(projected_wins, 1),
                'playoff_probability': 0.5 if win_pct > 0.5 else 0.3,
                'note': 'Basic projection - Monte Carlo not available'
            }

        return projections

    def _calculate_division_odds(self, team: str, projections: Dict, sport: str) -> float:
        """Calculate probability of winning division (simplified)."""
        # This would need division membership data
        return 0.25  # Placeholder

    def _calculate_championship_odds(self, playoff_prob: float) -> float:
        """Estimate championship odds based on playoff probability."""
        if playoff_prob < 0.3:
            return 0.01
        elif playoff_prob < 0.6:
            return 0.05
        elif playoff_prob < 0.8:
            return 0.10
        else:
            return 0.20

    def _calculate_magic_number(self, projection: Dict, sport: str) -> Optional[int]:
        """Calculate playoff magic number."""
        # Simplified - would need division/conference data
        return None

    def _calculate_elimination_number(self, projection: Dict, sport: str) -> Optional[int]:
        """Calculate elimination number."""
        # Simplified
        return None

    def _team_in_division(self, team: str, division: str) -> bool:
        """Check if team is in division."""
        # Would need division mapping
        return True

    def _save_projections(self, sport: str, projections: Dict):
        """Save projections to disk."""
        filepath = os.path.join(
            self.storage_path,
            f'{sport}_projections_{datetime.now().strftime("%Y%m%d")}.json'
        )
        try:
            with open(filepath, 'w') as f:
                json.dump(projections, f, indent=2)
        except Exception as e:
            print(f"Error saving projections: {e}")

    def _load_historical_projections(self, sport: str) -> Dict:
        """Load historical projections for accuracy tracking."""
        # Would load from historical files
        return {}
