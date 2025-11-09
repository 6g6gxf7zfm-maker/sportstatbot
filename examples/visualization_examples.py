"""
Sports Analytics Visualization Examples

Complete examples for all 25 visualization features (26-50).
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from visualizations.charts.heatmaps import EPAHeatmap, CalendarHeatmap
from visualizations.charts.trajectories import ShotTrajectory
from visualizations.charts.timelines import MomentumTimeline
from visualizations.charts.scatter_plots import LuckVsSkillScatter
from visualizations.charts.probability_charts import PlayoffProbabilityFan, ProbabilityTicker
from visualizations.charts.radar_charts import PlayerRadarComparison
from visualizations.charts.worm_graphs import ScoreWormGraph
from visualizations.charts.tree_maps import LineupTreeMap
from visualizations.charts.flow_diagrams import TurnoverFlowDiagram, BallMovementChord
from visualizations.charts.xg_visualizations import XGDifferenceField, ExpectedGoalDensity
from visualizations.charts.depth_charts import DepthChartVisualization
from visualizations.charts.progress_bars import SeasonProgressBar
from visualizations.charts.histograms import ShotDistanceHistogram
from visualizations.charts.voronoi_maps import PositionalAreaControl
from visualizations.animations.win_path import WinPathVideo
from visualizations.animations.gif_exporter import PlaySequenceGIF
from visualizations.overlays.broadcast_overlay import BroadcastOverlay
from visualizations.overlays.confidence_glow import ConfidenceGlow
from visualizations.integrations.apple_notes import AppleNotesIntegration


def example_1_epa_heatmap():
    """Feature 26: EPA Heatmap"""
    print("Creating EPA Heatmap...")

    heatmap = EPAHeatmap(title="NFL EPA Analysis", dark_mode=False)

    # Use sample data (or provide your own)
    fig = heatmap.create(data={}, animate=True, frame_duration=500)

    # Save
    output_path = heatmap.save('epa_heatmap', format='html')
    print(f"Saved to: {output_path}")

    return fig


def example_2_shot_trajectory():
    """Feature 27: Shot Trajectory"""
    print("Creating Shot Trajectory...")

    trajectory = ShotTrajectory(sport='basketball')
    fig = trajectory.create(data={}, animate=True)

    trajectory.save('shot_trajectory', format='html')
    print("Saved shot trajectory")

    return fig


def example_3_momentum_timeline():
    """Feature 28: Momentum Timeline"""
    print("Creating Momentum Timeline...")

    timeline = MomentumTimeline()
    fig = timeline.create(data={})

    timeline.save('momentum_timeline', format='html')
    return fig


def example_4_luck_vs_skill():
    """Feature 29: Luck vs Skill Scatter"""
    print("Creating Luck vs Skill Analysis...")

    scatter = LuckVsSkillScatter()
    fig = scatter.create(data={})

    scatter.save('luck_vs_skill', format='html')
    return fig


def example_5_playoff_probability():
    """Feature 30: Playoff Probability Fan Chart"""
    print("Creating Playoff Probability Chart...")

    fan_chart = PlayoffProbabilityFan()
    fig = fan_chart.create(data={})

    fan_chart.save('playoff_probability', format='html')
    return fig


def example_6_player_radar():
    """Feature 31: Player Radar Comparison"""
    print("Creating Player Radar Comparison...")

    radar = PlayerRadarComparison()
    fig = radar.create(data={})

    radar.save('player_radar', format='html')
    return fig


def example_7_score_worm():
    """Feature 32: Score Worm Graph"""
    print("Creating Score Worm Graph...")

    worm = ScoreWormGraph()
    fig = worm.create(data={})

    worm.save('score_worm', format='html')
    return fig


def example_8_lineup_treemap():
    """Feature 33: Lineup Tree Map"""
    print("Creating Lineup Tree Map...")

    treemap = LineupTreeMap()
    fig = treemap.create(data={})

    treemap.save('lineup_treemap', format='html')
    return fig


def example_9_turnover_flow():
    """Feature 34: Turnover Flow Diagram"""
    print("Creating Turnover Flow Diagram...")

    flow = TurnoverFlowDiagram()
    fig = flow.create(data={})

    flow.save('turnover_flow', format='html')
    return fig


def example_10_xg_field():
    """Feature 35: xG Difference Field"""
    print("Creating xG Difference Field...")

    xg = XGDifferenceField(sport='soccer')
    fig = xg.create(data={})

    xg.save('xg_field', format='html')
    return fig


def example_11_win_path():
    """Feature 36: Win Path Video"""
    print("Creating Win Path Animation...")

    win_path = WinPathVideo()
    fig = win_path.create(data={})

    win_path.save('win_path', format='html')
    return fig


def example_12_broadcast_overlay():
    """Feature 37: Broadcast Overlay"""
    print("Creating Broadcast Overlay...")

    overlay = BroadcastOverlay()
    scoreboard = overlay.create_scoreboard(data={})

    overlay.save('broadcast_overlay', format='html')
    return scoreboard


def example_13_depth_chart():
    """Feature 38: Depth Chart"""
    print("Creating Depth Chart...")

    depth = DepthChartVisualization()
    fig = depth.create(data={})

    depth.save('depth_chart', format='html')
    return fig


def example_14_goal_density():
    """Feature 39: Expected Goal Density"""
    print("Creating Goal Density Surface...")

    density = ExpectedGoalDensity()
    fig = density.create(data={})

    density.save('goal_density', format='html')
    return fig


def example_15_ball_movement():
    """Feature 40: Ball Movement Chord"""
    print("Creating Ball Movement Diagram...")

    chord = BallMovementChord()
    fig = chord.create(data={})

    chord.save('ball_movement', format='html')
    return fig


def example_16_season_progress():
    """Feature 41: Season Progress Bar"""
    print("Creating Season Progress Bar...")

    progress = SeasonProgressBar()
    fig = progress.create(data={})

    progress.save('season_progress', format='html')
    return fig


def example_17_calendar_heatmap():
    """Feature 42: Calendar Heatmap"""
    print("Creating Calendar Heatmap...")

    calendar = CalendarHeatmap()
    fig = calendar.create(data={})

    calendar.save('calendar_heatmap', format='html')
    return fig


def example_18_probability_ticker():
    """Feature 43: Probability Ticker"""
    print("Creating Probability Ticker...")

    ticker = ProbabilityTicker()
    fig = ticker.create(data={})

    ticker.save('probability_ticker', format='html')
    return fig


def example_19_confidence_glow():
    """Feature 46: Confidence Glow"""
    print("Creating Confidence Glow Visualization...")

    glow = ConfidenceGlow()
    fig = glow.create(data={})

    glow.save('confidence_glow', format='html')
    return fig


def example_20_voronoi_map():
    """Feature 47: Voronoi Area Control"""
    print("Creating Voronoi Area Control Map...")

    voronoi = PositionalAreaControl(sport='soccer')
    fig = voronoi.create(data={})

    voronoi.save('voronoi_map', format='html')
    return fig


def example_21_shot_histogram():
    """Feature 48: Shot Distance Histogram"""
    print("Creating Shot Distance Histogram...")

    histogram = ShotDistanceHistogram()
    fig = histogram.create(data={})

    histogram.save('shot_histogram', format='html')
    return fig


def example_22_play_sequence_gif():
    """Feature 49: Play Sequence GIF"""
    print("Creating Play Sequence GIF...")

    gif_exporter = PlaySequenceGIF()
    gif_path = gif_exporter.create_gif(
        data={},
        filename='play_sequence',
        fps=2
    )

    print(f"GIF saved to: {gif_path}")
    return gif_path


def example_23_apple_notes():
    """Feature 50: Apple Notes Integration"""
    print("Testing Apple Notes Integration...")

    notes = AppleNotesIntegration()

    if notes.notes_available:
        # Example: Export a chart to Notes
        # First create and save a chart
        radar = PlayerRadarComparison()
        fig = radar.create(data={})
        chart_path = radar.save('sample_chart', format='png')

        # Export to Notes (macOS only)
        success = notes.export_to_notes(
            chart_path=chart_path,
            note_title='Sports Analytics Example',
            note_body='Sample visualization export'
        )

        if success:
            print("Successfully exported to Apple Notes!")
        else:
            print("Failed to export to Notes")
    else:
        print("Apple Notes not available (macOS only)")


def run_all_examples():
    """Run all visualization examples"""
    print("=" * 60)
    print("SPORTS ANALYTICS VISUALIZATION EXAMPLES")
    print("=" * 60)

    examples = [
        example_1_epa_heatmap,
        example_2_shot_trajectory,
        example_3_momentum_timeline,
        example_4_luck_vs_skill,
        example_5_playoff_probability,
        example_6_player_radar,
        example_7_score_worm,
        example_8_lineup_treemap,
        example_9_turnover_flow,
        example_10_xg_field,
        example_11_win_path,
        example_12_broadcast_overlay,
        example_13_depth_chart,
        example_14_goal_density,
        example_15_ball_movement,
        example_16_season_progress,
        example_17_calendar_heatmap,
        example_18_probability_ticker,
        example_19_confidence_glow,
        example_20_voronoi_map,
        example_21_shot_histogram,
        example_22_play_sequence_gif,
        # example_23_apple_notes,  # macOS only
    ]

    for i, example_func in enumerate(examples, 1):
        print(f"\n[{i}/{len(examples)}] {example_func.__doc__}")
        try:
            example_func()
            print("✓ Success")
        except Exception as e:
            print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED!")
    print("=" * 60)
    print("\nOutput files saved to: visualizations/output/")
    print("\nTo view dashboard:")
    print("  python visualizations/dashboard/app.py")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run visualization examples')
    parser.add_argument('--all', action='store_true', help='Run all examples')
    parser.add_argument('--example', type=int, help='Run specific example (1-23)')

    args = parser.parse_args()

    if args.all:
        run_all_examples()
    elif args.example:
        examples = [
            example_1_epa_heatmap, example_2_shot_trajectory, example_3_momentum_timeline,
            example_4_luck_vs_skill, example_5_playoff_probability, example_6_player_radar,
            example_7_score_worm, example_8_lineup_treemap, example_9_turnover_flow,
            example_10_xg_field, example_11_win_path, example_12_broadcast_overlay,
            example_13_depth_chart, example_14_goal_density, example_15_ball_movement,
            example_16_season_progress, example_17_calendar_heatmap, example_18_probability_ticker,
            example_19_confidence_glow, example_20_voronoi_map, example_21_shot_histogram,
            example_22_play_sequence_gif, example_23_apple_notes
        ]

        if 1 <= args.example <= len(examples):
            examples[args.example - 1]()
        else:
            print(f"Invalid example number. Choose 1-{len(examples)}")
    else:
        print("Usage:")
        print("  python examples/visualization_examples.py --all")
        print("  python examples/visualization_examples.py --example 1")
