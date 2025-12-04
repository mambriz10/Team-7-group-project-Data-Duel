-- =============================================================================
-- DATADUEL USER PROFILE MIGRATION - SUPABASE
-- =============================================================================
-- This migration adds user profile fields to user_strava table
-- Run this in your Supabase SQL Editor
-- =============================================================================

-- Add user profile columns to user_strava table
ALTER TABLE user_strava 
ADD COLUMN IF NOT EXISTS name TEXT,
ADD COLUMN IF NOT EXISTS display_name TEXT,
ADD COLUMN IF NOT EXISTS location TEXT,
ADD COLUMN IF NOT EXISTS avatar TEXT,
ADD COLUMN IF NOT EXISTS total_moving_time BIGINT DEFAULT 0,
ADD COLUMN IF NOT EXISTS score NUMERIC DEFAULT 0,
ADD COLUMN IF NOT EXISTS improvement NUMERIC DEFAULT 0,
ADD COLUMN IF NOT EXISTS badge_points INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS challenge_points INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create index for fast lookups by athlete_id (if not exists)
CREATE INDEX IF NOT EXISTS idx_user_strava_athlete_id 
ON user_strava(strava_athlete_id);

-- Add comments for documentation
COMMENT ON COLUMN user_strava.name IS 'User full name';
COMMENT ON COLUMN user_strava.display_name IS 'User display name';
COMMENT ON COLUMN user_strava.location IS 'User location (city, state)';
COMMENT ON COLUMN user_strava.avatar IS 'User avatar URL';
COMMENT ON COLUMN user_strava.total_moving_time IS 'Total moving time in seconds';
COMMENT ON COLUMN user_strava.score IS 'User score';
COMMENT ON COLUMN user_strava.improvement IS 'Score improvement percentage';
COMMENT ON COLUMN user_strava.badge_points IS 'Points from badges';
COMMENT ON COLUMN user_strava.challenge_points IS 'Points from weekly challenges';

-- =============================================================================
-- VERIFICATION
-- =============================================================================
-- After running this migration, verify with:
-- SELECT column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'user_strava' 
-- AND column_name IN ('name', 'location', 'avatar', 'total_moving_time', 'score', 'improvement');

