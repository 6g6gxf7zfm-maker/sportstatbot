"""Command-line interface for SportStatBot Search Engine."""
import argparse
import sys
from typing import Optional
from search_engine import SportStatSearchEngine
from data_fetchers.espn_fetcher import ESPNFetcher


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 80 + "\n")


def format_search_results(results: list) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    output = []

    for i, result in enumerate(results, 1):
        output.append(f"\n**Result {i}:**")

        # Show metadata if available
        metadata = result.get('metadata', {})
        if metadata:
            if metadata.get('sport'):
                output.append(f"  Sport: {metadata['sport'].upper()}")
            if metadata.get('date'):
                output.append(f"  Date: {metadata['date']}")
            if metadata.get('teams'):
                output.append(f"  Teams: {', '.join(metadata['teams'])}")

        # Show content snippet
        content = result.get('content', '')
        if len(content) > 200:
            content = content[:200] + "..."

        output.append(f"\n{content}\n")

        # Show relevance score if available
        if 'distance' in result:
            output.append(f"  Relevance: {1 - result['distance']:.2f}")
        elif 'similarity' in result:
            output.append(f"  Similarity: {result['similarity']:.2f}")

    return '\n'.join(output)


def format_comparison(comparison: dict) -> str:
    """Format comparison results for display."""
    output = []

    entity1_name = comparison.get('player1', {}).get('name') or comparison.get('team1', 'Entity 1')
    entity2_name = comparison.get('player2', {}).get('name') or comparison.get('team2', 'Entity 2')

    output.append(f"\n**Comparing {entity1_name} vs {entity2_name}**\n")

    # Show individual stats
    stats1 = comparison.get('player1', {}).get('stats') or comparison.get('comparisons', {})
    stats2 = comparison.get('player2', {}).get('stats') or {}

    if stats1:
        output.append(f"\n{entity1_name} Stats:")
        for stat, value in list(stats1.items())[:10]:
            output.append(f"  {stat}: {value}")

    if stats2:
        output.append(f"\n{entity2_name} Stats:")
        for stat, value in list(stats2.items())[:10]:
            output.append(f"  {stat}: {value}")

    # Show winner if available
    winner = comparison.get('winner') or comparison.get('overall_advantage')
    if winner:
        if winner == 'entity1' or winner == 'team1':
            output.append(f"\n**Advantage: {entity1_name}**")
        elif winner == 'entity2' or winner == 'team2':
            output.append(f"\n**Advantage: {entity2_name}**")
        else:
            output.append(f"\n**Result: {winner}**")

    return '\n'.join(output)


def handle_query_command(args, engine: SportStatSearchEngine):
    """Handle natural language query."""
    print(f"\nQuery: {args.query}")
    print_separator()

    result = engine.query(args.query, top_k=args.limit)

    query_type = result.get('query_type')
    answer = result.get('answer')

    if query_type == 'stat_explanation':
        print(answer)

    elif query_type == 'comparison':
        if isinstance(answer, dict):
            print(format_comparison(answer))
        else:
            print(answer)

    elif isinstance(answer, list):
        print(format_search_results(answer))

    elif isinstance(answer, dict):
        # Generic dict answer
        import json
        print(json.dumps(answer, indent=2))

    else:
        print(answer)

    print_separator()


def handle_search_command(args, engine: SportStatSearchEngine):
    """Handle semantic search through reports."""
    print(f"\nSearching: {args.query}")
    print_separator()

    results = engine.ask_the_story(args.query, top_k=args.limit)
    print(format_search_results(results))

    print_separator()


def handle_explain_command(args, engine: SportStatSearchEngine):
    """Handle stat explanation."""
    print(f"\nExplaining: {args.stat}")
    print_separator()

    explanation = engine.explain_stat(args.stat)
    print(explanation)

    print_separator()


def handle_compare_command(args, engine: SportStatSearchEngine):
    """Handle comparison."""
    print(f"\nComparing: {args.entity1} vs {args.entity2}")
    if args.aspect:
        print(f"Aspect: {args.aspect}")

    print_separator()

    comparison = engine.compare(
        args.entity1,
        args.entity2,
        aspect=args.aspect,
        time_period=args.period
    )

    print(format_comparison(comparison))
    print_separator()


def handle_history_command(args, engine: SportStatSearchEngine):
    """Handle historical lookup."""
    print(f"\nFinding: {args.event}")
    if args.team:
        print(f"Team: {args.team}")

    print_separator()

    result = engine.find_last_occurrence(
        args.event,
        team=args.team,
        player=args.player
    )

    if result:
        print(format_search_results([result]))
    else:
        print("No historical occurrence found.")

    print_separator()


def handle_story_command(args, engine: SportStatSearchEngine):
    """Handle stats-to-story generation."""
    print("\nGenerating story from stats...")
    print_separator()

    # Parse stats from command line
    # Expected format: "player=Name stat1=value1 stat2=value2"
    data = {}

    for item in args.data:
        if '=' in item:
            key, value = item.split('=', 1)

            # Try to parse as number
            try:
                value = float(value)
            except ValueError:
                pass  # Keep as string

            if key == 'player' or key == 'team':
                data[key] = value
            elif key == 'stats':
                # Already a dict
                data['stats'] = data.get('stats', {})
            else:
                # Add to stats
                data['stats'] = data.get('stats', {})
                data['stats'][key] = value

    story = engine.stats_to_story(data, story_type=args.type)
    print(story)

    print_separator()


def handle_glossary_command(args, engine: SportStatSearchEngine):
    """Handle glossary search."""
    if args.list_all:
        print("\nAll Stats in Glossary:")
        print_separator()

        all_stats = engine.stats_glossary.get_all_stats_list()
        for stat in sorted(all_stats):
            info = engine.stats_glossary.get_stat_info(stat)
            print(f"{stat:10} - {info['name']}")

    elif args.search:
        print(f"\nSearching glossary: {args.search}")
        print_separator()

        results = engine.search_stats_glossary(args.search, sport=args.sport)

        for result in results:
            print(f"\n**{result['key']}** - {result['name']}")
            print(f"  Sport: {result['sport']}")
            print(f"  Definition: {result['definition']}")

    elif args.sport:
        print(f"\nStats for {args.sport.upper()}:")
        print_separator()

        stats = engine.stats_glossary.get_stats_by_sport(args.sport)

        for stat in stats:
            print(f"\n**{stat['key']}** - {stat['name']}")
            print(f"  {stat['definition']}")

    print_separator()


def handle_stats_command(args, engine: SportStatSearchEngine):
    """Show search engine statistics."""
    print("\nSearch Engine Statistics:")
    print_separator()

    stats = engine.get_stats()

    print(f"Semantic Search:")
    sem_stats = stats.get('semantic_search', {})
    print(f"  Total Documents: {sem_stats.get('total_documents', 0)}")
    print(f"  Embedding Model: {sem_stats.get('embedding_model', 'None')}")
    print(f"  Vector DB Enabled: {sem_stats.get('vector_db_enabled', False)}")

    print(f"\nReport Storage:")
    storage_stats = stats.get('storage', {})
    print(f"  Total Reports: {storage_stats.get('total_reports', 0)}")
    print(f"  Total Sections: {storage_stats.get('total_sections', 0)}")
    print(f"  Oldest Report: {storage_stats.get('oldest_report', 'N/A')}")
    print(f"  Newest Report: {storage_stats.get('newest_report', 'N/A')}")

    print(f"\nStats Glossary:")
    print(f"  Total Stat Definitions: {stats.get('glossary_stats', 0)}")

    print_separator()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='SportStatBot Search Engine - Natural Language Sports Query System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Natural language query
  python search_cli.py query "Which teams have the best net rating since March?"

  # Search past reports
  python search_cli.py search "Celtics injuries" --limit 5

  # Explain a stat
  python search_cli.py explain EPA

  # Compare entities
  python search_cli.py compare "Patrick Mahomes" "Josh Allen" --aspect passing

  # Find historical event
  python search_cli.py history "lost 3 straight" --team Celtics

  # Generate story from stats
  python search_cli.py story player=Mahomes points=350 touchdowns=4

  # Browse glossary
  python search_cli.py glossary --sport nfl
  python search_cli.py glossary --search "efficiency"
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Query command
    query_parser = subparsers.add_parser('query', help='Natural language query')
    query_parser.add_argument('query', help='Natural language query')
    query_parser.add_argument('--limit', type=int, default=5, help='Number of results')

    # Search command
    search_parser = subparsers.add_parser('search', help='Semantic search through reports')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=5, help='Number of results')

    # Explain command
    explain_parser = subparsers.add_parser('explain', help='Explain a stat')
    explain_parser.add_argument('stat', help='Stat abbreviation (e.g., EPA, TS%, wRC+)')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare two entities')
    compare_parser.add_argument('entity1', help='First entity (player or team)')
    compare_parser.add_argument('entity2', help='Second entity')
    compare_parser.add_argument('--aspect', help='Aspect to compare')
    compare_parser.add_argument('--period', help='Time period')

    # History command
    history_parser = subparsers.add_parser('history', help='Find historical occurrence')
    history_parser.add_argument('event', help='Event description')
    history_parser.add_argument('--team', help='Team name')
    history_parser.add_argument('--player', help='Player name')

    # Story command
    story_parser = subparsers.add_parser('story', help='Generate story from stats')
    story_parser.add_argument('data', nargs='+', help='Data in key=value format')
    story_parser.add_argument('--type', default='auto', help='Story type')

    # Glossary command
    glossary_parser = subparsers.add_parser('glossary', help='Browse stats glossary')
    glossary_parser.add_argument('--sport', help='Filter by sport')
    glossary_parser.add_argument('--search', help='Search glossary')
    glossary_parser.add_argument('--list-all', action='store_true', help='List all stats')

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show search engine statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize search engine
    print("Initializing search engine...")

    try:
        data_fetcher = ESPNFetcher()
        engine = SportStatSearchEngine(data_fetcher=data_fetcher)

        # Route to appropriate handler
        if args.command == 'query':
            handle_query_command(args, engine)

        elif args.command == 'search':
            handle_search_command(args, engine)

        elif args.command == 'explain':
            handle_explain_command(args, engine)

        elif args.command == 'compare':
            handle_compare_command(args, engine)

        elif args.command == 'history':
            handle_history_command(args, engine)

        elif args.command == 'story':
            handle_story_command(args, engine)

        elif args.command == 'glossary':
            handle_glossary_command(args, engine)

        elif args.command == 'stats':
            handle_stats_command(args, engine)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
