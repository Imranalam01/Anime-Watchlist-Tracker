/**
 * AniTrack — Filters, Search, and Sorting Controller
 */

const AnimeFilters = {
    state: {
        status: 'All',
        searchQuery: '',
        genre: null,
        favoritesOnly: false,
        sortKey: 'title_asc',
        viewMode: 'grid'
    },

    /**
     * Set active status filter.
     */
    setStatus(status) {
        this.state.status = status;
        if (status !== 'All') {
            this.state.favoritesOnly = false;
        }
    },

    /**
     * Set favorites filter.
     */
    setFavoritesOnly(flag) {
        this.state.favoritesOnly = flag;
        if (flag) {
            this.state.status = 'All';
        }
    },

    /**
     * Set search query.
     */
    setSearch(query) {
        this.state.searchQuery = (query || '').trim().toLowerCase();
    },

    /**
     * Toggle or set genre filter.
     */
    setGenre(genre) {
        if (this.state.genre === genre) {
            this.state.genre = null; // Toggle off
        } else {
            this.state.genre = genre;
        }
    },

    /**
     * Set sort key ('title_asc', 'rating_desc', etc.).
     */
    setSort(sortKey) {
        this.state.sortKey = sortKey;
    },

    /**
     * Set view mode ('grid' or 'list').
     */
    setViewMode(mode) {
        this.state.viewMode = mode;
    },

    /**
     * Apply active filters, search, and sorting on a list of anime items.
     */
    apply(items = []) {
        let result = [...items];

        // 1. Status Filter
        if (!this.state.favoritesOnly && this.state.status && this.state.status !== 'All') {
            result = result.filter(item => item.status === this.state.status);
        }

        // 2. Favorites Filter
        if (this.state.favoritesOnly) {
            result = result.filter(item => Boolean(item.is_favorite));
        }

        // 3. Genre Filter
        if (this.state.genre) {
            const genreQuery = this.state.genre.toLowerCase();
            result = result.filter(item => {
                const genres = (item.genres || '').toLowerCase();
                return genres.includes(genreQuery);
            });
        }

        // 4. Search Filter (Title + Genre)
        if (this.state.searchQuery) {
            const query = this.state.searchQuery;
            result = result.filter(item => {
                const title = (item.title || '').toLowerCase();
                const genres = (item.genres || '').toLowerCase();
                return title.includes(query) || genres.includes(query);
            });
        }

        // 5. Sorting
        result.sort((a, b) => {
            switch (this.state.sortKey) {
                case 'title_asc':
                    return (a.title || '').localeCompare(b.title || '');
                case 'title_desc':
                    return (b.title || '').localeCompare(a.title || '');
                case 'rating_desc': {
                    const rA = a.rating !== null && a.rating !== undefined ? a.rating : -1;
                    const rB = b.rating !== null && b.rating !== undefined ? b.rating : -1;
                    if (rA === rB) return (a.title || '').localeCompare(b.title || '');
                    return rB - rA;
                }
                case 'rating_asc': {
                    const rA = a.rating !== null && a.rating !== undefined ? a.rating : 999;
                    const rB = b.rating !== null && b.rating !== undefined ? b.rating : 999;
                    if (rA === rB) return (a.title || '').localeCompare(b.title || '');
                    return rA - rB;
                }
                case 'episodes_desc': {
                    const epA = a.episodes_watched || 0;
                    const epB = b.episodes_watched || 0;
                    if (epA === epB) return (a.title || '').localeCompare(b.title || '');
                    return epB - epA;
                }
                case 'created_desc':
                    return (b.id || 0) - (a.id || 0);
                default:
                    return (a.title || '').localeCompare(b.title || '');
            }
        });

        return result;
    },

    /**
     * Compute status counts from the entire raw collection.
     */
    computeCounts(items = []) {
        const counts = {
            all: items.length,
            watching: 0,
            completed: 0,
            dropped: 0,
            plantowatch: 0,
            favorites: 0
        };

        for (const item of items) {
            if (item.status === 'Watching') counts.watching++;
            else if (item.status === 'Completed') counts.completed++;
            else if (item.status === 'Dropped') counts.dropped++;
            else if (item.status === 'Plan to Watch') counts.plantowatch++;

            if (item.is_favorite) counts.favorites++;
        }

        return counts;
    }
};

window.AnimeFilters = AnimeFilters;
