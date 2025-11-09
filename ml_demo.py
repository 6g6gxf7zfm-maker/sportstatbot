#!/usr/bin/env python3
"""
Demo script for ML models in SportStatBot

Showcases the Performance Stability Index and Travel Fatigue Model
"""

from ml_models.predictive.stability_index import PerformanceStabilityAnalyzer
from ml_models.contextual.travel_fatigue import TravelFatigueModel


def demo_stability_index():
    """Demonstrate the Performance Stability Index"""
    print("=" * 80)
    print("🎯 PERFORMANCE STABILITY INDEX DEMO")
    print("=" * 80)

    analyzer = PerformanceStabilityAnalyzer()

    # Example 1: Consistent scorer (like Giannis)
    print("\n📊 Example 1: Consistent High-Volume Scorer")
    print("-" * 80)

    consistent_player = [
        {'points': 28, 'rebounds': 11, 'assists': 6, 'date': '2024-11-01'},
        {'points': 31, 'rebounds': 10, 'assists': 5, 'date': '2024-11-03'},
        {'points': 27, 'rebounds': 12, 'assists': 7, 'date': '2024-11-05'},
        {'points': 29, 'rebounds': 11, 'assists': 6, 'date': '2024-11-07'},
        {'points': 32, 'rebounds': 9, 'assists': 5, 'date': '2024-11-09'},
        {'points': 28, 'rebounds': 10, 'assists': 6, 'date': '2024-11-11'},
        {'points': 30, 'rebounds': 11, 'assists': 7, 'date': '2024-11-13'},
        {'points': 29, 'rebounds': 12, 'assists': 5, 'date': '2024-11-15'},
    ]

    print(analyzer.generate_report("Giannis Antetokounmpo", consistent_player, 'points'))

    # Example 2: Volatile scorer (boom-bust)
    print("\n\n📊 Example 2: Volatile Scorer (Boom-Bust Type)")
    print("-" * 80)

    volatile_player = [
        {'points': 12, 'rebounds': 5, 'assists': 2, 'date': '2024-11-01'},
        {'points': 38, 'rebounds': 8, 'assists': 9, 'date': '2024-11-03'},
        {'points': 8, 'rebounds': 3, 'assists': 1, 'date': '2024-11-05'},
        {'points': 42, 'rebounds': 11, 'assists': 7, 'date': '2024-11-07'},
        {'points': 15, 'rebounds': 4, 'assists': 3, 'date': '2024-11-09'},
        {'points': 35, 'rebounds': 9, 'assists': 8, 'date': '2024-11-11'},
        {'points': 10, 'rebounds': 2, 'assists': 2, 'date': '2024-11-13'},
        {'points': 40, 'rebounds': 10, 'assists': 6, 'date': '2024-11-15'},
    ]

    print(analyzer.generate_report("Jordan Poole", volatile_player, 'points'))

    # Example 3: Player comparison
    print("\n\n📊 Example 3: Player Comparison")
    print("-" * 80)

    players_data = {
        'Giannis Antetokounmpo': consistent_player,
        'Jordan Poole': volatile_player,
    }

    comparison = analyzer.compare_players(players_data, 'points')

    print("\n🏆 Stability Rankings:\n")
    for i, player in enumerate(comparison, 1):
        print(f"{i}. {player['player']}")
        print(f"   • Stability Index: {player['stability_index']}/100")
        print(f"   • Rating: {player['consistency_rating']}")
        print(f"   • Average: {player['mean_performance']} PPG")
        print(f"   • Reliability Score: {player['reliability_score']}/100")
        print()


def demo_travel_fatigue():
    """Demonstrate the Travel Fatigue Model"""
    print("\n\n" + "=" * 80)
    print("✈️ TRAVEL FATIGUE MODEL DEMO")
    print("=" * 80)

    model = TravelFatigueModel()

    # Example 1: Home game (baseline)
    print("\n📍 Example 1: Home Game (No Travel)")
    print("-" * 80)
    print(model.generate_report("Boston Celtics", "boston", "boston", 2))

    # Example 2: Short road trip
    print("\n\n📍 Example 2: Short Road Trip")
    print("-" * 80)
    print(model.generate_report("Boston Celtics", "boston", "philadelphia", 1))

    # Example 3: Cross-country trip
    print("\n\n📍 Example 3: West Coast Trip")
    print("-" * 80)
    print(model.generate_report("Boston Celtics", "boston", "portland", 1))

    # Example 4: Brutal back-to-back
    print("\n\n📍 Example 4: Cross-Country Back-to-Back")
    print("-" * 80)
    print(model.generate_report("Miami Heat", "portland", "miami", 0))

    # Example 5: Scenario comparison
    print("\n\n📊 Example 5: Scenario Comparison")
    print("-" * 80)

    scenarios = {
        'Home Game': {'from': 'boston', 'to': 'boston', 'rest': 2},
        'Division Rival': {'from': 'boston', 'to': 'new_york', 'rest': 1},
        'Midwest Trip': {'from': 'boston', 'to': 'chicago', 'rest': 1},
        'West Coast': {'from': 'boston', 'to': 'golden_state', 'rest': 1},
        'Denver High Altitude': {'from': 'miami', 'to': 'denver', 'rest': 1},
        'Coast-to-Coast B2B': {'from': 'portland', 'to': 'miami', 'rest': 0}
    }

    comparison = model.compare_scenarios(scenarios)

    print("\n🛫 Travel Impact Rankings (Easiest → Hardest):\n")
    sorted_scenarios = sorted(comparison.items(), key=lambda x: x[1]['fatigue_score'])

    for i, (scenario, data) in enumerate(sorted_scenarios, 1):
        impact_emoji = "✅" if data['fatigue_score'] < 3 else "⚠️" if data['fatigue_score'] < 6 else "🚨"
        print(f"{i}. {impact_emoji} {scenario}")
        print(f"   • Fatigue Score: {data['fatigue_score']:.1f}")
        print(f"   • Distance: {data['distance_miles']:,.0f} miles")
        print(f"   • Performance Impact: {data['performance_impact_pct']:+.1f}%")
        print()


def demo_combined_analysis():
    """Show how both models can work together"""
    print("\n\n" + "=" * 80)
    print("🧠 COMBINED ANALYSIS DEMO")
    print("=" * 80)
    print("\nHow to use Stability Index + Travel Fatigue together:\n")

    analyzer = PerformanceStabilityAnalyzer()
    travel_model = TravelFatigueModel()

    # Player stats
    player_logs = [
        {'points': 28, 'date': '2024-11-01'},
        {'points': 31, 'date': '2024-11-03'},
        {'points': 27, 'date': '2024-11-05'},
        {'points': 29, 'date': '2024-11-07'},
        {'points': 32, 'date': '2024-11-09'},
    ]

    # Get stability
    stability = analyzer.calculate_stability_index(player_logs, 'points')

    # Get travel impact for upcoming game
    travel = travel_model.calculate_fatigue_score(
        from_city='boston',
        to_city='portland',
        rest_days=1
    )

    print("📊 Player Analysis:")
    print(f"• Average Points: {stability['mean_performance']}")
    print(f"• Stability Index: {stability['stability_index']}/100")
    print(f"• Consistency: {stability['consistency_rating']}")

    print("\n✈️ Upcoming Game Context:")
    print(f"• Trip: Boston → Portland")
    print(f"• Travel Fatigue Score: {travel['fatigue_score']:.1f}")
    print(f"• Expected Impact: {travel['performance_impact_pct']:+.1f}%")

    # Adjust prediction
    base_prediction = stability['mean_performance']
    travel_adjusted = base_prediction * (1 + travel['performance_impact_pct'] / 100)

    print("\n🎯 Prediction:")
    print(f"• Base Prediction: {base_prediction:.1f} points")
    print(f"• Travel-Adjusted: {travel_adjusted:.1f} points")
    print(f"• Confidence: {'High' if stability['stability_index'] > 70 else 'Medium'} "
          f"(based on {stability['consistency_rating']})")

    print("\n💡 Insight:")
    if stability['stability_index'] > 70:
        print("High-consistency player should maintain production despite travel.")
    else:
        print("Volatile player + travel fatigue = higher risk of underperformance.")


def main():
    """Run all demos"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🏆 SPORTSTATBOT ML MODELS DEMO" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")

    demo_stability_index()
    demo_travel_fatigue()
    demo_combined_analysis()

    print("\n\n" + "=" * 80)
    print("✅ Demo Complete!")
    print("=" * 80)
    print("\nNext Steps:")
    print("• Integrate these models into the main report generator")
    print("• Add data fetching for real player game logs")
    print("• Implement additional models from DATA_SCIENCE_ROADMAP.md")
    print("• Train models on historical data")
    print("\nSee ml_models/README.md for development guidelines.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
