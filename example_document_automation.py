#!/usr/bin/env python3
"""
Example usage of Document Automation for SportStatBot.

This script demonstrates how to use the Google Docs and Apple Notes
automation features to publish and manage sports content.
"""

from document_managers import DocumentOrchestrator
from report_generator import SportsReportGenerator
import config


def main():
    """Main example workflow."""

    print("=" * 60)
    print("SportStatBot - Document Automation Example")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = DocumentOrchestrator()

    # Step 1: Setup folder structures
    print("\n📁 Setting up folder structures...")
    setup_status = orchestrator.setup_all()

    for platform, status in setup_status.items():
        if isinstance(status, bool):
            emoji = "✓" if status else "✗"
            print(f"  {emoji} {platform}: {'Success' if status else 'Failed'}")
            if not status and f"{platform}_error" in setup_status:
                print(f"    Error: {setup_status[f'{platform}_error']}")

    # Step 2: Generate a sports report
    print("\n📊 Generating sports report...")
    report_gen = SportsReportGenerator()
    nfl_data = report_gen._generate_sport_data('nfl')

    if nfl_data:
        print("  ✓ NFL data generated")

        # Step 3: Publish to both platforms
        print("\n📝 Publishing to Google Docs and Apple Notes...")

        results = orchestrator.publish_sports_report(
            report_data=nfl_data,
            league='NFL',
            report_type='Digests'
        )

        # Display results
        if 'google_docs_url' in results:
            print(f"  ✓ Google Doc: {results['google_docs_url']}")

        if 'apple_notes_id' in results:
            print(f"  ✓ Apple Note: {results['apple_notes_id']}")

    else:
        print("  ✗ No NFL data available")

    # Step 4: Demonstrate custom content publishing
    print("\n📄 Publishing custom content...")

    custom_content = """
# Game Analysis: Chiefs vs. Bills

## Overview
This week's matchup between Kansas City and Buffalo promises to be one of the
most exciting games of the season. Both teams are coming off strong performances.

## Key Players to Watch
- Patrick Mahomes (KC QB)
- Josh Allen (BUF QB)
- Travis Kelce (KC TE)

## Betting Lines
- Spread: KC -2.5
- Over/Under: 52.5
- Moneyline: KC -140, BUF +120

## Prediction
Expect a high-scoring affair with both quarterbacks putting up big numbers.
    """

    custom_results = orchestrator.publish_content(
        title="Chiefs vs Bills - Game Preview",
        content=custom_content,
        league='NFL',
        category='Previews',
        metadata={
            'author': 'SportStatBot',
            'tags': ['#nfl', '#preview', '#chiefs', '#bills']
        }
    )

    if 'google_docs_url' in custom_results:
        print(f"  ✓ Preview published to Google Docs: {custom_results['google_docs_url']}")

    # Step 5: Create weekly summary
    print("\n📅 Creating weekly summary...")
    summary_results = orchestrator.create_weekly_summary()

    if 'apple_notes_summary' in summary_results:
        print(f"  ✓ Weekly summary created: {summary_results['apple_notes_summary']}")

    # Step 6: Get platform statistics
    print("\n📈 Platform Statistics:")
    stats = orchestrator.get_platform_stats()

    print(f"\nGoogle Docs:")
    print(f"  Folders: {stats.get('google_docs', {}).get('folders', 0)}")
    print(f"  Authenticated: {stats.get('google_docs', {}).get('authenticated', False)}")

    print(f"\nApple Notes:")
    notes_stats = stats.get('apple_notes', {})
    print(f"  Platform: {notes_stats.get('platform', 'Unknown')}")
    print(f"  Total Notes: {notes_stats.get('total_notes', 0)}")

    # Step 7: Demonstrate archival
    print("\n🗄️  Archiving old content (older than 30 days)...")
    archive_results = orchestrator.archive_old_content(days_old=30)

    for platform, count in archive_results.items():
        if isinstance(count, int):
            print(f"  Archived {count} items from {platform}")

    # Step 8: Export to PDF
    print("\n📑 Exporting documents to PDF...")
    export_results = orchestrator.export_batch_pdf(
        platform='both',
        output_dir='./exports'
    )

    if 'google_docs_files' in export_results:
        print(f"  ✓ Exported {len(export_results['google_docs_files'])} Google Docs")

    if 'apple_notes_files' in export_results:
        print(f"  ✓ Exported {len(export_results['apple_notes_files'])} Apple Notes")

    print("\n" + "=" * 60)
    print("✓ Document automation demonstration complete!")
    print("=" * 60)


def example_individual_managers():
    """Example using individual managers instead of orchestrator."""

    print("\n" + "=" * 60)
    print("Example: Using Individual Managers")
    print("=" * 60)

    # Using Google Docs Manager directly
    from document_managers import GoogleDocsManager

    google_docs = GoogleDocsManager()

    if google_docs.authenticate():
        print("✓ Authenticated with Google")

        # Setup folders
        google_docs.setup_league_folders()

        # Create a document
        doc_id = google_docs.create_document(
            title="NBA Injury Report",
            content="Latest injuries and their impact on upcoming games...",
            league="NBA",
            category="Injuries",
            metadata={'author': 'SportStatBot'}
        )

        print(f"✓ Created document: {doc_id}")

        # Lock the document
        google_docs.lock_document(doc_id)
        print(f"✓ Locked document from edits")

    # Using Apple Notes Manager directly
    from document_managers import AppleNotesManager

    apple_notes = AppleNotesManager()

    # Create folder structure
    apple_notes.create_folder_structure()

    # Create a note
    note_id = apple_notes.create_note(
        league='MLB',
        category='Digests',
        title='MLB Daily Digest',
        content='Latest scores, standings, and highlights from MLB...',
        tags=['#mlb', '#daily'],
        color='published'
    )

    print(f"✓ Created Apple Note: {note_id}")


if __name__ == '__main__':
    # Run main workflow
    main()

    # Optionally run individual manager examples
    # example_individual_managers()
