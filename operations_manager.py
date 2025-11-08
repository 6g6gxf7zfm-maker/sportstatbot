#!/usr/bin/env python3
"""
SportStatBot Operations Manager
Centralized management for all pipeline and operations systems.
"""

import sys
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

# Import all pipeline and operations components
from pipeline.cache_manager import CacheManager
from pipeline.health_monitor import HealthMonitor
from pipeline.error_recovery import ErrorRecoveryBot
from pipeline.rate_limiter import RateLimiter
from pipeline.schema_validator import SchemaValidator
from pipeline.offline_mode import OfflineMode
from pipeline.token_manager import TokenManager
from pipeline.smart_throttling import SmartThrottling
from pipeline.retention_policy import RetentionPolicy

from monitoring.report_generator import MonitoringReportGenerator
from monitoring.heatmap_generator import FreshnessHeatmap

from storage.backup_manager import BackupManager
from storage.cloud_sync import CloudStorageSync
from storage.sheets_bridge import GoogleSheetsbridge


class OperationsManager:
    """
    Centralized operations manager for SportStatBot.
    Provides unified interface to all pipeline and ops systems.
    """

    def __init__(self):
        """Initialize operations manager with all subsystems."""
        print("🚀 Initializing SportStatBot Operations Manager...")

        # Pipeline components
        self.cache = CacheManager()
        self.health = HealthMonitor()
        self.recovery = ErrorRecoveryBot()
        self.rate_limiter = RateLimiter()
        self.validator = SchemaValidator()
        self.offline = OfflineMode()
        self.tokens = TokenManager()
        self.throttling = SmartThrottling()
        self.retention = RetentionPolicy()

        # Monitoring components
        self.monitoring = MonitoringReportGenerator()
        self.heatmap = FreshnessHeatmap()

        # Storage components
        self.backup = BackupManager()
        self.cloud_sync = CloudStorageSync()
        self.sheets = GoogleSheetsbridge()

        print("✅ Operations Manager initialized")

    def run_health_check(self) -> None:
        """Run comprehensive system health check."""
        print("\n" + "=" * 70)
        print("🏥 RUNNING SYSTEM HEALTH CHECK")
        print("=" * 70 + "\n")

        # Health report
        print(self.health.generate_daily_digest())
        print("")

        # Heatmap
        print(self.heatmap.render_text_heatmap())
        print("")

        # Cache stats
        stats = self.cache.get_cache_stats()
        print(f"💾 Cache: {stats['total_entries']} entries, {stats['size_mb']:.2f} MB")
        print("")

    def run_daily_operations(self) -> None:
        """Run daily operational tasks."""
        print("\n" + "=" * 70)
        print("📅 RUNNING DAILY OPERATIONS")
        print(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70 + "\n")

        # Generate daily digest
        print("📊 Generating daily digest...")
        digest = self.monitoring.generate_daily_digest()
        print(digest)

        # Save digest
        self.monitoring.save_report(digest, "daily_digest")

        # Cleanup old data
        print("\n🗑️ Running cleanup tasks...")
        cleanup_results = self.retention.cleanup_all()
        print(f"   Deleted {cleanup_results['total_deleted_files']} files")
        print(f"   Freed {cleanup_results['total_freed_mb']:.2f} MB")

        # Create backup
        print("\n💾 Creating backup...")
        backup_path = self.backup.create_backup()
        if backup_path:
            print(f"   Backup created: {backup_path}")

        # Reset 24h counters
        print("\n🔄 Resetting counters...")
        self.health.reset_24h_counters()

        print("\n✅ Daily operations complete")

    def generate_master_report(self) -> str:
        """Generate comprehensive master report."""
        report = []

        report.append("=" * 70)
        report.append("📋 SPORTSTATBOT - MASTER OPERATIONS REPORT")
        report.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}")
        report.append("=" * 70)
        report.append("")

        # System Health
        report.append(self.health.generate_daily_digest())
        report.append("\n")

        # Recovery Stats
        report.append(self.recovery.generate_recovery_report())
        report.append("\n")

        # Rate Limits
        report.append(self.rate_limiter.generate_status_report())
        report.append("\n")

        # Offline Mode
        report.append(self.offline.generate_offline_report())
        report.append("\n")

        # Throttling
        report.append(self.throttling.generate_throttling_report())
        report.append("\n")

        # Backups
        report.append(self.backup.generate_backup_report())
        report.append("\n")

        # Cloud Sync
        report.append(self.cloud_sync.generate_sync_report())
        report.append("\n")

        # Retention Policy
        report.append(self.retention.generate_retention_report())
        report.append("\n")

        # Token Management
        report.append(self.tokens.generate_token_report())
        report.append("\n")

        return "\n".join(report)

    def save_master_report(self, filename: Optional[str] = None) -> str:
        """
        Generate and save master report.

        Args:
            filename: Optional filename (auto-generated if None)

        Returns:
            Path to saved report
        """
        report = self.generate_master_report()

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/monitoring/master_report_{timestamp}.txt"

        filepath = Path(filename)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            f.write(report)

        return str(filepath)

    def get_system_status(self) -> Dict:
        """
        Get current system status as JSON.

        Returns:
            Complete system status dictionary
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'health': self.health.generate_health_report(),
            'cache': self.cache.get_cache_stats(),
            'recovery': self.recovery.get_recovery_stats(),
            'rate_limits': self.rate_limiter.get_all_status(),
            'offline_mode': self.offline.get_offline_status(),
            'backups': {
                'local': len(self.backup.list_backups('local'))
            }
        }

    def interactive_menu(self) -> None:
        """Run interactive menu for operations management."""
        while True:
            print("\n" + "=" * 70)
            print("🤖 SPORTSTATBOT OPERATIONS MANAGER")
            print("=" * 70)
            print("\n📋 Available Commands:")
            print("  1. Run Health Check")
            print("  2. Generate Daily Digest")
            print("  3. View Freshness Heatmap")
            print("  4. Run Daily Operations")
            print("  5. Create Backup")
            print("  6. Generate Master Report")
            print("  7. View System Status")
            print("  8. Cleanup Old Data")
            print("  9. View Rate Limits")
            print("  0. Exit")
            print("")

            choice = input("Enter command number: ").strip()

            if choice == "1":
                self.run_health_check()

            elif choice == "2":
                print("\n" + self.monitoring.generate_daily_digest())

            elif choice == "3":
                print("\n" + self.heatmap.render_text_heatmap())

            elif choice == "4":
                self.run_daily_operations()

            elif choice == "5":
                print("\n💾 Creating backup...")
                backup_path = self.backup.create_backup()
                if backup_path:
                    print(f"✅ Backup created: {backup_path}")

            elif choice == "6":
                print("\n📋 Generating master report...")
                report_path = self.save_master_report()
                print(f"✅ Report saved: {report_path}")
                print("\nPreview:")
                print(self.generate_master_report()[:500] + "...")

            elif choice == "7":
                import json
                print("\n" + json.dumps(self.get_system_status(), indent=2))

            elif choice == "8":
                print("\n🗑️ Running cleanup...")
                results = self.retention.cleanup_all()
                print(f"✅ Deleted {results['total_deleted_files']} files")
                print(f"✅ Freed {results['total_freed_mb']:.2f} MB")

            elif choice == "9":
                print("\n" + self.rate_limiter.generate_status_report())

            elif choice == "0":
                print("\n👋 Goodbye!")
                break

            else:
                print("\n❌ Invalid choice. Please try again.")

            input("\nPress Enter to continue...")


def main():
    """Main entry point for operations manager."""
    import argparse

    parser = argparse.ArgumentParser(
        description='SportStatBot Operations Manager'
    )

    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Run system health check'
    )

    parser.add_argument(
        '--daily-ops',
        action='store_true',
        help='Run daily operations tasks'
    )

    parser.add_argument(
        '--master-report',
        action='store_true',
        help='Generate master report'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run interactive menu'
    )

    args = parser.parse_args()

    # Initialize manager
    ops = OperationsManager()

    if args.health_check:
        ops.run_health_check()

    elif args.daily_ops:
        ops.run_daily_operations()

    elif args.master_report:
        report_path = ops.save_master_report()
        print(f"✅ Master report saved: {report_path}")
        print("\nReport preview:")
        print(ops.generate_master_report())

    elif args.interactive:
        ops.interactive_menu()

    else:
        # Default: show help
        parser.print_help()
        print("\n" + "=" * 70)
        print("💡 Quick Start:")
        print("=" * 70)
        print("\n  Run health check:")
        print("    python operations_manager.py --health-check")
        print("\n  Run daily operations:")
        print("    python operations_manager.py --daily-ops")
        print("\n  Interactive mode:")
        print("    python operations_manager.py --interactive")
        print("")


if __name__ == '__main__':
    main()
