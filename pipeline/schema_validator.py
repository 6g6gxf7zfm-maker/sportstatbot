"""Schema validation and data quality checks for sports data."""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pathlib import Path


class SchemaValidator:
    """
    Validates data schemas and performs quality checks on ingested data.
    Ensures data integrity and catches issues early.
    """

    def __init__(self, schema_dir: str = "config/schemas"):
        """
        Initialize schema validator.

        Args:
            schema_dir: Directory containing schema definitions
        """
        self.schema_dir = Path(schema_dir)
        self.schema_dir.mkdir(parents=True, exist_ok=True)

        # Define expected schemas
        self.schemas = self._load_schemas()

    def _load_schemas(self) -> Dict:
        """Load or define data schemas."""
        return {
            'scoreboard': {
                'required_fields': ['events', 'leagues'],
                'event_fields': ['id', 'name', 'date', 'competitions'],
                'competition_fields': ['competitors', 'status']
            },
            'standings': {
                'required_fields': ['children'],
                'standing_fields': ['team', 'stats']
            },
            'odds': {
                'required_fields': ['sport_key', 'commence_time', 'home_team', 'away_team'],
                'optional_fields': ['bookmakers']
            },
            'team': {
                'required_fields': ['id', 'displayName'],
                'optional_fields': ['abbreviation', 'logo', 'record']
            },
            'player': {
                'required_fields': ['id', 'displayName'],
                'optional_fields': ['position', 'jersey', 'team']
            }
        }

    def validate(self, data: Any, schema_type: str) -> Dict:
        """
        Validate data against schema.

        Args:
            data: Data to validate
            schema_type: Type of schema to validate against

        Returns:
            Validation result with errors and warnings
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'timestamp': datetime.now().isoformat()
        }

        if schema_type not in self.schemas:
            result['warnings'].append(f"No schema defined for type: {schema_type}")
            return result

        schema = self.schemas[schema_type]

        # Check if data is None or empty
        if data is None:
            result['valid'] = False
            result['errors'].append("Data is None")
            return result

        # Type checking
        if not isinstance(data, dict):
            result['valid'] = False
            result['errors'].append(f"Expected dict, got {type(data).__name__}")
            return result

        # Check required fields
        if 'required_fields' in schema:
            for field in schema['required_fields']:
                if field not in data:
                    result['valid'] = False
                    result['errors'].append(f"Missing required field: {field}")
                elif data[field] is None:
                    result['warnings'].append(f"Required field '{field}' is None")

        # Additional validation based on schema type
        if schema_type == 'scoreboard':
            result = self._validate_scoreboard(data, result)
        elif schema_type == 'standings':
            result = self._validate_standings(data, result)
        elif schema_type == 'odds':
            result = self._validate_odds(data, result)

        return result

    def _validate_scoreboard(self, data: Dict, result: Dict) -> Dict:
        """Validate scoreboard-specific data."""
        if 'events' in data:
            if not isinstance(data['events'], list):
                result['valid'] = False
                result['errors'].append("'events' must be a list")
            else:
                # Validate each event
                for idx, event in enumerate(data['events']):
                    if not isinstance(event, dict):
                        result['errors'].append(f"Event {idx} is not a dict")
                        continue

                    # Check event fields
                    event_schema = self.schemas['scoreboard']['event_fields']
                    for field in event_schema:
                        if field not in event:
                            result['warnings'].append(
                                f"Event {idx} missing field: {field}"
                            )

        return result

    def _validate_standings(self, data: Dict, result: Dict) -> Dict:
        """Validate standings-specific data."""
        if 'children' in data:
            if not isinstance(data['children'], list):
                result['valid'] = False
                result['errors'].append("'children' must be a list")
            else:
                if len(data['children']) == 0:
                    result['warnings'].append("Standings data is empty")

        return result

    def _validate_odds(self, data: Dict, result: Dict) -> Dict:
        """Validate odds-specific data."""
        # Validate time format
        if 'commence_time' in data:
            try:
                # Try parsing ISO format
                datetime.fromisoformat(data['commence_time'].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                result['warnings'].append("Invalid commence_time format")

        # Validate team names
        if 'home_team' in data and not data['home_team']:
            result['warnings'].append("home_team is empty")

        if 'away_team' in data and not data['away_team']:
            result['warnings'].append("away_team is empty")

        return result

    def validate_batch(self, data_items: List[Dict], schema_type: str) -> Dict:
        """
        Validate multiple data items.

        Args:
            data_items: List of data items to validate
            schema_type: Schema type to validate against

        Returns:
            Batch validation result
        """
        batch_result = {
            'total_items': len(data_items),
            'valid_items': 0,
            'invalid_items': 0,
            'items_with_warnings': 0,
            'results': [],
            'timestamp': datetime.now().isoformat()
        }

        for idx, item in enumerate(data_items):
            item_result = self.validate(item, schema_type)
            item_result['index'] = idx

            if item_result['valid']:
                batch_result['valid_items'] += 1
            else:
                batch_result['invalid_items'] += 1

            if item_result['warnings']:
                batch_result['items_with_warnings'] += 1

            batch_result['results'].append(item_result)

        return batch_result

    def check_data_quality(self, data: Dict, schema_type: str) -> Dict:
        """
        Perform data quality checks beyond schema validation.

        Args:
            data: Data to check
            schema_type: Type of data

        Returns:
            Quality check result
        """
        quality_result = {
            'completeness_score': 0.0,
            'freshness_score': 0.0,
            'consistency_score': 0.0,
            'overall_score': 0.0,
            'issues': []
        }

        # Completeness check
        if isinstance(data, dict):
            total_fields = len(self.schemas.get(schema_type, {}).get('required_fields', []))
            total_fields += len(self.schemas.get(schema_type, {}).get('optional_fields', []))

            if total_fields > 0:
                filled_fields = sum(1 for key in data.keys() if data[key] is not None)
                quality_result['completeness_score'] = min(100.0, (filled_fields / total_fields) * 100)

        # Freshness check (if timestamp available)
        if 'timestamp' in data or 'date' in data:
            timestamp_field = 'timestamp' if 'timestamp' in data else 'date'
            try:
                data_time = datetime.fromisoformat(
                    str(data[timestamp_field]).replace('Z', '+00:00')
                )
                age_hours = (datetime.now() - data_time).total_seconds() / 3600

                if age_hours < 1:
                    quality_result['freshness_score'] = 100.0
                elif age_hours < 24:
                    quality_result['freshness_score'] = max(0, 100 - (age_hours * 4))
                else:
                    quality_result['freshness_score'] = 0.0

                if quality_result['freshness_score'] < 50:
                    quality_result['issues'].append(
                        f"Data is {age_hours:.1f} hours old (stale)"
                    )
            except:
                quality_result['issues'].append("Unable to parse timestamp")

        # Consistency checks (basic)
        quality_result['consistency_score'] = 100.0  # Default to 100

        # Check for empty required fields
        if isinstance(data, dict):
            schema = self.schemas.get(schema_type, {})
            for field in schema.get('required_fields', []):
                if field in data and not data[field]:
                    quality_result['consistency_score'] -= 10
                    quality_result['issues'].append(f"Empty required field: {field}")

        # Overall score
        scores = [
            quality_result['completeness_score'],
            quality_result['freshness_score'],
            quality_result['consistency_score']
        ]
        quality_result['overall_score'] = sum(scores) / len(scores)

        return quality_result

    def generate_validation_report(self, validation_results: List[Dict]) -> str:
        """
        Generate human-readable validation report.

        Args:
            validation_results: List of validation results

        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 60)
        report.append("✅ DATA VALIDATION REPORT")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        report.append("")

        total = len(validation_results)
        valid = sum(1 for r in validation_results if r['valid'])
        invalid = total - valid
        with_warnings = sum(1 for r in validation_results if r.get('warnings'))

        report.append("📊 Summary:")
        report.append(f"  Total Validations: {total}")
        report.append(f"  ✅ Valid: {valid}")
        report.append(f"  ❌ Invalid: {invalid}")
        report.append(f"  ⚠️ With Warnings: {with_warnings}")
        report.append("")

        # Show errors if any
        all_errors = []
        for result in validation_results:
            all_errors.extend(result.get('errors', []))

        if all_errors:
            report.append("🚨 Errors:")
            for error in all_errors[:10]:  # Show first 10
                report.append(f"  • {error}")
            if len(all_errors) > 10:
                report.append(f"  ... and {len(all_errors) - 10} more")
            report.append("")

        # Show warnings if any
        all_warnings = []
        for result in validation_results:
            all_warnings.extend(result.get('warnings', []))

        if all_warnings:
            report.append("⚠️ Warnings:")
            for warning in all_warnings[:10]:  # Show first 10
                report.append(f"  • {warning}")
            if len(all_warnings) > 10:
                report.append(f"  ... and {len(all_warnings) - 10} more")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)

    def save_validation_log(self, validation_result: Dict,
                           log_file: str = "logs/validation.json") -> None:
        """
        Save validation result to log file.

        Args:
            validation_result: Validation result to save
            log_file: Path to log file
        """
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            logs = []
            if log_path.exists():
                with open(log_path, 'r') as f:
                    logs = json.load(f)

            logs.append(validation_result)

            # Keep only last 1000 entries
            logs = logs[-1000:]

            with open(log_path, 'w') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            print(f"Error saving validation log: {e}")
