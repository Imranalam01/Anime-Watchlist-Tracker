/**
 * AniTrack — Anime API Client & Utilities
 * Handles all REST API communications with the Flask backend.
 */

const AnimeAPI = {
    baseUrl: '',

    /**
     * Handle HTTP response and extract JSON or formatted error.
     */
    async _handleResponse(response) {
        let data;
        try {
            data = await response.json();
        } catch (e) {
            data = { success: false, error: 'Failed to parse JSON server response.' };
        }

        if (!response.ok) {
            const errorMsg = data.error || (data.errors ? Object.values(data.errors).join(', ') : `HTTP ${response.status}`);
            const error = new Error(errorMsg);
            error.status = response.status;
            error.details = data.errors || {};
            throw error;
        }

        return data;
    },

    /**
     * Fetch list of anime with optional query params.
     */
    async getAll(params = {}) {
        const query = new URLSearchParams();
        if (params.status && params.status !== 'All') query.append('status', params.status);
        if (params.search) query.append('search', params.search);
        if (params.sort_by) query.append('sort_by', params.sort_by);
        if (params.sort_order) query.append('sort_order', params.sort_order);
        if (params.favorite !== undefined && params.favorite !== null) query.append('favorite', params.favorite);

        const url = `${this.baseUrl}/api/anime${query.toString() ? '?' + query.toString() : ''}`;
        const response = await fetch(url);
        return this._handleResponse(response);
    },

    /**
     * Fetch single anime details.
     */
    async getById(id) {
        const response = await fetch(`${this.baseUrl}/api/anime/${id}`);
        return this._handleResponse(response);
    },

    /**
     * Create new anime entry.
     */
    async create(animeData) {
        const response = await fetch(`${this.baseUrl}/api/anime`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(animeData)
        });
        return this._handleResponse(response);
    },

    /**
     * Update existing anime entry.
     */
    async update(id, animeData) {
        const response = await fetch(`${this.baseUrl}/api/anime/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(animeData)
        });
        return this._handleResponse(response);
    },

    /**
     * Delete an anime entry.
     */
    async delete(id) {
        const response = await fetch(`${this.baseUrl}/api/anime/${id}`, {
            method: 'DELETE'
        });
        return this._handleResponse(response);
    },

    /**
     * Toggle favorite status.
     */
    async toggleFavorite(id) {
        const response = await fetch(`${this.baseUrl}/api/anime/${id}/favorite`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' }
        });
        return this._handleResponse(response);
    },

    /**
     * Update episode progress with delta (+1 / -1).
     */
    async updateProgress(id, delta) {
        const response = await fetch(`${this.baseUrl}/api/anime/${id}/progress`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ delta })
        });
        return this._handleResponse(response);
    },

    /**
     * Search external anime data via Jikan API through backend.
     */
    async searchExternal(query, limit = 10) {
        const url = `${this.baseUrl}/api/search-anime?q=${encodeURIComponent(query)}&limit=${limit}`;
        const response = await fetch(url);
        return this._handleResponse(response);
    },

    /**
     * Fetch aggregated statistics.
     */
    async getStats() {
        const response = await fetch(`${this.baseUrl}/api/stats`);
        return this._handleResponse(response);
    },

    /**
     * Health check endpoint.
     */
    async checkHealth() {
        const response = await fetch(`${this.baseUrl}/health`);
        return this._handleResponse(response);
    }
};

/**
 * Local Anime Artwork Palette Generator
 * Procedural stylized background palettes so anime cards look gorgeous without external CDNs.
 */
const AnimeVisuals = {
    palettes: [
        { bg: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)', glyph: '剣' },
        { bg: 'linear-gradient(135deg, #7c3aed 0%, #ec4899 100%)', glyph: '魔' },
        { bg: 'linear-gradient(135deg, #059669 0%, #10b981 100%)', glyph: '旅' },
        { bg: 'linear-gradient(135deg, #d97706 0%, #f43f5e 100%)', glyph: '炎' },
        { bg: 'linear-gradient(135deg, #0284c7 0%, #6366f1 100%)', glyph: '空' },
        { bg: 'linear-gradient(135deg, #831843 0%, #e11d48 100%)', glyph: '血' },
        { bg: 'linear-gradient(135deg, #1e1b4b 0%, #4338ca 100%)', glyph: '夜' },
        { bg: 'linear-gradient(135deg, #312e81 0%, #9333ea 100%)', glyph: '魂' }
    ],

    getVisualForAnime(id, title) {
        let hash = 0;
        const str = (title || '') + (id || '');
        for (let i = 0; i < str.length; i++) {
            hash = (hash << 5) - hash + str.charCodeAt(i);
            hash |= 0;
        }
        const index = Math.abs(hash) % this.palettes.length;
        const initials = (title || 'A')
            .split(' ')
            .map(word => word[0])
            .filter(Boolean)
            .slice(0, 2)
            .join('')
            .toUpperCase();

        return {
            gradient: this.palettes[index].bg,
            glyph: this.palettes[index].glyph,
            initials: initials
        };
    }
};

window.AnimeAPI = AnimeAPI;
window.AnimeVisuals = AnimeVisuals;
