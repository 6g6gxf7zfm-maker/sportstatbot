#!/usr/bin/env python3
"""
Knowledge Management CLI

Command-line interface for the sports knowledge management system
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

from knowledge_manager import (
    DocumentManager,
    FolderManager,
    MetadataManager,
    SearchEngine,
    QuickRecallAgent,
    StoryMemoryMap,
    ArchiveManager,
    EditorDashboard,
    DocumentExporter,
)
from knowledge_manager.indexer import AutoIndexer
from knowledge_manager.models import League, DocumentType


def create_document_command(args):
    """Create a new document"""
    dm = DocumentManager()
    fm = FolderManager()

    # Parse league and type
    league = League(args.league)
    doc_type = DocumentType(args.type)

    # Read content from file or stdin
    if args.file:
        with open(args.file, 'r') as f:
            content = f.read()
    else:
        print("Enter document content (Ctrl+D when done):")
        content = sys.stdin.read()

    # Parse tags
    tags = set(args.tags.split(',')) if args.tags else set()

    # Auto-tag if requested
    if args.auto_tag:
        mm = MetadataManager()
        auto_tags = mm.auto_tag_document(content, args.title)
        tags.update(auto_tags)
        print(f"Auto-detected tags: {', '.join(auto_tags)}")

    # Create document
    doc = dm.create_document(
        title=args.title,
        content=content,
        league=league,
        document_type=doc_type,
        folder_path=args.folder,
        authors=[args.author] if args.author else ['system'],
        tags=tags,
        season=args.season,
        week=args.week
    )

    # Add to folder
    fm.add_document_to_folder(args.folder, doc.doc_id)

    # Auto-link if requested
    if args.auto_link:
        smm = StoryMemoryMap()
        links = smm.auto_link_documents(doc.doc_id)
        print(f"Created {links} automatic links")

    print(f"✓ Document created: {doc.doc_id}")
    print(f"  Title: {doc.title}")
    print(f"  Folder: {args.folder}")
    print(f"  Tags: {', '.join(tags)}")


def search_command(args):
    """Search documents"""
    se = SearchEngine()

    # Parse parameters
    league = League(args.league) if args.league else None
    doc_type = DocumentType(args.type) if args.type else None
    tags = set(args.tags.split(',')) if args.tags else None

    # Perform search
    results = se.search(
        query=args.query,
        league=league,
        folder=args.folder,
        tags=tags,
        doc_type=doc_type
    )

    print(f"\n{'='*60}")
    print(f"Search Results: {len(results)} documents found")
    print(f"{'='*60}\n")

    for i, doc in enumerate(results[:args.limit], 1):
        print(f"{i}. {doc['title']}")
        print(f"   ID: {doc['doc_id']}")
        print(f"   League: {doc['metadata']['league']} | Type: {doc['metadata']['document_type']}")
        print(f"   Date: {doc['metadata']['date']}")
        if doc['metadata'].get('tags'):
            print(f"   Tags: {', '.join(doc['metadata']['tags'])}")
        print()

    # Export if requested
    if args.export:
        exporter = DocumentExporter()
        export_path = exporter.export_search_results(results, args.export)
        print(f"✓ Results exported to: {export_path}")


def recall_command(args):
    """Quick recall for player/team"""
    qr = QuickRecallAgent()

    result = qr.recall(args.entity, limit=args.limit)

    if not result['found']:
        print(f"No mentions found for '{args.entity}'")
        return

    print(f"\n{'='*60}")
    print(f"Quick Recall: {args.entity}")
    print(f"{'='*60}\n")
    print(result['summary'])
    print(f"\nTotal mentions: {result['total_mentions']}\n")

    for i, mention in enumerate(result['mentions'], 1):
        print(f"{i}. {mention['title']}")
        print(f"   Date: {mention['date']} | League: {mention['league']}")
        print(f"   Doc ID: {mention['doc_id']}")
        print()

    # Show timeline if requested
    if args.timeline:
        timeline = qr.get_entity_timeline(args.entity)
        print("\nTimeline:")
        for event in timeline[:10]:
            print(f"  {event['date']}: {event['title']}")


def dashboard_command(args):
    """Show editor dashboard"""
    dashboard = EditorDashboard()

    view = dashboard.get_dashboard_view(assignee=args.assignee)

    print(f"\n{'='*60}")
    print(f"Editor Dashboard")
    if args.assignee:
        print(f"Assignee: {args.assignee}")
    print(f"{'='*60}\n")

    print(f"TASKS:")
    print(f"  Total Pending: {view['tasks']['total_pending']}")
    print(f"  Overdue: {view['tasks']['overdue']}")
    print(f"  Due Soon: {view['tasks']['due_soon']}")
    print(f"\nBy Priority:")
    for priority, count in view['tasks']['by_priority'].items():
        if count > 0:
            print(f"  {priority.title()}: {count}")

    print(f"\nDOCUMENTS:")
    print(f"  Drafts: {view['documents']['drafts']}")
    print(f"  In Edit: {view['documents']['in_edit']}")
    print(f"  Ready to Publish: {view['documents']['ready_to_publish']}")

    if view['urgent_tasks']:
        print(f"\nURGENT TASKS:")
        for task in view['urgent_tasks'][:5]:
            print(f"  • {task['title']}")
            if task.get('deadline'):
                print(f"    Deadline: {task['deadline']}")

    if view['overdue_tasks']:
        print(f"\nOVERDUE TASKS:")
        for task in view['overdue_tasks'][:5]:
            print(f"  • {task['title']}")
            print(f"    Deadline: {task['deadline']}")

    # Weekly summary
    if args.weekly:
        summary = dashboard.get_weekly_summary(args.assignee)
        print(f"\nWEEKLY SUMMARY:")
        print(f"  Tasks Created: {summary['tasks_created']}")
        print(f"  Tasks Completed: {summary['tasks_completed']}")
        print(f"  Documents Published: {summary['documents_published']}")
        print(f"  Completion Rate: {summary['completion_rate']}%")


def export_command(args):
    """Export documents"""
    exporter = DocumentExporter()

    if args.doc_id:
        # Export single document
        if args.format == 'markdown':
            path = exporter.export_to_markdown(args.doc_id)
            print(f"✓ Exported to: {path}")
        elif args.format == 'pdf':
            path = exporter.export_to_pdf_markdown(args.doc_id, args.output)
            print(f"✓ PDF-ready markdown: {path}")
            print(f"  Convert to PDF with: pandoc {path} -o output.pdf")
        elif args.format == 'json':
            path = exporter.export_to_json(args.doc_id, args.output)
            print(f"✓ Exported to: {path}")

    elif args.weekly:
        # Export weekly briefing
        league = args.league
        week_start = datetime.now() - timedelta(days=7)
        week_end = datetime.now()

        path = exporter.export_weekly_briefing(league, week_start, week_end)
        print(f"✓ Weekly briefing exported: {path}")
        print(f"  Convert to PDF with: pandoc {path} -o briefing.pdf")


def index_command(args):
    """Generate indexes"""
    indexer = AutoIndexer()

    if args.type == 'weekly':
        league = League(args.league) if args.league else None
        index = indexer.build_weekly_index(league, weeks_back=args.weeks)

        print(f"\nWeekly Index - {index['league'].upper()}")
        print(f"Total Documents: {index['total_documents']}\n")

        for week, docs in list(index['weeks'].items())[:args.weeks]:
            print(f"\n{week} ({len(docs)} documents)")
            for doc in docs[:5]:
                print(f"  • {doc['title']} ({doc['league']})")
            if len(docs) > 5:
                print(f"  ... and {len(docs) - 5} more")

    elif args.type == 'sport':
        index = indexer.build_sport_index()

        print("\nIndex by Sport\n")
        for sport, data in index['sports'].items():
            print(f"{sport.upper()}: {data['total']} documents")
            for doc in data['recent_documents'][:3]:
                print(f"  • {doc['title']}")
            print()

    elif args.type == 'archive':
        summary = indexer.generate_archive_summary(days_back=args.days)
        print(summary)


def archive_command(args):
    """Archive management"""
    archiver = ArchiveManager()

    if args.action == 'auto':
        result = archiver.auto_archive(days_old=args.days, dry_run=args.dry_run)

        print(f"\nAuto-Archive Results")
        print(f"Cutoff Date: {result['cutoff_date']}")
        print(f"Candidates: {result['candidates']}")
        print(f"Archived: {result['archived']}")
        if args.dry_run:
            print("\n⚠️  DRY RUN - No documents were actually archived")

        if result['documents']:
            print("\nDocuments:")
            for doc in result['documents'][:10]:
                print(f"  • {doc['title']} ({doc['date']})")

    elif args.action == 'stats':
        stats = archiver.get_archive_stats()

        print(f"\nArchive Statistics")
        print(f"Total Archived: {stats['total_archived']}")
        print(f"Archive Size: {stats['archive_size_mb']} MB")
        print(f"\nBy League:")
        for league, count in stats['by_league'].items():
            print(f"  {league}: {count}")

    elif args.action == 'cleanup':
        result = archiver.schedule_cleanup()
        print("\n✓ Cleanup completed")
        print(f"  Archived: {result['auto_archive']['archived']}")
        print(f"  Revisions deleted: {result['revision_cleanup']['revisions_deleted']}")


def story_map_command(args):
    """View story memory map"""
    smm = StoryMemoryMap()

    if args.action == 'view':
        story_map = smm.get_story_map(args.doc_id, depth=args.depth)

        print(f"\nStory Memory Map for: {args.doc_id}")
        print(f"Total Nodes: {len(story_map['nodes'])}")
        print(f"Total Edges: {len(story_map['edges'])}\n")

        print("Connected Stories:")
        for node in story_map['nodes'][:10]:
            depth_indent = "  " * node['depth']
            print(f"{depth_indent}• {node['title']} (depth: {node['depth']})")

    elif args.action == 'correlation':
        matrix = smm.get_story_correlation_matrix(args.team)

        print(f"\nStory Correlation Matrix: {args.team}")
        print(f"Total Mentions: {matrix['total_mentions']}\n")
        print("Teams appearing with " + args.team + ":")

        for team, count in list(matrix['co_occurrences'].items())[:10]:
            print(f"  {team}: {count} times")

    elif args.action == 'clusters':
        clusters = smm.find_story_clusters(min_cluster_size=args.min_size)

        print(f"\nStory Clusters Found: {len(clusters)}\n")

        for i, cluster in enumerate(clusters[:5], 1):
            print(f"{i}. Cluster Size: {cluster['size']}")
            print(f"   Common Teams: {', '.join(cluster['common_teams'])}")
            print(f"   Common Tags: {', '.join(cluster['common_tags'])}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description='Sports Knowledge Management System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create document
    create_parser = subparsers.add_parser('create', help='Create a new document')
    create_parser.add_argument('title', help='Document title')
    create_parser.add_argument('--league', required=True, choices=[l.value for l in League])
    create_parser.add_argument('--type', required=True, choices=[t.value for t in DocumentType])
    create_parser.add_argument('--folder', required=True, help='Folder path')
    create_parser.add_argument('--file', help='Read content from file')
    create_parser.add_argument('--author', default='system', help='Author name')
    create_parser.add_argument('--tags', help='Comma-separated tags')
    create_parser.add_argument('--auto-tag', action='store_true', help='Auto-detect tags')
    create_parser.add_argument('--auto-link', action='store_true', help='Auto-link related stories')
    create_parser.add_argument('--season', help='Season (e.g., 2024-25)')
    create_parser.add_argument('--week', type=int, help='Week number')

    # Search
    search_parser = subparsers.add_parser('search', help='Search documents')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--league', choices=[l.value for l in League])
    search_parser.add_argument('--type', choices=[t.value for t in DocumentType])
    search_parser.add_argument('--folder', help='Filter by folder')
    search_parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    search_parser.add_argument('--limit', type=int, default=20, help='Result limit')
    search_parser.add_argument('--export', help='Export results to file')

    # Quick recall
    recall_parser = subparsers.add_parser('recall', help='Quick recall player/team')
    recall_parser.add_argument('entity', help='Player or team name')
    recall_parser.add_argument('--limit', type=int, default=5, help='Number of mentions')
    recall_parser.add_argument('--timeline', action='store_true', help='Show timeline')

    # Dashboard
    dash_parser = subparsers.add_parser('dashboard', help='Show editor dashboard')
    dash_parser.add_argument('--assignee', help='Filter by assignee')
    dash_parser.add_argument('--weekly', action='store_true', help='Show weekly summary')

    # Export
    export_parser = subparsers.add_parser('export', help='Export documents')
    export_parser.add_argument('--doc-id', help='Document ID to export')
    export_parser.add_argument('--format', choices=['markdown', 'pdf', 'json'], default='markdown')
    export_parser.add_argument('--output', help='Output filename')
    export_parser.add_argument('--weekly', action='store_true', help='Export weekly briefing')
    export_parser.add_argument('--league', help='League for weekly export')

    # Index
    index_parser = subparsers.add_parser('index', help='Generate indexes')
    index_parser.add_argument('type', choices=['weekly', 'sport', 'archive'])
    index_parser.add_argument('--league', choices=[l.value for l in League])
    index_parser.add_argument('--weeks', type=int, default=4, help='Weeks to include')
    index_parser.add_argument('--days', type=int, default=7, help='Days for archive summary')

    # Archive
    archive_parser = subparsers.add_parser('archive', help='Archive management')
    archive_parser.add_argument('action', choices=['auto', 'stats', 'cleanup'])
    archive_parser.add_argument('--days', type=int, default=30, help='Archive after N days')
    archive_parser.add_argument('--dry-run', action='store_true', help='Dry run')

    # Story map
    map_parser = subparsers.add_parser('story-map', help='Story memory map')
    map_parser.add_argument('action', choices=['view', 'correlation', 'clusters'])
    map_parser.add_argument('--doc-id', help='Document ID')
    map_parser.add_argument('--depth', type=int, default=2, help='Map depth')
    map_parser.add_argument('--team', help='Team name for correlation')
    map_parser.add_argument('--min-size', type=int, default=3, help='Min cluster size')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate command
    commands = {
        'create': create_document_command,
        'search': search_command,
        'recall': recall_command,
        'dashboard': dashboard_command,
        'export': export_command,
        'index': index_command,
        'archive': archive_command,
        'story-map': story_map_command,
    }

    try:
        commands[args.command](args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
