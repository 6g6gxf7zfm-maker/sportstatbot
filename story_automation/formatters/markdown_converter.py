"""
Markdown Converter - Convert markdown to various formats preserving formatting
"""

import re
from typing import Dict, List, Any, Optional


class MarkdownConverter:
    """Convert markdown to Google Docs, HTML, and other formats"""

    def __init__(self):
        self.bold_pattern = re.compile(r'\*\*(.+?)\*\*|__(.+?)__')
        self.italic_pattern = re.compile(r'\*(.+?)\*|_(.+?)_')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def to_google_docs(self, markdown_text: str) -> Dict[str, Any]:
        """
        Convert markdown to Google Docs API format

        Args:
            markdown_text: Markdown text to convert

        Returns:
            Google Docs API request format
        """
        # Parse markdown into structured elements
        elements = self._parse_markdown(markdown_text)

        # Convert to Google Docs requests
        requests = []
        index = 1

        for element in elements:
            if element['type'] == 'heading':
                requests.extend(self._create_heading_requests(
                    element['text'],
                    element['level'],
                    index
                ))
                index += len(element['text']) + 1

            elif element['type'] == 'paragraph':
                requests.extend(self._create_paragraph_requests(
                    element['text'],
                    element.get('formatting', {}),
                    index
                ))
                index += len(element['text']) + 1

            elif element['type'] == 'bullet':
                requests.extend(self._create_bullet_requests(
                    element['text'],
                    index
                ))
                index += len(element['text']) + 1

        return {
            'requests': requests,
            'elements': elements
        }

    def to_html(self, markdown_text: str) -> str:
        """
        Convert markdown to HTML

        Args:
            markdown_text: Markdown text to convert

        Returns:
            HTML string
        """
        html = markdown_text

        # Convert headings
        html = re.sub(
            r'^######\s+(.+)$',
            r'<h6>\1</h6>',
            html,
            flags=re.MULTILINE
        )
        html = re.sub(
            r'^#####\s+(.+)$',
            r'<h5>\1</h5>',
            html,
            flags=re.MULTILINE
        )
        html = re.sub(
            r'^####\s+(.+)$',
            r'<h4>\1</h4>',
            html,
            flags=re.MULTILINE
        )
        html = re.sub(
            r'^###\s+(.+)$',
            r'<h3>\1</h3>',
            html,
            flags=re.MULTILINE
        )
        html = re.sub(
            r'^##\s+(.+)$',
            r'<h2>\1</h2>',
            html,
            flags=re.MULTILINE
        )
        html = re.sub(
            r'^#\s+(.+)$',
            r'<h1>\1</h1>',
            html,
            flags=re.MULTILINE
        )

        # Convert bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)

        # Convert italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

        # Convert links
        html = re.sub(
            r'\[([^\]]+)\]\(([^\)]+)\)',
            r'<a href="\2">\1</a>',
            html
        )

        # Convert bullets
        html = re.sub(r'^\* (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Wrap lists
        html = re.sub(
            r'(<li>.*?</li>(\n)?)+',
            lambda m: f'<ul>{m.group(0)}</ul>',
            html,
            flags=re.MULTILINE
        )

        # Convert paragraphs
        lines = html.split('\n\n')
        formatted_lines = []
        for line in lines:
            if not line.strip().startswith('<'):
                formatted_lines.append(f'<p>{line.strip()}</p>')
            else:
                formatted_lines.append(line)

        html = '\n'.join(formatted_lines)

        return html

    def to_plain_text(self, markdown_text: str) -> str:
        """
        Convert markdown to plain text (strip formatting)

        Args:
            markdown_text: Markdown text to convert

        Returns:
            Plain text string
        """
        text = markdown_text

        # Remove markdown formatting
        text = re.sub(r'\*\*|__|\*|_', '', text)  # Bold and italic
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)  # Headings
        text = re.sub(r'^[\*\-]\s+', '', text, flags=re.MULTILINE)  # Bullets

        return text

    def preserve_emoji(self, text: str) -> str:
        """
        Ensure emojis are preserved during conversion

        Args:
            text: Text containing emojis

        Returns:
            Text with emoji-safe encoding
        """
        # Emojis are typically preserved in most formats
        # This method can be extended for special handling
        return text

    def _parse_markdown(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Parse markdown into structured elements"""
        elements = []
        lines = markdown_text.split('\n')

        for line in lines:
            if not line.strip():
                continue

            # Check for heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                elements.append({
                    'type': 'heading',
                    'level': len(heading_match.group(1)),
                    'text': heading_match.group(2)
                })
                continue

            # Check for bullet
            bullet_match = re.match(r'^[\*\-]\s+(.+)$', line)
            if bullet_match:
                elements.append({
                    'type': 'bullet',
                    'text': bullet_match.group(1)
                })
                continue

            # Regular paragraph
            if line.strip():
                formatting = self._extract_formatting(line)
                elements.append({
                    'type': 'paragraph',
                    'text': line,
                    'formatting': formatting
                })

        return elements

    def _extract_formatting(self, text: str) -> Dict[str, List[tuple]]:
        """Extract formatting information from text"""
        formatting = {
            'bold': [],
            'italic': [],
            'links': []
        }

        # Find bold
        for match in self.bold_pattern.finditer(text):
            start = match.start()
            end = match.end()
            formatting['bold'].append((start, end))

        # Find italic
        for match in self.italic_pattern.finditer(text):
            start = match.start()
            end = match.end()
            formatting['italic'].append((start, end))

        # Find links
        for match in self.link_pattern.finditer(text):
            start = match.start()
            end = match.end()
            url = match.group(2)
            formatting['links'].append((start, end, url))

        return formatting

    def _create_heading_requests(
        self,
        text: str,
        level: int,
        index: int
    ) -> List[Dict]:
        """Create Google Docs requests for heading"""
        return [
            {
                'insertText': {
                    'location': {'index': index},
                    'text': f'{text}\n'
                }
            },
            {
                'updateParagraphStyle': {
                    'range': {
                        'startIndex': index,
                        'endIndex': index + len(text)
                    },
                    'paragraphStyle': {
                        'namedStyleType': f'HEADING_{level}'
                    },
                    'fields': 'namedStyleType'
                }
            }
        ]

    def _create_paragraph_requests(
        self,
        text: str,
        formatting: Dict,
        index: int
    ) -> List[Dict]:
        """Create Google Docs requests for paragraph"""
        requests = [
            {
                'insertText': {
                    'location': {'index': index},
                    'text': f'{text}\n'
                }
            }
        ]

        # Add formatting
        for bold_range in formatting.get('bold', []):
            requests.append({
                'updateTextStyle': {
                    'range': {
                        'startIndex': index + bold_range[0],
                        'endIndex': index + bold_range[1]
                    },
                    'textStyle': {'bold': True},
                    'fields': 'bold'
                }
            })

        return requests

    def _create_bullet_requests(
        self,
        text: str,
        index: int
    ) -> List[Dict]:
        """Create Google Docs requests for bullet point"""
        return [
            {
                'insertText': {
                    'location': {'index': index},
                    'text': f'{text}\n'
                }
            },
            {
                'createParagraphBullets': {
                    'range': {
                        'startIndex': index,
                        'endIndex': index + len(text)
                    },
                    'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
                }
            }
        ]
