#!/usr/bin/env python3
"""
Demo script for Sports Knowledge Management System

This demonstrates the key features of the knowledge management system.
Run this script to see the system in action!
"""

from datetime import datetime, timedelta
from knowledge_manager import (
    DocumentManager,
    FolderManager,
    MetadataManager,
    SearchEngine,
    QuickRecallAgent,
    StoryMemoryMap,
    EditorDashboard,
)
from knowledge_manager.indexer import AutoIndexer
from knowledge_manager.models import League, DocumentType


def demo_header(title):
    """Print a demo section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_document_creation():
    """Demo: Creating documents"""
    demo_header("1. Creating Documents")

    dm = DocumentManager()
    fm = FolderManager()

    # Create a sample document
    doc1 = dm.create_document(
        title="Chiefs Defeat Bills in Thrilling Showdown",
        content="""
**Kansas City Chiefs 31, Buffalo Bills 28**

In a game that lived up to the hype, the Kansas City Chiefs edged past
the Buffalo Bills 31-28 in a playoff preview that had fans on the edge
of their seats.

**Standout Performances:**
- Patrick Mahomes: 368 passing yards, 3 touchdowns
- Josh Allen: 342 passing yards, 2 touchdowns
- Travis Kelce: 9 catches, 121 yards, 2 TDs

The Chiefs improved to 8-2 on the season, maintaining their lead in the
AFC West. The Bills fall to 7-3 but remain in playoff contention.

This victory extends the Chiefs' win streak to 5 games and solidifies
their position as Super Bowl contenders.
        """.strip(),
        league=League.NFL,
        document_type=DocumentType.RECAP,
        folder_path="/NFL/Weekly Digests/2025-11-08",
        authors=["Demo Author"],
        tags={"chiefs", "bills", "playoff-preview", "mahomes"},
        season="2024-25",
        week=10
    )

    print(f"✓ Created document: {doc1.title}")
    print(f"  ID: {doc1.doc_id}")
    print(f"  League: {doc1.metadata.league.value}")
    print(f"  Tags: {', '.join(doc1.metadata.tags)}")
    print(f"  Auto-detected teams: {', '.join(doc1.metadata.teams)}")
    print(f"  Auto-detected players: {', '.join(doc1.metadata.players[:5])}")

    # Create another related document
    doc2 = dm.create_document(
        title="Mahomes Named AFC Offensive Player of the Week",
        content="""
Kansas City Chiefs quarterback Patrick Mahomes has been named AFC Offensive
Player of the Week following his stellar performance against the Buffalo Bills.

Mahomes threw for 368 yards and 3 touchdowns in the Chiefs' 31-28 victory,
including two touchdown passes to Travis Kelce. His EPA per play was an
impressive 0.31, well above the league average.

This marks Mahomes' third Player of the Week honor this season.
        """.strip(),
        league=League.NFL,
        document_type=DocumentType.FEATURE,
        folder_path="/NFL/Features/Stars",
        authors=["Demo Author"],
        tags={"mahomes", "chiefs", "awards"},
        season="2024-25"
    )

    print(f"\n✓ Created document: {doc2.title}")
    print(f"  ID: {doc2.doc_id}")

    # Add to folder
    fm.add_document_to_folder("/NFL/Weekly Digests/2025-11-08", doc1.doc_id)

    return doc1.doc_id, doc2.doc_id


def demo_auto_tagging():
    """Demo: Auto-tagging"""
    demo_header("2. Auto-Tagging")

    mm = MetadataManager()

    content = """
LeBron James suffered a minor ankle injury during last night's game against
the Celtics. The Lakers star is listed as questionable for tomorrow's matchup.
    """.strip()

    suggested_tags = mm.auto_tag_document(content, "Lakers Star Questionable")

    print("Sample content:")
    print(f'  "{content}"')
    print(f"\nAuto-detected tags:")
    for tag in suggested_tags:
        print(f"  • #{tag}")


def demo_search():
    """Demo: Searching"""
    demo_header("3. Searching Documents")

    se = SearchEngine()

    # Text search
    results = se.search("Mahomes")

    print(f"Search results for 'Mahomes': {len(results)} found\n")
    for i, doc in enumerate(results[:3], 1):
        print(f"{i}. {doc['title']}")
        print(f"   League: {doc['metadata']['league']} | Type: {doc['metadata']['document_type']}")
        print(f"   Tags: {', '.join(doc['metadata'].get('tags', []))}\n")

    # Search by stat
    stat_results = se.search_by_stat("yards", ">", 300)
    print(f"\nStories with 'yards > 300': {len(stat_results)} found")
    for doc in stat_results[:2]:
        stats = doc.get('metadata', {}).get('stats_mentioned', {})
        print(f"  • {doc['title']}")
        print(f"    Yards: {stats.get('yards', 'N/A')}")


def demo_quick_recall(doc_id1, doc_id2):
    """Demo: Quick Recall"""
    demo_header("4. Quick Recall Agent")

    qr = QuickRecallAgent()

    # Recall player
    result = qr.recall("Mahomes", limit=5)

    print(f"Quick Recall: Mahomes\n")
    print(result['summary'])
    print(f"\nMentions found: {result['total_mentions']}\n")

    for i, mention in enumerate(result['mentions'][:3], 1):
        print(f"{i}. {mention['title']}")
        print(f"   Date: {mention['date']} | League: {mention['league']}")

    # Entity stats
    print("\n" + "-"*60)
    stats = qr.get_entity_stats("Chiefs")
    print(f"\nEntity Statistics: Chiefs")
    print(f"  Total mentions: {stats['total_mentions']}")
    print(f"  Documents: {stats['documents']}")
    print(f"  Leagues: {', '.join(stats['leagues'])}")


def demo_story_map(doc_id1, doc_id2):
    """Demo: Story Memory Map"""
    demo_header("5. Story Memory Map & Auto-Linking")

    smm = StoryMemoryMap()

    # Auto-link documents
    links1 = smm.auto_link_documents(doc_id1)
    print(f"Auto-linked document 1: {links1} links created")

    links2 = smm.auto_link_documents(doc_id2)
    print(f"Auto-linked document 2: {links2} links created")

    # Get story map
    if links1 > 0:
        story_map = smm.get_story_map(doc_id1, depth=2)
        print(f"\nStory Map for document 1:")
        print(f"  Total connected nodes: {len(story_map['nodes'])}")
        print(f"  Total connections: {len(story_map['edges'])}")

        print(f"\n  Connected stories:")
        for node in story_map['nodes'][:5]:
            indent = "    " * node['depth']
            print(f"{indent}• {node['title']} (depth: {node['depth']})")

    # Correlation matrix
    matrix = smm.get_story_correlation_matrix("Chiefs")
    print(f"\nTeam Correlation Matrix: Chiefs")
    print(f"  Total mentions: {matrix['total_mentions']}")
    print(f"  Teams appearing with Chiefs:")
    for team, count in list(matrix['co_occurrences'].items())[:3]:
        print(f"    • {team}: {count} times")


def demo_indexing():
    """Demo: Auto-Indexing"""
    demo_header("6. Auto-Indexing")

    indexer = AutoIndexer()

    # Weekly index
    weekly = indexer.build_weekly_index(League.NFL, weeks_back=2)
    print(f"Weekly Index - {weekly['league'].upper()}")
    print(f"Total documents: {weekly['total_documents']}\n")

    for week, docs in list(weekly['weeks'].items())[:2]:
        print(f"{week}: {len(docs)} documents")
        for doc in docs[:2]:
            print(f"  • {doc['title']}")
        print()

    # Sport index
    print("-"*60)
    sport_index = indexer.build_sport_index()
    print("\nIndex by Sport:")
    for sport, data in list(sport_index['sports'].items())[:3]:
        print(f"  {sport.upper()}: {data['total']} documents")


def demo_dashboard():
    """Demo: Editor Dashboard"""
    demo_header("7. Editor Dashboard")

    dashboard = EditorDashboard()

    # Create sample tasks
    task1 = dashboard.create_task(
        title="Review Chiefs-Bills recap",
        description="Check stats and quotes",
        assignee="Editor One",
        priority="high",
        deadline=datetime.now() + timedelta(days=1)
    )

    task2 = dashboard.create_task(
        title="Fact-check Mahomes feature",
        assignee="Editor Two",
        priority="medium",
        deadline=datetime.now() + timedelta(days=3)
    )

    print(f"✓ Created task: {task1.title}")
    print(f"✓ Created task: {task2.title}")

    # Get dashboard view
    view = dashboard.get_dashboard_view()

    print(f"\nDashboard Summary:")
    print(f"  Total pending tasks: {view['tasks']['total_pending']}")
    print(f"  By priority:")
    for priority, count in view['tasks']['by_priority'].items():
        if count > 0:
            print(f"    • {priority.title()}: {count}")

    print(f"\n  Documents:")
    print(f"    • Drafts: {view['documents']['drafts']}")
    print(f"    • In edit: {view['documents']['in_edit']}")
    print(f"    • Ready to publish: {view['documents']['ready_to_publish']}")

    # Team workload
    workload = dashboard.get_team_workload()
    if workload:
        print(f"\n  Team Workload:")
        for assignee, stats in workload.items():
            print(f"    • {assignee}: {stats['pending']} pending, {stats['total']} total")


def demo_export(doc_id):
    """Demo: Exporting"""
    demo_header("8. Document Export")

    from knowledge_manager import DocumentExporter

    exporter = DocumentExporter()

    # Export to markdown
    md_path = exporter.export_to_markdown(doc_id)
    print(f"✓ Exported to Markdown")
    print(f"  Path: {md_path}")

    # Export to PDF-ready markdown
    pdf_path = exporter.export_to_pdf_markdown(doc_id)
    print(f"\n✓ Exported to PDF-ready Markdown")
    print(f"  Path: {pdf_path}")
    print(f"  Convert to PDF: pandoc {pdf_path} -o output.pdf")

    # List exports
    exports = exporter.list_exports()
    print(f"\nTotal exports: {len(exports)}")
    for export in exports[:3]:
        print(f"  • {export['filename']} ({export['size_kb']} KB)")


def demo_archive():
    """Demo: Archive Management"""
    demo_header("9. Archive Management")

    from knowledge_manager import ArchiveManager

    archiver = ArchiveManager()

    # Dry run archive
    result = archiver.auto_archive(days_old=365, dry_run=True)

    print(f"Auto-Archive (Dry Run):")
    print(f"  Cutoff date: {result['cutoff_date']}")
    print(f"  Candidates for archiving: {result['candidates']}")
    print(f"  Would archive: {result['archived']}")

    # Archive stats
    stats = archiver.get_archive_stats()
    print(f"\nArchive Statistics:")
    print(f"  Total archived: {stats['total_archived']}")
    print(f"  Archive size: {stats['archive_size_mb']} MB")
    if stats['by_league']:
        print(f"  By league:")
        for league, count in stats['by_league'].items():
            print(f"    • {league}: {count}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     SPORTS KNOWLEDGE MANAGEMENT SYSTEM - DEMO                ║
║                                                              ║
║  This demo showcases the key features of the comprehensive   ║
║  sports content organization and retrieval system.           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    try:
        # Run demos
        doc_id1, doc_id2 = demo_document_creation()
        demo_auto_tagging()
        demo_search()
        demo_quick_recall(doc_id1, doc_id2)
        demo_story_map(doc_id1, doc_id2)
        demo_indexing()
        demo_dashboard()
        demo_export(doc_id1)
        demo_archive()

        # Summary
        demo_header("Demo Complete!")
        print("""
The Sports Knowledge Management System provides:

✓ Hierarchical folder organization
✓ Auto-tagging and metadata management
✓ Advanced search with stat-based queries
✓ Quick recall for players/teams
✓ Story memory maps and auto-linking
✓ Auto-indexing and table of contents
✓ Editor dashboard and task management
✓ Export to PDF, Markdown, JSON
✓ Archive management with auto-cleanup

See KNOWLEDGE_MANAGEMENT.md for full documentation.

Try the CLI:
  python knowledge_cli.py search "your query"
  python knowledge_cli.py recall "player name"
  python knowledge_cli.py dashboard

Happy organizing! 🏆
""")

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
