/**
 * API Client for DataDuel Backend
 * Handles all communication with Flask API
 */

// Import configuration from config.js
import { API_URL } from './config.js';

const API_BASE_URL = API_URL;

class DataDuelAPI {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async _fetch(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'API request failed');
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // ========================================================================
    // Authentication
    // ========================================================================

    async getStatus() {
        return this._fetch('/api/status');
    }

    // ========================================================================
    // Data Sync
    // ========================================================================

    async syncActivities() {
        return this._fetch('/api/sync', { method: 'POST' });
    }

    // ========================================================================
    // User Profile
    // ========================================================================

    async getProfile() {
        return this._fetch('/api/profile');
    }

    // ========================================================================
    // Leaderboard
    // ========================================================================

    async getLeaderboard() {
        return this._fetch('/api/leaderboard');
    }

    // ========================================================================
    // Leagues
    // ========================================================================

    async getLeagueLeaderboard(leagueId) {
        return this._fetch(`/api/league/${leagueId}/leaderboard`);
    }

    async getLeagueInfo(leagueId) {
        return this._fetch(`/api/league/${leagueId}/info`);
    }

    async deleteLeague(leagueId, accessToken) {
        return this._fetch(`/leaderboard/${leagueId}/delete`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ access_token: accessToken })
        });
    }

    async addMemberToLeague(leagueId, userId, accessToken) {
        return this._fetch('/leaderboard/add_member', {
            method: 'POST',
            body: JSON.stringify({
                access_token: accessToken,
                leaderboard_id: leagueId,
                user_id: userId
            })
        });
    }

    async getLeagueChallenges(leagueId) {
        return this._fetch(`/api/league/${leagueId}/challenges`);
    }

    async updateLeagueChallenges(leagueId, accessToken, challengeData) {
        return this._fetch(`/api/league/${leagueId}/challenges/update`, {
            method: 'POST',
            body: JSON.stringify({
                access_token: accessToken,
                ...challengeData
            })
        });
    }

    // ========================================================================
    // Friends
    // ========================================================================

    async getFriends() {
        return this._fetch('/api/friends');
    }

    // ========================================================================
    // Strava Direct
    // ========================================================================

    async getActivities() {
        return this._fetch('/strava/activities');
    }

    // ========================================================================
    // Routes
    // ========================================================================

    async getAllRoutes() {
        return this._fetch('/api/routes/all');
    }

    async searchRoutes(distance_km, difficulty, surface) {
        const params = new URLSearchParams();
        if (distance_km) params.append('distance_km', distance_km);
        if (difficulty) params.append('difficulty', difficulty);
        if (surface) params.append('surface', surface);
        
        return this._fetch(`/api/routes/search?${params.toString()}`);
    }

    async getRoute(routeId) {
        return this._fetch(`/api/routes/${routeId}`);
    }

    async generateCustomRoute(distance_km, start_location) {
        return this._fetch('/api/routes/generate', {
            method: 'POST',
            body: JSON.stringify({ distance_km, start_location })
        });
    }
}

// Create global API instance
const api = new DataDuelAPI();

// Make available globally for non-module scripts
window.api = api;
window.DataDuelAPI = DataDuelAPI;

// Export for ES6 modules
export { DataDuelAPI, api };

