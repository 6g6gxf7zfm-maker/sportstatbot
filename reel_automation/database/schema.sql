-- Sports Reel Automation Database Schema
-- For use with Supabase

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Processed Reels Table
CREATE TABLE reels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Video Information
  video_url TEXT,
  local_path TEXT NOT NULL,
  thumbnail_url TEXT,
  duration INTEGER, -- in seconds

  -- Sport & Event Details
  sport TEXT NOT NULL,
  event_name TEXT,
  event_id TEXT,
  teams TEXT[] DEFAULT '{}',
  players TEXT[] DEFAULT '{}',

  -- Content Description
  headline TEXT,
  play_description TEXT,
  play_type TEXT,

  -- Engagement Metrics
  viral_score FLOAT NOT NULL DEFAULT 5.0,

  -- Caption & Hashtags
  caption TEXT,
  hook TEXT,
  hashtags TEXT[] DEFAULT '{}',

  -- Posting Information
  suggested_post_time TIMESTAMP WITH TIME ZONE,
  status TEXT DEFAULT 'ready' CHECK (status IN ('ready', 'posted', 'archived', 'failed')),
  posted_at TIMESTAMP WITH TIME ZONE,

  -- Instagram Data
  instagram_url TEXT,
  instagram_post_id TEXT,

  -- Performance Metrics
  views INTEGER DEFAULT 0,
  likes INTEGER DEFAULT 0,
  comments INTEGER DEFAULT 0,
  saves INTEGER DEFAULT 0,
  shares INTEGER DEFAULT 0,
  engagement_rate FLOAT DEFAULT 0.0,

  -- Metadata
  source_url TEXT,
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for common queries
CREATE INDEX idx_reels_created_at ON reels(created_at DESC);
CREATE INDEX idx_reels_sport ON reels(sport);
CREATE INDEX idx_reels_status ON reels(status);
CREATE INDEX idx_reels_viral_score ON reels(viral_score DESC);
CREATE INDEX idx_reels_posted_at ON reels(posted_at DESC) WHERE posted_at IS NOT NULL;

-- Posting History Table (for tracking performance over time)
CREATE TABLE posting_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  reel_id UUID REFERENCES reels(id) ON DELETE CASCADE,
  posted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Engagement over time
  hour_1_views INTEGER DEFAULT 0,
  hour_1_likes INTEGER DEFAULT 0,
  hour_1_comments INTEGER DEFAULT 0,

  hour_6_views INTEGER DEFAULT 0,
  hour_6_likes INTEGER DEFAULT 0,
  hour_6_comments INTEGER DEFAULT 0,

  hour_24_views INTEGER DEFAULT 0,
  hour_24_likes INTEGER DEFAULT 0,
  hour_24_comments INTEGER DEFAULT 0,

  week_1_views INTEGER DEFAULT 0,
  week_1_likes INTEGER DEFAULT 0,
  week_1_comments INTEGER DEFAULT 0,

  -- Calculated metrics
  engagement_rate FLOAT DEFAULT 0.0,
  viral_coefficient FLOAT DEFAULT 0.0,

  -- Metadata
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_posting_history_reel_id ON posting_history(reel_id);
CREATE INDEX idx_posting_history_posted_at ON posting_history(posted_at DESC);

-- Performance Preferences Table (machine learning from past performance)
CREATE TABLE performance_preferences (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Categorization
  sport TEXT NOT NULL,
  play_type TEXT,
  posting_hour INTEGER, -- 0-23
  posting_day INTEGER, -- 0-6 (Sunday-Saturday)

  -- Aggregated metrics
  total_posts INTEGER DEFAULT 0,
  successful_posts INTEGER DEFAULT 0, -- viral_score >= 7 or engagement_rate >= 0.05
  avg_viral_score FLOAT DEFAULT 0.0,
  avg_engagement_rate FLOAT DEFAULT 0.0,
  avg_views INTEGER DEFAULT 0,
  avg_likes INTEGER DEFAULT 0,
  avg_comments INTEGER DEFAULT 0,

  -- Calculated preferences
  success_rate FLOAT DEFAULT 0.0,

  -- Metadata
  metadata JSONB DEFAULT '{}'::jsonb,

  UNIQUE(sport, play_type, posting_hour, posting_day)
);

CREATE INDEX idx_performance_sport ON performance_preferences(sport);
CREATE INDEX idx_performance_success_rate ON performance_preferences(success_rate DESC);

-- Posting Queue Table
CREATE TABLE posting_queue (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  reel_id UUID REFERENCES reels(id) ON DELETE CASCADE,
  scheduled_time TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'posted', 'cancelled')),
  priority INTEGER DEFAULT 5, -- 1-10, higher is more important

  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Metadata
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_posting_queue_scheduled_time ON posting_queue(scheduled_time);
CREATE INDEX idx_posting_queue_status ON posting_queue(status);
CREATE INDEX idx_posting_queue_reel_id ON posting_queue(reel_id);

-- App Settings Table
CREATE TABLE app_settings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  key TEXT UNIQUE NOT NULL,
  value JSONB NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default settings
INSERT INTO app_settings (key, value, description) VALUES
('sports_enabled', '["NBA", "NFL", "MLB", "MLS", "EPL", "LaLiga", "Champions League"]'::jsonb, 'List of enabled sports'),
('viral_score_threshold', '7'::jsonb, 'Minimum viral score to process'),
('posts_per_day_target', '5'::jsonb, 'Target number of posts per day'),
('caption_style', '"hype"'::jsonb, 'Default caption style'),
('optimal_post_times', '["07:30", "12:15", "18:00", "20:30", "22:00"]'::jsonb, 'Optimal posting times');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_reels_updated_at BEFORE UPDATE ON reels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performance_preferences_updated_at BEFORE UPDATE ON performance_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_posting_queue_updated_at BEFORE UPDATE ON posting_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_app_settings_updated_at BEFORE UPDATE ON app_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE reels ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE performance_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE posting_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_settings ENABLE ROW LEVEL SECURITY;

-- Allow all operations for authenticated users (adjust based on your auth setup)
CREATE POLICY "Allow all for authenticated users" ON reels
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON posting_history
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON performance_preferences
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON posting_queue
    FOR ALL USING (true);

CREATE POLICY "Allow all for authenticated users" ON app_settings
    FOR ALL USING (true);

-- Views for common queries

-- Today's reels view
CREATE OR REPLACE VIEW todays_reels AS
SELECT
    id,
    created_at,
    sport,
    teams,
    players,
    headline,
    viral_score,
    caption,
    local_path,
    thumbnail_url,
    status,
    posted_at
FROM reels
WHERE created_at >= CURRENT_DATE
ORDER BY viral_score DESC, created_at DESC;

-- Performance summary view
CREATE OR REPLACE VIEW performance_summary AS
SELECT
    sport,
    COUNT(*) as total_reels,
    AVG(viral_score) as avg_viral_score,
    AVG(engagement_rate) as avg_engagement_rate,
    SUM(views) as total_views,
    SUM(likes) as total_likes,
    SUM(comments) as total_comments
FROM reels
WHERE status = 'posted'
GROUP BY sport
ORDER BY total_views DESC;
