"""Experiment mode for safely testing new prompt variations and configurations."""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import hashlib


class ExperimentMode:
    """Manage experimental prompt variations and A/B testing."""

    def __init__(self, experiments_dir: str = 'experiments'):
        """
        Initialize experiment mode.

        Args:
            experiments_dir: Directory for experiment files
        """
        self.experiments_dir = experiments_dir
        os.makedirs(experiments_dir, exist_ok=True)
        self.active_experiment = None

    def create_experiment(
        self,
        name: str,
        description: str,
        prompt_variation: str,
        leagues: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create a new experiment.

        Args:
            name: Experiment name
            description: Experiment description
            prompt_variation: The prompt variation to test
            leagues: Leagues to test on
            metadata: Additional metadata

        Returns:
            Experiment ID
        """
        # Generate unique ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        exp_id = f"{name.lower().replace(' ', '_')}_{timestamp}"

        experiment = {
            'id': exp_id,
            'name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'status': 'draft',
            'prompt_variation': prompt_variation,
            'leagues': leagues or [],
            'metadata': metadata or {},
            'runs': [],
            'results': {}
        }

        # Save experiment
        exp_file = os.path.join(self.experiments_dir, f"{exp_id}.json")
        with open(exp_file, 'w') as f:
            json.dump(experiment, f, indent=2)

        return exp_id

    def load_experiment(self, exp_id: str) -> Optional[Dict]:
        """
        Load an experiment by ID.

        Args:
            exp_id: Experiment ID

        Returns:
            Experiment data or None
        """
        exp_file = os.path.join(self.experiments_dir, f"{exp_id}.json")
        if not os.path.exists(exp_file):
            print(f"Experiment {exp_id} not found")
            return None

        try:
            with open(exp_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error loading experiment: {e}")
            return None

    def save_experiment(self, experiment: Dict) -> bool:
        """
        Save experiment data.

        Args:
            experiment: Experiment data

        Returns:
            True if successful
        """
        try:
            exp_file = os.path.join(
                self.experiments_dir,
                f"{experiment['id']}.json"
            )
            with open(exp_file, 'w') as f:
                json.dump(experiment, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving experiment: {e}")
            return False

    def activate_experiment(self, exp_id: str) -> bool:
        """
        Activate an experiment for testing.

        Args:
            exp_id: Experiment ID

        Returns:
            True if successful
        """
        experiment = self.load_experiment(exp_id)
        if not experiment:
            return False

        experiment['status'] = 'active'
        experiment['activated_at'] = datetime.now().isoformat()

        self.active_experiment = experiment
        return self.save_experiment(experiment)

    def deactivate_experiment(self, exp_id: str) -> bool:
        """
        Deactivate an experiment.

        Args:
            exp_id: Experiment ID

        Returns:
            True if successful
        """
        experiment = self.load_experiment(exp_id)
        if not experiment:
            return False

        experiment['status'] = 'completed'
        experiment['completed_at'] = datetime.now().isoformat()

        if self.active_experiment and self.active_experiment['id'] == exp_id:
            self.active_experiment = None

        return self.save_experiment(experiment)

    def log_run(
        self,
        exp_id: str,
        run_data: Dict
    ) -> bool:
        """
        Log an experimental run.

        Args:
            exp_id: Experiment ID
            run_data: Data from the run

        Returns:
            True if successful
        """
        experiment = self.load_experiment(exp_id)
        if not experiment:
            return False

        run_entry = {
            'timestamp': datetime.now().isoformat(),
            'data': run_data,
            'run_hash': hashlib.md5(
                json.dumps(run_data, sort_keys=True).encode()
            ).hexdigest()
        }

        experiment['runs'].append(run_entry)
        return self.save_experiment(experiment)

    def compare_with_baseline(
        self,
        exp_id: str,
        baseline_id: str
    ) -> Dict:
        """
        Compare experiment results with baseline.

        Args:
            exp_id: Experiment ID
            baseline_id: Baseline experiment ID

        Returns:
            Comparison results
        """
        experiment = self.load_experiment(exp_id)
        baseline = self.load_experiment(baseline_id)

        if not experiment or not baseline:
            return {'error': 'Could not load experiments'}

        comparison = {
            'experiment': exp_id,
            'baseline': baseline_id,
            'experiment_runs': len(experiment.get('runs', [])),
            'baseline_runs': len(baseline.get('runs', [])),
            'differences': []
        }

        # Compare metrics (if available)
        exp_results = experiment.get('results', {})
        base_results = baseline.get('results', {})

        for metric in set(exp_results.keys()) | set(base_results.keys()):
            exp_val = exp_results.get(metric, 0)
            base_val = base_results.get(metric, 0)

            if base_val != 0:
                change = ((exp_val - base_val) / base_val) * 100
            else:
                change = 0

            comparison['differences'].append({
                'metric': metric,
                'experiment_value': exp_val,
                'baseline_value': base_val,
                'change_percent': round(change, 2)
            })

        return comparison

    def list_experiments(
        self,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        List all experiments.

        Args:
            status: Filter by status (draft, active, completed)

        Returns:
            List of experiment summaries
        """
        experiments = []

        for filename in os.listdir(self.experiments_dir):
            if not filename.endswith('.json'):
                continue

            exp_file = os.path.join(self.experiments_dir, filename)
            try:
                with open(exp_file, 'r') as f:
                    exp = json.load(f)

                    # Filter by status if specified
                    if status and exp.get('status') != status:
                        continue

                    experiments.append({
                        'id': exp['id'],
                        'name': exp['name'],
                        'status': exp['status'],
                        'created_at': exp['created_at'],
                        'runs': len(exp.get('runs', []))
                    })
            except:
                continue

        # Sort by creation date
        experiments.sort(key=lambda x: x['created_at'], reverse=True)
        return experiments

    def get_experiment_summary(self, exp_id: str) -> str:
        """
        Get formatted summary of experiment.

        Args:
            exp_id: Experiment ID

        Returns:
            Formatted summary string
        """
        experiment = self.load_experiment(exp_id)
        if not experiment:
            return f"Experiment {exp_id} not found"

        output = []
        output.append("\n" + "="*70)
        output.append(f"🔬 EXPERIMENT: {experiment['name']}")
        output.append("="*70)
        output.append(f"ID:          {experiment['id']}")
        output.append(f"Status:      {experiment['status'].upper()}")
        output.append(f"Created:     {experiment['created_at'][:19]}")
        output.append(f"\nDescription: {experiment['description']}")

        if experiment.get('leagues'):
            output.append(f"\nLeagues:     {', '.join(experiment['leagues'])}")

        output.append(f"\nRuns:        {len(experiment.get('runs', []))}")

        if experiment.get('results'):
            output.append("\nResults:")
            for key, value in experiment['results'].items():
                output.append(f"  • {key}: {value}")

        output.append("\nPrompt Variation:")
        output.append("─" * 70)
        output.append(experiment['prompt_variation'])
        output.append("─" * 70)

        return "\n".join(output)

    def delete_experiment(self, exp_id: str) -> bool:
        """
        Delete an experiment.

        Args:
            exp_id: Experiment ID

        Returns:
            True if successful
        """
        exp_file = os.path.join(self.experiments_dir, f"{exp_id}.json")
        if not os.path.exists(exp_file):
            print(f"Experiment {exp_id} not found")
            return False

        try:
            os.remove(exp_file)
            return True
        except Exception as e:
            print(f"Error deleting experiment: {e}")
            return False

    def clone_experiment(
        self,
        exp_id: str,
        new_name: str,
        modifications: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Clone an existing experiment with modifications.

        Args:
            exp_id: Experiment ID to clone
            new_name: Name for new experiment
            modifications: Optional modifications to apply

        Returns:
            New experiment ID or None
        """
        original = self.load_experiment(exp_id)
        if not original:
            return None

        # Create new experiment based on original
        new_exp_id = self.create_experiment(
            name=new_name,
            description=f"Cloned from {original['name']}",
            prompt_variation=original['prompt_variation'],
            leagues=original.get('leagues'),
            metadata=original.get('metadata', {})
        )

        # Apply modifications if provided
        if modifications:
            new_exp = self.load_experiment(new_exp_id)
            if new_exp:
                new_exp.update(modifications)
                self.save_experiment(new_exp)

        return new_exp_id
