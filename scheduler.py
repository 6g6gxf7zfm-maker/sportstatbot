#!/usr/bin/env python3
"""Automated scheduler for sports reports."""
import schedule
import time
import requests
from datetime import datetime
from typing import Optional

from report_generator import SportsReportGenerator
import config


class ReportScheduler:
    """Schedules and runs automated sports reports."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.generator = SportsReportGenerator()
        self.webhook_url = webhook_url or config.SLACK_WEBHOOK_URL

    def post_to_slack(self, report: str) -> bool:
        """
        Post report to Slack webhook.

        Args:
            report: Formatted report text

        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            print("Warning: No Slack webhook URL configured")
            return False

        try:
            payload = {
                'text': report,
                'mrkdwn': True
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )

            response.raise_for_status()
            print(f"✅ Report posted to Slack at {datetime.now().strftime('%I:%M %p')}")
            return True

        except Exception as e:
            print(f"❌ Error posting to Slack: {e}")
            return False

    def morning_report(self):
        """Generate and post morning sports report."""
        print(f"\n{'='*60}")
        print(f"🌅 Running morning sports report - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        print(f"{'='*60}\n")

        try:
            # Generate full report for all active sports
            report = self.generator.generate_full_report()

            # Post to Slack if configured
            if self.webhook_url:
                self.post_to_slack(report)
            else:
                # Just print to console
                print(report)

            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"reports/morning_report_{timestamp}.md"
            self.generator.save_report(report, filename)

        except Exception as e:
            print(f"❌ Error in morning report: {e}")
            import traceback
            traceback.print_exc()

    def evening_report(self):
        """Generate and post evening sports report."""
        print(f"\n{'='*60}")
        print(f"🌙 Running evening sports report - {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        print(f"{'='*60}\n")

        try:
            # Generate full report focusing on today's results
            report = self.generator.generate_full_report()

            # Post to Slack if configured
            if self.webhook_url:
                self.post_to_slack(report)
            else:
                print(report)

            # Save to file
            timestamp = datetime.now().strftime('%Y%m%d')
            filename = f"reports/evening_report_{timestamp}.md"
            self.generator.save_report(report, filename)

        except Exception as e:
            print(f"❌ Error in evening report: {e}")
            import traceback
            traceback.print_exc()

    def quick_update(self, sport: str):
        """
        Generate quick update for a specific sport.

        Args:
            sport: Sport key (nfl, nba, etc.)
        """
        print(f"\n📊 Quick {sport.upper()} update - {datetime.now().strftime('%I:%M %p')}")

        try:
            report = self.generator.generate_sport_report(sport, quick=True)

            if self.webhook_url:
                self.post_to_slack(report)
            else:
                print(report)

        except Exception as e:
            print(f"❌ Error in quick update: {e}")

    def run(self):
        """Run the scheduler continuously."""
        print("\n" + "="*60)
        print("🤖 SportStatBot Scheduler Started")
        print("="*60)
        print("\nScheduled reports:")
        print("  🌅 Morning Report: 8:00 AM daily")
        print("  🌙 Evening Report: 6:00 PM daily")
        print("\nPress Ctrl+C to stop\n")
        print("="*60 + "\n")

        # Schedule jobs
        schedule.every().day.at("08:00").do(self.morning_report)
        schedule.every().day.at("18:00").do(self.evening_report)

        # Optional: Add sport-specific updates during game times
        # NFL - Sunday updates
        schedule.every().sunday.at("13:00").do(lambda: self.quick_update('nfl'))
        schedule.every().sunday.at("16:00").do(lambda: self.quick_update('nfl'))

        # NBA - Evening updates during season
        schedule.every().day.at("19:00").do(lambda: self.quick_update('nba'))

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("🛑 Scheduler stopped by user")
            print("="*60 + "\n")


def main():
    """Main entry point for scheduler."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Run automated sports report scheduler'
    )

    parser.add_argument(
        '--webhook',
        type=str,
        help='Slack webhook URL (overrides .env)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Run a test report immediately'
    )

    args = parser.parse_args()

    scheduler = ReportScheduler(webhook_url=args.webhook)

    if args.test:
        print("Running test report...\n")
        scheduler.morning_report()
    else:
        scheduler.run()


if __name__ == '__main__':
    main()
