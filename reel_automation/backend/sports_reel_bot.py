"""
Sports Reel Automation Bot
Main orchestrator for automated sports reel creation
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import traceback

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from config_loader import config
from video_processing.video_processor import VideoProcessor
from api_clients.espn_highlights_fetcher import ESPNHighlightsFetcher, AlternativeHighlightsFetcher
from api_clients.caption_generator import CaptionGenerator
from utils.viral_score import ViralScoreCalculator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SportsReelBot:
    """
    Main bot that orchestrates the sports reel automation pipeline
    """

    def __init__(self):
        """Initialize the sports reel bot"""
        logger.info("Initializing Sports Reel Bot...")

        self.config = config
        self.video_processor = VideoProcessor(
            output_resolution=config.video_resolution
        )
        self.highlights_fetcher = ESPNHighlightsFetcher()
        self.alt_fetcher = AlternativeHighlightsFetcher()
        self.caption_generator = CaptionGenerator()
        self.viral_calculator = ViralScoreCalculator(
            weights=config.viral_score_weights
        )

        self.output_dir = config.output_directory
        self.temp_dir = Path(os.path.expanduser(os.getenv('PROCESSING_TEMP_DIR', '/tmp/reel_processing')))

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Temp directory: {self.temp_dir}")

    def process_highlights(
        self,
        hours_back: int = 24,
        max_highlights: int = None
    ) -> List[Dict]:
        """
        Main processing pipeline: fetch, process, and prepare highlights

        Args:
            hours_back: How many hours back to look for highlights
            max_highlights: Maximum number of highlights to process

        Returns:
            List of processed highlight dictionaries
        """
        logger.info("=" * 60)
        logger.info("Starting highlight processing pipeline")
        logger.info("=" * 60)

        try:
            # Step 1: Fetch highlights
            highlights = self._fetch_highlights(hours_back)

            if not highlights:
                logger.warning("No highlights found")
                return []

            logger.info(f"Fetched {len(highlights)} highlights")

            # Step 2: Calculate viral scores
            highlights = self._score_highlights(highlights)

            # Step 3: Filter by threshold
            highlights = self._filter_highlights(highlights)

            if not highlights:
                logger.warning("No highlights passed viral score threshold")
                return []

            # Step 4: Limit to max highlights
            if max_highlights:
                highlights = highlights[:max_highlights]

            logger.info(f"Processing {len(highlights)} highlights")

            # Step 5: Generate captions
            highlights = self._generate_captions(highlights)

            # Step 6: Process videos (download & edit)
            processed_highlights = self._process_videos(highlights)

            # Step 7: Save metadata and organize files
            self._organize_output(processed_highlights)

            logger.info("=" * 60)
            logger.info(f"Successfully processed {len(processed_highlights)} highlights")
            logger.info("=" * 60)

            return processed_highlights

        except Exception as e:
            logger.error(f"Error in processing pipeline: {e}")
            logger.error(traceback.format_exc())
            return []

    def _fetch_highlights(self, hours_back: int) -> List[Dict]:
        """Fetch highlights from all configured sports"""
        logger.info(f"Fetching highlights from last {hours_back} hours")

        sports = [s for s in self.config.sports if s not in self.config.exclude_sports]
        logger.info(f"Monitoring sports: {', '.join(sports)}")

        highlights = self.highlights_fetcher.fetch_highlights(sports, hours_back)

        return highlights

    def _score_highlights(self, highlights: List[Dict]) -> List[Dict]:
        """Calculate viral scores and rank highlights"""
        logger.info("Calculating viral scores...")

        ranked_highlights = self.viral_calculator.rank_highlights(highlights)

        # Log top scores
        logger.info("Top viral scores:")
        for i, h in enumerate(ranked_highlights[:5], 1):
            logger.info(f"  {i}. [{h['viral_score']:.1f}] {h.get('headline', 'Unknown')}")

        return ranked_highlights

    def _filter_highlights(self, highlights: List[Dict]) -> List[Dict]:
        """Filter highlights by viral score threshold"""
        threshold = self.config.viral_score_threshold
        logger.info(f"Filtering highlights with threshold: {threshold}")

        filtered = self.viral_calculator.filter_by_threshold(highlights, threshold)

        return filtered

    def _generate_captions(self, highlights: List[Dict]) -> List[Dict]:
        """Generate captions for all highlights"""
        logger.info("Generating captions...")

        style = self.config.caption_style
        highlights_with_captions = self.caption_generator.generate_batch_captions(
            highlights, style
        )

        return highlights_with_captions

    def _process_videos(self, highlights: List[Dict]) -> List[Dict]:
        """Download and process videos"""
        logger.info("Processing videos...")

        processed = []

        for i, highlight in enumerate(highlights, 1):
            logger.info(f"Processing video {i}/{len(highlights)}: {highlight.get('headline', 'Unknown')}")

            try:
                # Download video (or use sample for testing)
                video_url = highlight.get('video_url')

                if not video_url:
                    logger.warning(f"No video URL for highlight: {highlight.get('headline')}")
                    continue

                # Create temp file path
                temp_filename = f"temp_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                temp_path = self.temp_dir / temp_filename

                # Download video
                download_success = self._download_video(video_url, str(temp_path))

                if not download_success:
                    logger.warning(f"Failed to download video from {video_url}")
                    continue

                # Process video
                output_filename = self._generate_output_filename(highlight)
                output_path = self._get_output_path(highlight) / output_filename

                processing_result = self.video_processor.process_highlight(
                    input_path=str(temp_path),
                    output_path=str(output_path),
                    max_duration=self.config.max_reel_length,
                    apply_speed_ramp=True
                )

                if processing_result['success']:
                    highlight['processed_video_path'] = str(output_path)
                    highlight['processing_status'] = 'success'
                    processed.append(highlight)
                else:
                    logger.error(f"Video processing failed: {processing_result.get('error')}")
                    highlight['processing_status'] = 'failed'

                # Clean up temp file
                if temp_path.exists():
                    temp_path.unlink()

            except Exception as e:
                logger.error(f"Error processing video: {e}")
                logger.error(traceback.format_exc())
                highlight['processing_status'] = 'error'

        logger.info(f"Successfully processed {len(processed)}/{len(highlights)} videos")

        return processed

    def _download_video(self, url: str, output_path: str) -> bool:
        """Download video from URL"""
        try:
            # Use highlights fetcher download method
            return self.highlights_fetcher.download_video(url, output_path)
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return False

    def _generate_output_filename(self, highlight: Dict) -> str:
        """Generate standardized filename for processed video"""
        timestamp = datetime.now().strftime('%H%M')
        sport = highlight.get('sport', 'Unknown').replace(' ', '_')

        teams = highlight.get('teams', [])
        if teams:
            teams_str = '_'.join([t.replace(' ', '') for t in teams[:2]])
        else:
            teams_str = 'highlight'

        filename = f"{timestamp}_{teams_str}_reel.mp4"

        return filename

    def _get_output_path(self, highlight: Dict) -> Path:
        """Get output directory path for a highlight"""
        today = datetime.now().strftime('%Y-%m-%d')
        sport = highlight.get('sport', 'Unknown')

        output_path = self.output_dir / today / sport
        output_path.mkdir(parents=True, exist_ok=True)

        return output_path

    def _organize_output(self, highlights: List[Dict]) -> None:
        """Organize output files and create metadata files"""
        logger.info("Organizing output files...")

        for highlight in highlights:
            if 'processed_video_path' not in highlight:
                continue

            video_path = Path(highlight['processed_video_path'])
            base_path = video_path.with_suffix('')

            # Save caption to text file
            caption_path = Path(str(base_path) + '_caption.txt')
            with open(caption_path, 'w', encoding='utf-8') as f:
                f.write(highlight.get('caption', ''))

            # Save metadata to JSON
            metadata_path = Path(str(base_path) + '_metadata.json')
            metadata = {
                'sport': highlight.get('sport'),
                'teams': highlight.get('teams'),
                'players': highlight.get('players'),
                'headline': highlight.get('headline'),
                'description': highlight.get('description'),
                'play_type': highlight.get('play_type'),
                'viral_score': highlight.get('viral_score'),
                'timestamp': highlight.get('timestamp'),
                'hashtags': highlight.get('hashtags', []),
                'suggested_post_time': self._suggest_post_time()
            }

            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)

        # Create posting schedule file
        self._create_posting_schedule(highlights)

    def _suggest_post_time(self) -> str:
        """Suggest optimal posting time"""
        optimal_times = self.config.get('optimal_post_times', [])

        if not optimal_times:
            return datetime.now().strftime('%Y-%m-%d %H:%M')

        # Get next optimal time
        now = datetime.now()
        current_time = now.strftime('%H:%M')

        for time_str in optimal_times:
            if time_str > current_time:
                suggested_datetime = now.strftime('%Y-%m-%d') + ' ' + time_str
                return suggested_datetime

        # If no time left today, suggest first time tomorrow
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = tomorrow.replace(day=tomorrow.day + 1)
        suggested_datetime = tomorrow.strftime('%Y-%m-%d') + ' ' + optimal_times[0]

        return suggested_datetime

    def _create_posting_schedule(self, highlights: List[Dict]) -> None:
        """Create posting schedule JSON file"""
        today = datetime.now().strftime('%Y-%m-%d')
        schedule_path = self.output_dir / today / 'posting_schedule.json'

        schedule = {
            'date': today,
            'total_reels': len(highlights),
            'reels': []
        }

        for highlight in highlights:
            if 'processed_video_path' not in highlight:
                continue

            reel_entry = {
                'video_path': highlight['processed_video_path'],
                'sport': highlight.get('sport'),
                'viral_score': highlight.get('viral_score'),
                'suggested_time': highlight.get('suggested_post_time', ''),
                'caption_file': highlight['processed_video_path'].replace('.mp4', '_caption.txt')
            }

            schedule['reels'].append(reel_entry)

        with open(schedule_path, 'w', encoding='utf-8') as f:
            json.dump(schedule, f, indent=2)

        logger.info(f"Posting schedule created: {schedule_path}")

    def cleanup_old_files(self, days_to_keep: int = 7) -> None:
        """Clean up old processed files"""
        logger.info(f"Cleaning up files older than {days_to_keep} days")

        # Implementation would go here
        # For now, just log
        pass

    def generate_summary_report(self) -> Dict:
        """Generate summary report of processed reels"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_dir = self.output_dir / today

        if not today_dir.exists():
            return {
                'date': today,
                'total_reels': 0,
                'sports': {}
            }

        # Count reels by sport
        sports_count = {}
        total_reels = 0

        for sport_dir in today_dir.iterdir():
            if sport_dir.is_dir():
                video_files = list(sport_dir.glob('*_reel.mp4'))
                count = len(video_files)
                sports_count[sport_dir.name] = count
                total_reels += count

        report = {
            'date': today,
            'total_reels': total_reels,
            'sports': sports_count,
            'output_directory': str(today_dir)
        }

        return report


def main():
    """Main entry point for manual execution"""
    print("=" * 60)
    print("SPORTS REEL AUTOMATION BOT")
    print("=" * 60)
    print()

    bot = SportsReelBot()

    # Process highlights from last 24 hours
    highlights = bot.process_highlights(hours_back=24, max_highlights=10)

    # Print summary
    print("\n" + "=" * 60)
    print("PROCESSING SUMMARY")
    print("=" * 60)

    report = bot.generate_summary_report()

    print(f"\nDate: {report['date']}")
    print(f"Total Reels Created: {report['total_reels']}")
    print(f"\nBreakdown by Sport:")

    for sport, count in report['sports'].items():
        print(f"  {sport}: {count} reels")

    print(f"\nOutput Directory: {report['output_directory']}")
    print("\nReady for posting! 🚀")


if __name__ == "__main__":
    main()
