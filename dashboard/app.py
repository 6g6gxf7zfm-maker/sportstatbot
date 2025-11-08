"""Web dashboard for SportStatBot automation control."""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime

from automation.workflow_engine import WorkflowEngine
from automation.task_queue import TaskQueue
from automation.rate_limiter import RateLimiter
from automation.freshness_monitor import FreshnessMonitor
from automation.workflow_definitions import WorkflowDefinitions
from exporters.version_manager import VersionManager
from exporters.cleanup_manager import CleanupManager
from integrations.email_notifier import EmailNotifier
import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for API access

# Initialize automation components
workflow_engine = WorkflowEngine()
task_queue = TaskQueue(max_workers=5)
rate_limiter = RateLimiter()
freshness_monitor = FreshnessMonitor()
version_manager = VersionManager()
cleanup_manager = CleanupManager()

# Start services
task_queue.start()
freshness_monitor.start_monitoring()


@app.route('/')
def index():
    """Dashboard home page."""
    return render_template('dashboard.html')


@app.route('/api/status')
def api_status():
    """Get overall system status."""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'task_queue': 'running' if task_queue.running else 'stopped',
            'freshness_monitor': 'running' if freshness_monitor.running else 'stopped',
            'workflow_engine': 'initialized'
        }
    })


@app.route('/api/sports')
def api_sports():
    """Get list of sports with configuration."""
    sports_info = []
    for sport_key, sport_config in config.SPORTS_CONFIG.items():
        sports_info.append({
            'key': sport_key,
            'name': sport_config['display_name'],
            'emoji': sport_config['emoji'],
            'active': sport_config['season_active']
        })
    return jsonify(sports_info)


@app.route('/api/queue/status')
def api_queue_status():
    """Get task queue status."""
    stats = task_queue.get_statistics()
    return jsonify(stats)


@app.route('/api/queue/tasks')
def api_queue_tasks():
    """Get queued, running, and completed tasks."""
    return jsonify({
        'queued': task_queue.get_queued_tasks(),
        'running': task_queue.get_running_tasks(),
        'completed': task_queue.get_completed_tasks(limit=20)
    })


@app.route('/api/workflows')
def api_workflows():
    """Get list of registered workflows."""
    workflows = workflow_engine.list_workflows()
    return jsonify(workflows)


@app.route('/api/workflow/run', methods=['POST'])
def api_run_workflow():
    """Run a workflow."""
    data = request.json
    sport = data.get('sport')
    workflow_type = data.get('type', 'full_digest')

    if not sport:
        return jsonify({'error': 'Sport required'}), 400

    try:
        # Create workflow
        if workflow_type == 'full_digest':
            workflow = WorkflowDefinitions.create_full_digest_workflow(sport)
        elif workflow_type == 'quick_update':
            workflow = WorkflowDefinitions.create_quick_update_workflow(sport)
        else:
            return jsonify({'error': 'Invalid workflow type'}), 400

        # Register and execute
        workflow_engine.register_workflow(workflow)
        result = workflow_engine.execute_workflow(workflow.name)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error running workflow: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow/<workflow_name>/pause', methods=['POST'])
def api_pause_workflow(workflow_name):
    """Pause a workflow."""
    try:
        workflow_engine.pause_workflow(workflow_name)
        return jsonify({'status': 'paused', 'workflow': workflow_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow/<workflow_name>/resume', methods=['POST'])
def api_resume_workflow(workflow_name):
    """Resume a paused workflow."""
    try:
        result = workflow_engine.resume_workflow(workflow_name)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/workflow/<workflow_name>/cancel', methods=['POST'])
def api_cancel_workflow(workflow_name):
    """Cancel a workflow."""
    try:
        workflow_engine.cancel_workflow(workflow_name)
        return jsonify({'status': 'cancelled', 'workflow': workflow_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/freshness')
def api_freshness():
    """Get data freshness report."""
    report = freshness_monitor.get_freshness_report()
    return jsonify(report)


@app.route('/api/freshness/<sport>/refresh', methods=['POST'])
def api_force_refresh(sport):
    """Force refresh data for a sport."""
    try:
        success = freshness_monitor.force_refresh(sport)
        return jsonify({'success': success, 'sport': sport})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rate-limits')
def api_rate_limits():
    """Get rate limit status for all APIs."""
    status = rate_limiter.get_all_quota_status()
    return jsonify(status)


@app.route('/api/rate-limits/<api_name>')
def api_rate_limit_detail(api_name):
    """Get detailed rate limit status for an API."""
    status = rate_limiter.get_quota_status(api_name)
    return jsonify(status)


@app.route('/api/versions')
def api_versions():
    """Get version history."""
    sport = request.args.get('sport')
    limit = int(request.args.get('limit', 50))
    history = version_manager.get_version_history(sport, limit)
    return jsonify(history)


@app.route('/api/versions/latest')
def api_latest_versions():
    """Get latest versions."""
    limit = int(request.args.get('limit', 10))
    versions = version_manager.get_latest_versions(limit)
    return jsonify(versions)


@app.route('/api/cleanup/status')
def api_cleanup_status():
    """Get cleanup manager status."""
    stats = cleanup_manager.get_cleanup_statistics()
    return jsonify(stats)


@app.route('/api/cleanup/archives')
def api_cleanup_archives():
    """List archived files."""
    sport = request.args.get('sport')
    archives = cleanup_manager.list_archived_files(sport)
    return jsonify(archives)


@app.route('/api/cleanup/run', methods=['POST'])
def api_run_cleanup():
    """Run cleanup for a sport."""
    data = request.json
    sport = data.get('sport')
    dry_run = data.get('dry_run', True)

    if not sport:
        return jsonify({'error': 'Sport required'}), 400

    try:
        from pathlib import Path
        reports_dir = Path('reports') / sport.upper()
        stats = cleanup_manager.cleanup_directory(reports_dir, sport, dry_run)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/schedule', methods=['GET'])
def api_get_schedule():
    """Get schedule configuration."""
    # TODO: Implement schedule storage/retrieval
    return jsonify({
        'sports': {
            sport: {
                'enabled': True,
                'frequency': 'daily',
                'times': ['08:00', '18:00']
            }
            for sport in config.SPORTS_CONFIG.keys()
        }
    })


@app.route('/api/schedule', methods=['POST'])
def api_update_schedule():
    """Update schedule configuration."""
    data = request.json
    # TODO: Implement schedule update logic
    return jsonify({'status': 'updated', 'schedule': data})


@app.route('/api/digest/run', methods=['POST'])
def api_run_digest():
    """Run digest generation for a sport."""
    data = request.json
    sport = data.get('sport')
    digest_type = data.get('type', 'full')

    if not sport:
        return jsonify({'error': 'Sport required'}), 400

    try:
        # Add to task queue
        task_id = f"digest_{sport}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        def run_digest_task():
            """Task to run digest generation."""
            from report_generator import SportsReportGenerator
            generator = SportsReportGenerator()
            report = generator.generate_sport_report(sport, quick=(digest_type == 'quick'))
            return report

        task = task_queue.add_task(
            task_id=task_id,
            name=f"{sport.upper()} Digest",
            action=run_digest_task,
            sport=sport,
            metadata={'type': digest_type}
        )

        return jsonify({
            'status': 'queued',
            'task_id': task_id,
            'task': task.to_dict()
        })

    except Exception as e:
        logger.error(f"Error queuing digest: {e}")
        return jsonify({'error': str(e)}), 500


def shutdown_services():
    """Shutdown all services gracefully."""
    logger.info("Shutting down services...")
    task_queue.stop()
    freshness_monitor.stop_monitoring()
    logger.info("Services stopped")


if __name__ == '__main__':
    import atexit
    atexit.register(shutdown_services)

    # Get settings from environment
    port = int(os.getenv('DASHBOARD_PORT', 5000))
    host = os.getenv('DASHBOARD_HOST', '0.0.0.0')
    debug = os.getenv('DASHBOARD_DEBUG', 'false').lower() == 'true'

    logger.info(f"Starting dashboard on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
