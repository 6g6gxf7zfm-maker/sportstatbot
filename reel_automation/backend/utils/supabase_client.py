"""
Supabase Client for Sports Reel Bot
Handles database operations for storing and retrieving reel data
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupabaseReelDB:
    """Database client for reel automation system"""

    def __init__(self, url: str = None, key: str = None):
        """
        Initialize Supabase client

        Args:
            url: Supabase project URL (or uses SUPABASE_URL env var)
            key: Supabase anon/service key (or uses SUPABASE_SERVICE_KEY env var)
        """
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_ANON_KEY"))

        if not self.url or not self.key:
            logger.warning("Supabase credentials not provided - database features disabled")
            self.client: Optional[Client] = None
        else:
            try:
                self.client: Client = create_client(self.url, self.key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.client = None

    def save_reel(self, reel_data: Dict) -> Optional[Dict]:
        """
        Save a processed reel to the database

        Args:
            reel_data: Dictionary containing reel information

        Returns:
            Saved reel data with ID, or None if failed
        """
        if not self.client:
            logger.warning("Supabase client not available")
            return None

        try:
            # Prepare data for database
            db_data = {
                'sport': reel_data.get('sport'),
                'event_name': reel_data.get('event_name'),
                'event_id': reel_data.get('event_id'),
                'teams': reel_data.get('teams', []),
                'players': reel_data.get('players', []),
                'headline': reel_data.get('headline'),
                'play_description': reel_data.get('description'),
                'play_type': reel_data.get('play_type'),
                'viral_score': reel_data.get('viral_score', 5.0),
                'caption': reel_data.get('caption'),
                'hook': reel_data.get('hook'),
                'hashtags': reel_data.get('hashtags', []),
                'local_path': reel_data.get('processed_video_path'),
                'video_url': reel_data.get('video_url'),
                'thumbnail_url': reel_data.get('thumbnail'),
                'source_url': reel_data.get('source_url'),
                'duration': reel_data.get('duration', 15),
                'status': 'ready',
                'metadata': {
                    'timestamp': reel_data.get('timestamp'),
                    'processing_status': reel_data.get('processing_status')
                }
            }

            # Insert into database
            result = self.client.table('reels').insert(db_data).execute()

            if result.data:
                logger.info(f"Reel saved to database: {result.data[0]['id']}")
                return result.data[0]
            else:
                logger.error("Failed to save reel - no data returned")
                return None

        except Exception as e:
            logger.error(f"Error saving reel to database: {e}")
            return None

    def get_todays_reels(self) -> List[Dict]:
        """Get all reels created today"""
        if not self.client:
            return []

        try:
            result = self.client.table('reels').select('*').gte(
                'created_at',
                datetime.now().date().isoformat()
            ).order('viral_score', desc=True).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error fetching today's reels: {e}")
            return []

    def get_ready_reels(self, limit: int = 20) -> List[Dict]:
        """Get reels ready for posting"""
        if not self.client:
            return []

        try:
            result = self.client.table('reels').select('*').eq(
                'status', 'ready'
            ).order('viral_score', desc=True).limit(limit).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error fetching ready reels: {e}")
            return []

    def update_reel_status(self, reel_id: str, status: str, **kwargs) -> bool:
        """
        Update reel status

        Args:
            reel_id: UUID of the reel
            status: New status (ready, posted, archived, failed)
            **kwargs: Additional fields to update

        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False

        try:
            update_data = {'status': status}
            update_data.update(kwargs)

            result = self.client.table('reels').update(update_data).eq('id', reel_id).execute()

            if result.data:
                logger.info(f"Reel {reel_id} updated to status: {status}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error updating reel status: {e}")
            return False

    def add_to_posting_queue(
        self,
        reel_id: str,
        scheduled_time: datetime,
        priority: int = 5
    ) -> Optional[Dict]:
        """Add a reel to the posting queue"""
        if not self.client:
            return None

        try:
            queue_data = {
                'reel_id': reel_id,
                'scheduled_time': scheduled_time.isoformat(),
                'priority': priority,
                'status': 'scheduled'
            }

            result = self.client.table('posting_queue').insert(queue_data).execute()

            if result.data:
                logger.info(f"Reel {reel_id} added to posting queue")
                return result.data[0]
            return None

        except Exception as e:
            logger.error(f"Error adding to posting queue: {e}")
            return None

    def get_posting_queue(self, limit: int = 50) -> List[Dict]:
        """Get upcoming posts from queue"""
        if not self.client:
            return []

        try:
            result = self.client.table('posting_queue').select(
                '*, reels(*)'
            ).eq('status', 'scheduled').order('scheduled_time').limit(limit).execute()

            return result.data if result.data else []

        except Exception as e:
            logger.error(f"Error fetching posting queue: {e}")
            return []

    def record_performance(
        self,
        reel_id: str,
        views: int,
        likes: int,
        comments: int,
        **kwargs
    ) -> bool:
        """Record performance metrics for a reel"""
        if not self.client:
            return False

        try:
            # Calculate engagement rate
            engagement_rate = (likes + comments) / views if views > 0 else 0

            update_data = {
                'views': views,
                'likes': likes,
                'comments': comments,
                'engagement_rate': engagement_rate
            }
            update_data.update(kwargs)

            result = self.client.table('reels').update(update_data).eq('id', reel_id).execute()

            if result.data:
                logger.info(f"Performance recorded for reel {reel_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error recording performance: {e}")
            return False

    def get_performance_summary(self, days: int = 30) -> Dict:
        """Get performance summary for the last N days"""
        if not self.client:
            return {}

        try:
            result = self.client.rpc('performance_summary').execute()

            return result.data if result.data else {}

        except Exception as e:
            logger.error(f"Error fetching performance summary: {e}")
            return {}

    def get_settings(self, key: str) -> Optional[any]:
        """Get app setting by key"""
        if not self.client:
            return None

        try:
            result = self.client.table('app_settings').select('value').eq('key', key).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]['value']
            return None

        except Exception as e:
            logger.error(f"Error fetching setting {key}: {e}")
            return None

    def update_settings(self, key: str, value: any) -> bool:
        """Update app setting"""
        if not self.client:
            return False

        try:
            result = self.client.table('app_settings').update({'value': value}).eq('key', key).execute()

            if result.data:
                logger.info(f"Setting {key} updated")
                return True
            return False

        except Exception as e:
            logger.error(f"Error updating setting {key}: {e}")
            return False


# Global database client instance
db = SupabaseReelDB()
