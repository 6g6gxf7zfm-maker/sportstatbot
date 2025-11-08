"""
Document Exporter - Export documents to various formats (PDF, Markdown, etc.)
"""

from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import json

from .database_handler import DatabaseHandler


class DocumentExporter:
    """Export documents to various formats"""

    def __init__(
        self,
        db_path: str = "knowledge_manager/database/sports_knowledge.db",
        export_path: str = "knowledge_manager/exports"
    ):
        self.db = DatabaseHandler(db_path)
        self.export_path = Path(export_path)
        self.export_path.mkdir(parents=True, exist_ok=True)

    def export_to_markdown(
        self,
        doc_id: str,
        include_metadata: bool = True,
        include_links: bool = True
    ) -> str:
        """Export document to clean markdown"""
        doc = self.db.get_document(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        markdown = ""

        # Add metadata header if requested
        if include_metadata:
            metadata = doc['metadata']
            markdown += "---\n"
            markdown += f"title: {doc['title']}\n"
            markdown += f"league: {metadata['league']}\n"
            markdown += f"date: {metadata['date']}\n"
            markdown += f"authors: {', '.join(metadata['authors'])}\n"
            markdown += f"tags: {', '.join(f'#{tag}' for tag in metadata['tags'])}\n"
            markdown += f"type: {metadata['document_type']}\n"
            markdown += f"version: {metadata['version']}\n"
            markdown += "---\n\n"

        # Add title
        markdown += f"# {doc['title']}\n\n"

        # Add content
        markdown += doc['content']

        # Add related stories if requested
        if include_links:
            linked_docs = self.db.get_linked_documents(doc_id)
            if linked_docs:
                markdown += "\n\n---\n\n## Related Stories\n\n"
                for linked_doc in linked_docs[:5]:
                    markdown += f"- [{linked_doc['title']}](doc:{linked_doc['doc_id']})\n"

        return markdown

    def export_batch_to_markdown(
        self,
        doc_ids: List[str],
        output_file: str = "export.md"
    ) -> str:
        """Export multiple documents to a single markdown file"""
        output_path = self.export_path / output_file

        content = f"# Sports Content Export\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"**Documents:** {len(doc_ids)}\n\n"
        content += "---\n\n"

        for i, doc_id in enumerate(doc_ids, 1):
            try:
                doc_content = self.export_to_markdown(doc_id, include_links=False)
                content += f"\n\n## Document {i}\n\n"
                content += doc_content
                content += "\n\n---\n"
            except ValueError:
                content += f"\n\n*Document {doc_id} not found*\n\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    def export_to_pdf_markdown(
        self,
        doc_id: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Export document to PDF-ready markdown
        (Can be converted to PDF using pandoc or similar tools)
        """
        doc = self.db.get_document(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        if not output_file:
            output_file = f"{doc_id}.md"

        output_path = self.export_path / output_file

        # Create PDF-friendly markdown with title page
        markdown = f"""---
title: "{doc['title']}"
author: {', '.join(doc['metadata']['authors'])}
date: {datetime.fromisoformat(doc['metadata']['date']).strftime('%B %d, %Y')}
---

# {doc['title']}

**League:** {doc['metadata']['league'].upper()}
**Date:** {datetime.fromisoformat(doc['metadata']['date']).strftime('%B %d, %Y')}
**Authors:** {', '.join(doc['metadata']['authors'])}
**Type:** {doc['metadata']['document_type'].replace('_', ' ').title()}

---

{doc['content']}

---

*Document ID: {doc['doc_id']}*
*Version: {doc['metadata']['version']}*
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        return str(output_path)

    def export_weekly_briefing(
        self,
        league: str,
        week_start: datetime,
        week_end: datetime
    ) -> str:
        """Export a weekly briefing PDF"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM documents
                WHERE json_extract(metadata, '$.league') = ?
                AND json_extract(metadata, '$.date') BETWEEN ? AND ?
                ORDER BY json_extract(metadata, '$.date') DESC
            """, (league, week_start.isoformat(), week_end.isoformat()))

            docs = [self.db._row_to_dict(row) for row in cursor.fetchall()]

        # Create briefing
        filename = f"{league}_briefing_{week_start.strftime('%Y-%m-%d')}.md"
        output_path = self.export_path / filename

        briefing = f"""---
title: "{league.upper()} Weekly Briefing"
date: {week_start.strftime('%B %d, %Y')} - {week_end.strftime('%B %d, %Y')}
---

# {league.upper()} Weekly Briefing

**Week of {week_start.strftime('%B %d, %Y')} - {week_end.strftime('%B %d, %Y')}**

**Total Stories:** {len(docs)}

---

## Table of Contents

"""

        # Add TOC
        for i, doc in enumerate(docs, 1):
            briefing += f"{i}. {doc['title']}\n"

        briefing += "\n---\n\n"

        # Add full documents
        for doc in docs:
            date_str = datetime.fromisoformat(doc['metadata']['date']).strftime('%B %d, %Y')
            briefing += f"## {doc['title']}\n\n"
            briefing += f"**Date:** {date_str} | **Type:** {doc['metadata']['document_type'].replace('_', ' ').title()}\n\n"
            briefing += doc['content']
            briefing += "\n\n---\n\n"

        # Add footer
        briefing += f"\n\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(briefing)

        return str(output_path)

    def export_to_json(self, doc_id: str, output_file: Optional[str] = None) -> str:
        """Export document to JSON format"""
        doc = self.db.get_document(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")

        if not output_file:
            output_file = f"{doc_id}.json"

        output_path = self.export_path / output_file

        # Add export metadata
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'document': doc
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        return str(output_path)

    def export_search_results(
        self,
        results: List[Dict],
        output_file: str = "search_results.md"
    ) -> str:
        """Export search results to markdown"""
        output_path = self.export_path / output_file

        content = f"# Search Results\n\n"
        content += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        content += f"**Total Results:** {len(results)}\n\n"
        content += "---\n\n"

        for i, doc in enumerate(results, 1):
            content += f"## {i}. {doc['title']}\n\n"
            content += f"**League:** {doc['metadata']['league'].upper()}  \n"
            content += f"**Date:** {doc['metadata']['date']}  \n"
            content += f"**Type:** {doc['metadata']['document_type']}  \n"
            content += f"**ID:** `{doc['doc_id']}`\n\n"

            # Add snippet of content
            snippet = doc['content'][:300]
            if len(doc['content']) > 300:
                snippet += "..."
            content += f"{snippet}\n\n"
            content += "---\n\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(output_path)

    def export_player_report(
        self,
        player_name: str,
        mentions: List[Dict]
    ) -> str:
        """Export a player report with all mentions"""
        filename = f"player_report_{player_name.replace(' ', '_')}.md"
        output_path = self.export_path / filename

        report = f"# Player Report: {player_name}\n\n"
        report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        report += f"**Total Mentions:** {len(mentions)}\n\n"
        report += "---\n\n"

        # Group by league
        by_league = {}
        for mention in mentions:
            doc = self.db.get_document(mention['doc_id'])
            if doc:
                league = doc['metadata']['league']
                if league not in by_league:
                    by_league[league] = []
                by_league[league].append(doc)

        for league, docs in by_league.items():
            report += f"## {league.upper()} ({len(docs)} mentions)\n\n"

            for doc in sorted(docs, key=lambda d: d['metadata']['date'], reverse=True):
                date = datetime.fromisoformat(doc['metadata']['date']).strftime('%B %d, %Y')
                report += f"### {doc['title']}\n\n"
                report += f"**Date:** {date}  \n"
                report += f"**Type:** {doc['metadata']['document_type']}  \n\n"

                # Find mention context in content
                lines = doc['content'].split('\n')
                for line in lines:
                    if player_name.lower() in line.lower():
                        report += f"> {line}\n\n"
                        break

                report += "---\n\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return str(output_path)

    def list_exports(self) -> List[Dict]:
        """List all exported files"""
        exports = []
        for file_path in self.export_path.glob('*'):
            if file_path.is_file():
                exports.append({
                    'filename': file_path.name,
                    'size_kb': round(file_path.stat().st_size / 1024, 2),
                    'created': datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat(),
                    'path': str(file_path)
                })

        return sorted(exports, key=lambda x: x['created'], reverse=True)
