// Centralized authentication helper for Supabase token management
// Handles automatic token refresh and session management

import { db } from '/strava_user_frontend.js';

/**
 * Get a valid access token, refreshing if necessary
 * This function ensures tokens are automatically refreshed before they expire
 */
export async function getAccessToken() {
  try {
    // Get current session
    let { data: { session }, error } = await db.auth.getSession();
    
    if (error) {
      console.error('[AUTH] Error getting session:', error);
      throw new Error('Failed to get session: ' + error.message);
    }
    
    if (!session) {
      throw new Error('No active session. Please log in.');
    }
    
    // Check if token is expired or close to expiring (within 5 minutes)
    const expiresAt = session.expires_at;
    const now = Math.floor(Date.now() / 1000);
    const timeUntilExpiry = expiresAt - now;
    
    // If token is expired or expires within 5 minutes, refresh it
    if (timeUntilExpiry < 300) {
      console.log('[AUTH] Token expiring soon or expired, refreshing...');
      try {
        // Refresh the session using the refresh token
        const { data: { session: newSession }, error: refreshError } = await db.auth.refreshSession(session);
        
        if (refreshError) {
          console.error('[AUTH] Error refreshing session:', refreshError);
          // If refresh fails, the session might be invalid - user needs to re-login
          if (refreshError.message && refreshError.message.includes('refresh_token')) {
            throw new Error('Session expired. Please log in again.');
          }
          // Try to use current token as fallback
          return session.access_token;
        }
        
        if (newSession && newSession.access_token) {
          console.log('[AUTH] Token refreshed successfully');
          return newSession.access_token;
        } else {
          console.warn('[AUTH] Refresh returned no session, using current token');
          return session.access_token;
        }
      } catch (refreshErr) {
        console.error('[AUTH] Refresh failed:', refreshErr);
        // If refresh completely fails, user needs to re-authenticate
        if (timeUntilExpiry <= 0) {
          throw new Error('Session expired. Please log in again.');
        }
        // If token still has time, use it
        return session.access_token;
      }
    }
    
    return session.access_token;
  } catch (error) {
    console.error('[AUTH] Error getting access token:', error);
    throw error;
  }
}

/**
 * Set up auth state change listener
 * This helps detect when sessions expire or are refreshed
 */
export function setupAuthListener(callback) {
  db.auth.onAuthStateChange((event, session) => {
    console.log('[AUTH] Auth state changed:', event, session ? 'Session exists' : 'No session');
    
    // Handle all relevant events
    if (callback) {
      callback(event, session);
    }
    
    if (event === 'SIGNED_OUT') {
      console.warn('[AUTH] User signed out');
    } else if (event === 'TOKEN_REFRESHED') {
      console.log('[AUTH] Token refreshed automatically');
    } else if (event === 'SIGNED_IN') {
      console.log('[AUTH] User signed in');
    }
  });
}

/**
 * Initialize auth - sets up auto-refresh and ensures session is valid
 * Call this once when the app loads
 */
export function initializeAuth() {
  // Set up automatic token refresh
  setupAuthListener((event, session) => {
    if (event === 'SIGNED_OUT') {
      console.warn('[AUTH] Session expired, user needs to log in again');
    }
  });
  
  // Try to refresh session on load if it exists
  db.auth.getSession().then(({ data: { session }, error }) => {
    if (error) {
      console.error('[AUTH] Error loading session:', error);
      return;
    }
    
    if (session) {
      // Check if token needs refresh
      const expiresAt = session.expires_at;
      const now = Math.floor(Date.now() / 1000);
      const timeUntilExpiry = expiresAt - now;
      
      if (timeUntilExpiry < 300) {
        console.log('[AUTH] Initializing with expired/expiring token, refreshing...');
        db.auth.refreshSession(session).catch(err => {
          console.error('[AUTH] Failed to refresh on init:', err);
        });
      }
    }
  });
}

/**
 * Check if user is authenticated
 */
export async function isAuthenticated() {
  try {
    const { data: { session } } = await db.auth.getSession();
    return !!session;
  } catch (error) {
    console.error('[AUTH] Error checking authentication:', error);
    return false;
  }
}

/**
 * Get current user ID
 */
export async function getCurrentUserId() {
  try {
    const { data: { session } } = await db.auth.getSession();
    if (!session || !session.user) {
      return null;
    }
    return session.user.id;
  } catch (error) {
    console.error('[AUTH] Error getting user ID:', error);
    return null;
  }
}

