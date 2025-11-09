"""
Optimization Models

13. Lineup optimization via constrained linear programming
"""

import numpy as np
from typing import Dict, List, Optional, Tuple


class LineupOptimization:
    """
    Lineup optimization via constrained linear programming.

    Optimizes player lineups to maximize expected performance subject to
    constraints (salary cap, position requirements, chemistry, etc.).
    """

    def __init__(self, sport: str = 'basketball'):
        """
        Initialize lineup optimization model.

        Args:
            sport: Sport type (affects constraints)
        """
        self.sport = sport

        # Position requirements by sport
        self.position_requirements = {
            'basketball': {'G': 2, 'F': 2, 'C': 1},
            'football': {'QB': 1, 'RB': 2, 'WR': 3, 'TE': 1, 'K': 1, 'DEF': 1},
            'hockey': {'C': 2, 'W': 2, 'D': 2, 'G': 1},
            'soccer': {'GK': 1, 'D': 4, 'M': 3, 'F': 3}
        }

    def optimize_lineup(
        self,
        available_players: List[Dict],
        constraints: Dict,
        objective: str = 'maximize_points'
    ) -> Dict:
        """
        Optimize lineup selection.

        Args:
            available_players: List of player dicts with 'id', 'position',
                              'projected_points', 'salary', 'value'
            constraints: Constraint dict with 'salary_cap', 'max_players',
                        'position_requirements'
            objective: Optimization objective

        Returns:
            Optimal lineup
        """
        # Simple greedy optimization (in practice, use scipy.optimize or PuLP)
        # This is a simplified heuristic approach

        salary_cap = constraints.get('salary_cap', float('inf'))
        max_players = constraints.get('max_players', 9)
        position_reqs = constraints.get(
            'position_requirements',
            self.position_requirements.get(self.sport, {})
        )

        # Calculate value metric
        for player in available_players:
            if objective == 'maximize_points':
                player['optimization_value'] = player.get('projected_points', 0)
            elif objective == 'maximize_value':
                salary = player.get('salary', 1)
                player['optimization_value'] = player.get('projected_points', 0) / max(salary / 1000, 0.1)
            else:
                player['optimization_value'] = player.get('value', 0)

        # Sort by value
        sorted_players = sorted(
            available_players,
            key=lambda x: x['optimization_value'],
            reverse=True
        )

        # Greedy selection with constraints
        selected = []
        total_salary = 0
        position_counts = {pos: 0 for pos in position_reqs.keys()}

        for player in sorted_players:
            # Check constraints
            player_salary = player.get('salary', 0)
            player_position = player.get('position', '')

            # Position constraint
            if player_position in position_counts:
                required = position_reqs.get(player_position, 0)
                if position_counts[player_position] >= required:
                    continue

            # Salary constraint
            if total_salary + player_salary > salary_cap:
                continue

            # Max players constraint
            if len(selected) >= max_players:
                break

            # Add player
            selected.append(player)
            total_salary += player_salary
            if player_position in position_counts:
                position_counts[player_position] += 1

        # Calculate projected performance
        total_projected_points = sum(p.get('projected_points', 0) for p in selected)

        return {
            'optimal_lineup': selected,
            'total_projected_points': total_projected_points,
            'total_salary': total_salary,
            'salary_remaining': salary_cap - total_salary,
            'position_distribution': position_counts,
            'num_players': len(selected),
            'avg_value': total_projected_points / len(selected) if selected else 0
        }

    def optimize_with_stacking(
        self,
        available_players: List[Dict],
        constraints: Dict,
        stack_bonus: float = 1.1
    ) -> Dict:
        """
        Optimize lineup with team stacking bonus.

        Args:
            available_players: Available players
            constraints: Constraints dict
            stack_bonus: Multiplier for stacked players from same team

        Returns:
            Optimal lineup with stacking
        """
        # Count players by team
        from collections import defaultdict
        team_players = defaultdict(list)

        for player in available_players:
            team = player.get('team', 'unknown')
            team_players[team].append(player)

        # Try stacking strategies
        best_lineup = None
        best_score = 0

        # Strategy 1: No stacking (baseline)
        baseline = self.optimize_lineup(available_players, constraints)
        if baseline['total_projected_points'] > best_score:
            best_score = baseline['total_projected_points']
            best_lineup = baseline

        # Strategy 2: Stack top teams
        for team, players in team_players.items():
            if len(players) < 2:
                continue

            # Boost projected points for this team
            boosted_players = []
            for player in available_players:
                p_copy = player.copy()
                if p_copy.get('team') == team:
                    p_copy['projected_points'] = p_copy.get('projected_points', 0) * stack_bonus
                boosted_players.append(p_copy)

            stacked_lineup = self.optimize_lineup(boosted_players, constraints)

            # Count actual stacked players
            stacked_count = sum(
                1 for p in stacked_lineup['optimal_lineup']
                if p.get('team') == team
            )

            # Apply actual bonus
            actual_score = sum(
                p.get('projected_points', 0) * (stack_bonus if p.get('team') == team else 1.0)
                for p in stacked_lineup['optimal_lineup']
            )

            if actual_score > best_score:
                best_score = actual_score
                best_lineup = stacked_lineup
                best_lineup['stack_team'] = team
                best_lineup['stack_count'] = stacked_count
                best_lineup['adjusted_score'] = actual_score

        return best_lineup

    def calculate_lineup_chemistry(
        self,
        lineup: List[Dict]
    ) -> float:
        """
        Calculate chemistry/synergy score for lineup.

        Args:
            lineup: List of players in lineup

        Returns:
            Chemistry score (0-100)
        """
        if len(lineup) < 2:
            return 50.0

        chemistry_factors = []

        # Factor 1: Team chemistry (same team = good)
        teams = [p.get('team', '') for p in lineup]
        team_counts = {t: teams.count(t) for t in set(teams)}
        max_from_team = max(team_counts.values())

        if max_from_team >= 3:
            chemistry_factors.append(70 + (max_from_team - 3) * 5)
        else:
            chemistry_factors.append(50)

        # Factor 2: Position balance
        positions = [p.get('position', '') for p in lineup]
        position_variety = len(set(positions))

        if self.sport == 'basketball':
            ideal_variety = 3  # G, F, C
        elif self.sport == 'football':
            ideal_variety = 6
        else:
            ideal_variety = 4

        balance_score = min((position_variety / ideal_variety) * 100, 100)
        chemistry_factors.append(balance_score)

        # Factor 3: Experience mix (veterans + youth)
        if any('experience' in p for p in lineup):
            experiences = [p.get('experience', 5) for p in lineup]
            has_veteran = any(e > 8 for e in experiences)
            has_youth = any(e < 4 for e in experiences)

            if has_veteran and has_youth:
                chemistry_factors.append(70)
            elif has_veteran or has_youth:
                chemistry_factors.append(60)
            else:
                chemistry_factors.append(50)

        return np.mean(chemistry_factors)

    def sensitivity_analysis(
        self,
        lineup: List[Dict],
        player_id: str
    ) -> Dict:
        """
        Analyze sensitivity of lineup to player performance change.

        Args:
            lineup: Current lineup
            player_id: Player to analyze

        Returns:
            Sensitivity analysis
        """
        player = next((p for p in lineup if p.get('id') == player_id), None)

        if not player:
            return {'error': 'Player not in lineup'}

        base_points = player.get('projected_points', 0)

        # Calculate impact of ±20% performance change
        impacts = []
        for multiplier in [0.8, 0.9, 1.0, 1.1, 1.2]:
            adjusted_points = base_points * multiplier
            change = adjusted_points - base_points
            impacts.append({
                'multiplier': multiplier,
                'player_points': adjusted_points,
                'lineup_point_change': change,
                'pct_of_lineup': (change / sum(p.get('projected_points', 0) for p in lineup)) * 100
            })

        return {
            'player_id': player_id,
            'baseline_points': base_points,
            'impact_scenarios': impacts,
            'leverage': base_points / sum(p.get('projected_points', 0) for p in lineup)
        }
