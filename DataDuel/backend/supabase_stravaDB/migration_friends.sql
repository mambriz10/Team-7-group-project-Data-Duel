-- =============================================================================
-- DATADUEL FRIENDS SYSTEM - SUPABASE MIGRATION
-- =============================================================================
-- This migration creates the complete friends system in Supabase
-- Run this in your Supabase SQL Editor
-- =============================================================================

-- =============================================================================
-- 1. FRIENDS TABLE (Accepted friendships)
-- =============================================================================
-- This table stores confirmed friendships (bidirectional)

CREATE TABLE IF NOT EXISTS friends (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    friend_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique friendships (no duplicates)
    UNIQUE(user_id, friend_id),
    
    -- Prevent self-friendship
    CHECK (user_id != friend_id)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_friends_user_id ON friends(user_id);
CREATE INDEX IF NOT EXISTS idx_friends_friend_id ON friends(friend_id);

-- =============================================================================
-- 2. FRIEND_REQUESTS TABLE (Pending requests)
-- =============================================================================
-- This table stores friend requests that haven't been accepted/rejected yet

CREATE TABLE IF NOT EXISTS friend_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    to_user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'rejected')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure unique requests (no duplicate pending requests)
    UNIQUE(from_user_id, to_user_id),
    
    -- Prevent self-requests
    CHECK (from_user_id != to_user_id)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_friend_requests_from_user ON friend_requests(from_user_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_to_user ON friend_requests(to_user_id);
CREATE INDEX IF NOT EXISTS idx_friend_requests_status ON friend_requests(status);

-- =============================================================================
-- 3. ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================
-- Enable RLS for security
ALTER TABLE friends ENABLE ROW LEVEL SECURITY;
ALTER TABLE friend_requests ENABLE ROW LEVEL SECURITY;

-- Friends table policies
-- Users can see their own friendships
CREATE POLICY "Users can view their own friendships"
    ON friends FOR SELECT
    USING (auth.uid() = user_id OR auth.uid() = friend_id);

-- Users can create friendships (handled by backend function)
CREATE POLICY "Users can create friendships"
    ON friends FOR INSERT
    WITH CHECK (auth.uid() = user_id OR auth.uid() = friend_id);

-- Users can delete their own friendships
CREATE POLICY "Users can remove their own friendships"
    ON friends FOR DELETE
    USING (auth.uid() = user_id OR auth.uid() = friend_id);

-- Friend requests policies
-- Users can view requests they sent or received
CREATE POLICY "Users can view their friend requests"
    ON friend_requests FOR SELECT
    USING (auth.uid() = from_user_id OR auth.uid() = to_user_id);

-- Users can send friend requests
CREATE POLICY "Users can send friend requests"
    ON friend_requests FOR INSERT
    WITH CHECK (auth.uid() = from_user_id);

-- Users can update requests they received (accept/reject)
CREATE POLICY "Users can update received requests"
    ON friend_requests FOR UPDATE
    USING (auth.uid() = to_user_id);

-- Users can delete requests they sent
CREATE POLICY "Users can delete sent requests"
    ON friend_requests FOR DELETE
    USING (auth.uid() = from_user_id);

-- =============================================================================
-- 4. HELPER FUNCTIONS (Optional but useful)
-- =============================================================================

-- Function to check if two users are friends
CREATE OR REPLACE FUNCTION are_friends(user1 UUID, user2 UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM friends
        WHERE (user_id = user1 AND friend_id = user2)
           OR (user_id = user2 AND friend_id = user1)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get friend count for a user
CREATE OR REPLACE FUNCTION get_friend_count(user_uuid UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM friends
        WHERE user_id = user_uuid OR friend_id = user_uuid
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get pending request count
CREATE OR REPLACE FUNCTION get_pending_request_count(user_uuid UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM friend_requests
        WHERE to_user_id = user_uuid AND status = 'pending'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- 5. TRIGGERS FOR AUTOMATIC UPDATES
-- =============================================================================

-- Update updated_at timestamp on friend_requests changes
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_friend_requests_updated_at
    BEFORE UPDATE ON friend_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- 6. CLEANUP OLD DATA (Optional)
-- =============================================================================

-- Function to delete old rejected/accepted requests (cleanup)
CREATE OR REPLACE FUNCTION cleanup_old_requests()
RETURNS void AS $$
BEGIN
    DELETE FROM friend_requests
    WHERE status IN ('accepted', 'rejected')
    AND updated_at < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- 7. VERIFICATION QUERIES
-- =============================================================================
-- Run these to verify tables were created successfully

-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('friends', 'friend_requests');

-- Check if RLS is enabled
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('friends', 'friend_requests');

-- Check policies
SELECT tablename, policyname, cmd, qual 
FROM pg_policies 
WHERE tablename IN ('friends', 'friend_requests');

-- =============================================================================
-- NOTES:
-- =============================================================================
-- 1. Run this entire SQL script in Supabase SQL Editor
-- 2. Make sure uuid-ossp extension is enabled (usually is by default)
-- 3. After running, verify tables exist in Table Editor
-- 4. Test with sample data:
--
--    -- Insert test friend request
--    INSERT INTO friend_requests (from_user_id, to_user_id)
--    VALUES ('user-uuid-1', 'user-uuid-2');
--
--    -- Accept request (creates friendship)
--    INSERT INTO friends (user_id, friend_id)
--    VALUES ('user-uuid-1', 'user-uuid-2'),
--           ('user-uuid-2', 'user-uuid-1');
--
--    -- Update request status
--    UPDATE friend_requests
--    SET status = 'accepted'
--    WHERE from_user_id = 'user-uuid-1' AND to_user_id = 'user-uuid-2';
--
-- 5. The Python backend will handle the business logic
-- 6. RLS policies ensure users can only access their own data
-- =============================================================================

