#!/usr/bin/env python3
"""
Backend API server for SportStatBot Cursor Dashboard
Provides REST endpoints for the frontend to interact with SportStatBot
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path to import SportStatBot modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sports_report_generator import SportsReportGenerator
from src.sports_data_fetcher import SportsDataFetcher
from src.sports_data_analyzer import SportsDataAnalyzer
from src.report_formatter import ReportFormatter

app = Flask(__name__)
CORS(app)

# Global instances
generator = None
agent_logs = []


def add_agent_log(agent: str, action: str, details: str, data: Any = None):
    """Add an entry to the agent activity log"""
    agent_logs.append({
        'id': f'log-{len(agent_logs) + 1}',
        'agent': agent,
        'action': action,
        'details': details,
        'timestamp': datetime.now().isoformat(),
        'data': data
    })
    # Keep only last 100 logs
    if len(agent_logs) > 100:
        agent_logs.pop(0)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/sports/data', methods=['GET'])
def get_sports_data():
    """Fetch sports data for a specific league"""
    sport = request.args.get('sport', 'NFL').upper()

    try:
        add_agent_log('fetcher', 'Fetching data', f'Retrieving {sport} data from APIs')

        # Initialize generator with the requested sport
        config = {
            'sports': [sport],
            'espn_api_key': os.getenv('ESPN_API_KEY', ''),
            'odds_api_key': os.getenv('ODDS_API_KEY', '')
        }

        generator = SportsReportGenerator(config)
        sport_data = generator._generate_sport_data(sport)

        add_agent_log('analyzer', 'Data analysis complete', f'Analyzed {len(sport_data.get("games", []))} games')

        return jsonify({
            'success': True,
            'sport': sport,
            'data': sport_data,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        add_agent_log('fetcher', 'Error fetching data', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stories/generate', methods=['POST'])
def generate_story():
    """Generate a story based on template and sport"""
    data = request.json
    template = data.get('template', 'digest')
    sport = data.get('sport', 'NFL')

    try:
        add_agent_log('writer', 'Generating story', f'Creating {template} for {sport}')

        config = {
            'sports': [sport],
            'output_format': 'text'
        }

        generator = SportsReportGenerator(config)
        report = generator.generate_report()

        add_agent_log('formatter', 'Story formatted', f'Generated {len(report)} character story')

        return jsonify({
            'success': True,
            'content': report,
            'template': template,
            'sport': sport,
            'wordCount': len(report.split()),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        add_agent_log('writer', 'Error generating story', str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stories/expand', methods=['POST'])
def expand_paragraph():
    """Expand a paragraph using AI"""
    data = request.json
    paragraph = data.get('paragraph', '')
    context = data.get('context', {})

    try:
        add_agent_log('writer', 'Expanding paragraph', f'Expanding {len(paragraph)} character paragraph')

        # This would integrate with an AI service to expand the paragraph
        # For now, return a mock expansion
        expanded = f"{paragraph}\n\nThis section has been expanded with additional context and detail, providing more depth and analysis based on the available sports data."

        return jsonify({
            'success': True,
            'original': paragraph,
            'expanded': expanded,
            'wordCount': len(expanded.split()),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/writing/feedback', methods=['POST'])
def get_writing_feedback():
    """Analyze content and provide writing feedback"""
    data = request.json
    content = data.get('content', '')

    feedback = []

    # Sentence length analysis
    sentences = content.split('.')
    for i, sentence in enumerate(sentences):
        word_count = len(sentence.split())
        if word_count > 35:
            feedback.append({
                'id': f'feedback-{i}',
                'type': 'sentence_length',
                'message': f'Sentence is too long ({word_count} words). Consider breaking it up.',
                'severity': 'warning',
                'position': {'start': 0, 'end': len(sentence)},
                'suggestion': 'Break into 2-3 shorter sentences for better readability.'
            })

    # Check for data references without context
    if 'points' in content.lower() or 'rebounds' in content.lower():
        if 'per game' not in content.lower() and 'average' not in content.lower():
            feedback.append({
                'id': 'feedback-data-window',
                'type': 'missing_data',
                'message': 'Missing data window for this statistic',
                'severity': 'error',
                'position': {'start': 0, 'end': 50},
                'suggestion': 'Add time context (e.g., "per game", "this season", "last 3 games")'
            })

    return jsonify({
        'success': True,
        'feedback': feedback,
        'totalIssues': len(feedback),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/writing/proofread', methods=['POST'])
def proofread_content():
    """Real-time proofreading for grammar and style"""
    data = request.json
    content = data.get('content', '')

    # This would integrate with a grammar checking service
    # For now, return mock suggestions
    suggestions = []

    return jsonify({
        'success': True,
        'suggestions': suggestions,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/ai/coauthor/suggest', methods=['POST'])
def get_ai_suggestions():
    """Get AI co-author paragraph suggestions"""
    data = request.json
    current_content = data.get('content', '')
    sport = data.get('sport', 'NFL')

    try:
        add_agent_log('writer', 'Generating suggestions', 'Creating AI co-author suggestions')

        # This would integrate with an AI service
        # For now, return mock suggestions
        suggestions = [
            {
                'id': f'suggestion-{datetime.now().timestamp()}',
                'paragraph': "The team's recent performance has been impressive, with key players stepping up in crucial moments.",
                'reasoning': 'Building on current analysis with performance context',
                'dataPoints': ['Team stats', 'Player performance'],
                'confidence': 0.87
            }
        ]

        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export/google-docs', methods=['POST'])
def export_to_google_docs():
    """Export story to Google Docs"""
    data = request.json
    content = data.get('content', '')
    title = data.get('title', 'Untitled Story')

    try:
        add_agent_log('formatter', 'Exporting to Google Docs', f'Exporting "{title}"')

        # This would integrate with Google Docs API
        # For now, return success

        return jsonify({
            'success': True,
            'message': 'Story exported to Google Docs',
            'docUrl': 'https://docs.google.com/document/d/mock-url',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/export/markdown', methods=['POST'])
def export_to_markdown():
    """Export story as markdown file"""
    data = request.json
    content = data.get('content', '')
    title = data.get('title', 'Untitled Story')

    try:
        # Generate markdown file
        markdown_content = f"# {title}\n\n{content}"

        return jsonify({
            'success': True,
            'content': markdown_content,
            'filename': f"{title.replace(' ', '_').lower()}.md",
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/logs', methods=['GET'])
def get_agent_logs():
    """Get agent activity logs"""
    limit = request.args.get('limit', 50, type=int)
    agent_filter = request.args.get('agent', None)

    filtered_logs = agent_logs
    if agent_filter:
        filtered_logs = [log for log in agent_logs if log['agent'] == agent_filter]

    return jsonify({
        'success': True,
        'logs': filtered_logs[-limit:],
        'total': len(filtered_logs),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/fact-check', methods=['POST'])
def fact_check():
    """Verify a fact against data sources"""
    data = request.json
    text = data.get('text', '')

    try:
        # This would verify the fact against ESPN/other APIs
        # For now, return mock verification

        return jsonify({
            'success': True,
            'verified': True,
            'source': 'ESPN API',
            'sourceUrl': 'https://espn.com/stats',
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting SportStatBot API Server...")
    print("Dashboard will be available at http://localhost:3000")
    print("API running at http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)
