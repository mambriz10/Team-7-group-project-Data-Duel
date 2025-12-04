-- =============================================================================
-- DATADUEL LEAGUES & CHALLENGES MIGRATION - SUPABASE
-- =============================================================================
-- This migration adds simple challenge columns to leaderboards table
-- Simple format like challenges.py: 3 boolean challenges with descriptions
-- Run this in your Supabase SQL Editor
-- =============================================================================

-- =============================================================================
-- 1. UPDATE LEADERBOARDS TABLE
-- =============================================================================
-- Add simple challenge columns (format like challenges.py)

ALTER TABLE leaderboards 
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
-- Simple challenge format (like challenges.py)
ADD COLUMN IF NOT EXISTS first_challenge BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS second_challenge BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS third_challenge BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS first_description TEXT DEFAULT 'Run 3 times this week',
ADD COLUMN IF NOT EXISTS second_description TEXT DEFAULT 'Total distance ≥ 20 km',
ADD COLUMN IF NOT EXISTS third_description TEXT DEFAULT 'Set 1 segment PR';

-- =============================================================================
-- 2. COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON COLUMN leaderboards.description IS 'League description';
COMMENT ON COLUMN leaderboards.is_public IS 'Whether league is publicly visible';
COMMENT ON COLUMN leaderboards.first_challenge IS 'First challenge completion status (boolean)';
COMMENT ON COLUMN leaderboards.second_challenge IS 'Second challenge completion status (boolean)';
COMMENT ON COLUMN leaderboards.third_challenge IS 'Third challenge completion status (boolean)';
COMMENT ON COLUMN leaderboards.first_description IS 'First challenge description';
COMMENT ON COLUMN leaderboards.second_description IS 'Second challenge description';
COMMENT ON COLUMN leaderboards.third_description IS 'Third challenge description';

-- =============================================================================
-- 3. TRIGGER FOR AUTOMATIC UPDATES
-- =============================================================================

-- Update updated_at timestamp on leaderboards changes
CREATE OR REPLACE FUNCTION update_leaderboards_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_leaderboards_updated_at
    BEFORE UPDATE ON leaderboards
    FOR EACH ROW
    EXECUTE FUNCTION update_leaderboards_updated_at();

-- =============================================================================
-- 4. VERIFICATION QUERIES
-- =============================================================================
-- Run these to verify columns were added successfully

-- Check if challenge columns exist
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'leaderboards' 
AND column_name IN ('first_challenge', 'second_challenge', 'third_challenge', 
                     'first_description', 'second_description', 'third_description');

-- =============================================================================
-- NOTES:
-- =============================================================================
-- 1. Run this entire SQL script in Supabase SQL Editor
-- 2. This adds simple challenge columns to leaderboards table (like challenges.py format)
-- 3. Challenges are stored as 3 booleans (first_challenge, second_challenge, third_challenge)
-- 4. Each challenge has a description (first_description, second_description, third_description)
-- 5. League creators can update challenges via the API
-- 6. All league members can view challenges
-- 7. This is a simple MVP format - no complex progress tracking tables needed
-- =============================================================================

