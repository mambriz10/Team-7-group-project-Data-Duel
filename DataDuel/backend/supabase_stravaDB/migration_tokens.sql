-- =============================================================================
-- DATADUEL TOKEN STORAGE MIGRATION - SUPABASE
-- =============================================================================
-- This migration adds Strava OAuth token storage to user_strava table
-- Run this in your Supabase SQL Editor
-- =============================================================================

-- Add token columns to user_strava table
ALTER TABLE user_strava 
ADD COLUMN IF NOT EXISTS strava_access_token TEXT,
ADD COLUMN IF NOT EXISTS strava_refresh_token TEXT,
ADD COLUMN IF NOT EXISTS strava_expires_at BIGINT,
ADD COLUMN IF NOT EXISTS strava_athlete_id TEXT;

-- Create index for fast lookups by athlete_id
CREATE INDEX IF NOT EXISTS idx_user_strava_athlete_id 
ON user_strava(strava_athlete_id);

-- Add comment for documentation
COMMENT ON COLUMN user_strava.strava_access_token IS 'Strava OAuth access token';
COMMENT ON COLUMN user_strava.strava_refresh_token IS 'Strava OAuth refresh token';
COMMENT ON COLUMN user_strava.strava_expires_at IS 'Unix timestamp when access token expires';
COMMENT ON COLUMN user_strava.strava_athlete_id IS 'Strava athlete ID (unique identifier)';

-- =============================================================================
-- VERIFICATION
-- =============================================================================
-- After running this migration, verify with:
-- SELECT column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'user_strava' 
-- AND column_name LIKE 'strava_%';

