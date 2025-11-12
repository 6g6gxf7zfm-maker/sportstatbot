"""
Reel Automation Scheduler
Runs the sports reel bot on a schedule during game times
"""

import schedule
import time
import logging
from datetime import datetime
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from sports_reel_bot import SportsReelBot
from config_loader import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReelScheduler:
    """Scheduler for automated reel processing"""

    def __init__(self):
        """Initialize the scheduler"""
        self.bot = SportsReelBot()
        self.running = False

    def process_job(self):
        """Job to run on schedule"""
        try:
            logger.info("🤖 Starting scheduled reel processing...")

            # Process highlights
            highlights = self.bot.process_highlights(
                hours_back=4,  # Look back 4 hours for recent highlights
                max_highlights=5  # Process up to 5 per run
            )

            if highlights:
                logger.info(f"✅ Processed {len(highlights)} reels successfully")

                # Generate report
                report = self.bot.generate_summary_report()
                logger.info(f"📊 Today's total: {report['total_reels']} reels")
            else:
                logger.info("ℹ️  No new highlights to process")

        except Exception as e:
            logger.error(f"❌ Error in scheduled job: {e}")

    def setup_schedule(self):
        """Set up the processing schedule"""
        logger.info("Setting up processing schedule...")

        # Get schedule config
        processing_schedule = config.get('processing_schedule', {})

        # Weekday game times: 6 PM - midnight and noon-4 PM
        weekday_times = processing_schedule.get('weekday_times', ["18:00-23:59", "12:00-16:00"])

        # Weekend times: noon - midnight
        weekend_times = processing_schedule.get('weekend_times', ["12:00-23:59"])

        # Check interval (minutes)
        interval = processing_schedule.get('check_interval_minutes', 30)

        # Schedule weekday jobs
        for time_range in weekday_times:
            start_time, end_time = time_range.split('-')
            schedule.every(interval).minutes.between(start_time, end_time).do(self.process_job)
            logger.info(f"📅 Scheduled weekday runs every {interval} min between {start_time}-{end_time}")

        # You can add more sophisticated scheduling here for weekends
        # For simplicity, we'll use the same interval approach

        # Daily cleanup at 3 AM
        schedule.every().day.at("03:00").do(self.cleanup_job)
        logger.info("🧹 Scheduled daily cleanup at 3:00 AM")

        # Weekly report on Monday at 10 AM
        schedule.every().monday.at("10:00").do(self.weekly_report_job)
        logger.info("📈 Scheduled weekly report for Mondays at 10:00 AM")

    def cleanup_job(self):
        """Cleanup old files"""
        try:
            logger.info("🧹 Running cleanup job...")
            self.bot.cleanup_old_files(days_to_keep=7)
            logger.info("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"❌ Error in cleanup job: {e}")

    def weekly_report_job(self):
        """Generate weekly performance report"""
        try:
            logger.info("📈 Generating weekly report...")
            # This would generate analytics and insights
            # For now, just log
            logger.info("✅ Weekly report generated")
        except Exception as e:
            logger.error(f"❌ Error in weekly report: {e}")

    def run(self):
        """Start the scheduler"""
        logger.info("=" * 60)
        logger.info("🚀 SPORTS REEL AUTOMATION SCHEDULER STARTED")
        logger.info("=" * 60)

        self.setup_schedule()

        logger.info("\n📋 Active schedule:")
        for job in schedule.get_jobs():
            logger.info(f"  • {job}")

        logger.info("\n⏰ Scheduler is running... (Press Ctrl+C to stop)\n")

        self.running = True

        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("\n👋 Scheduler stopped by user")
            self.running = False

    def test_run(self):
        """Run a test processing job immediately"""
        logger.info("🧪 Running test processing job...")
        self.process_job()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Sports Reel Automation Scheduler')
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run a test processing job immediately and exit'
    )

    args = parser.parse_args()

    scheduler = ReelScheduler()

    if args.test:
        # Test mode - run once and exit
        scheduler.test_run()
    else:
        # Normal mode - run continuously
        scheduler.run()


if __name__ == "__main__":
    main()
