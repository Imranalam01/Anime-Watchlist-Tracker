/**
 * AniTrack — Main Application Controller
 * Coordinates API calls, DOM events, UI state, rendering, and toast notifications.
 * Includes MyAnimeList (Jikan API) search, auto-fill, poster loading, and separate community ratings.
 */

document.addEventListener('DOMContentLoaded', () => {
    // App State
    const AppState = {
        allAnime: [],
        isLoading: false,
        editingId: null,
        deletingId: null,
        malSearchResults: [],
        malSearchTimeout: null
    };

    // DOM Elements
    const elements = {
        // System status
        systemStatusDot: document.getElementById('system-status-dot'),
        systemStatusText: document.getElementById('system-status-text'),

        // Summary Stats
        statTotalCount: document.getElementById('stat-total-count'),
        statWatchingCount: document.getElementById('stat-watching-count'),
        statCompletedCount: document.getElementById('stat-completed-count'),
        statDroppedCount: document.getElementById('stat-dropped-count'),
        statAvgRating: document.getElementById('stat-avg-rating'),
        statTotalEpisodes: document.getElementById('stat-total-episodes'),
        statFavoritesCount: document.getElementById('stat-favorites-count'),
        statPlantowatchCount: document.getElementById('stat-plantowatch-count'),
        statCompletionRate: document.getElementById('stat-completion-rate'),

        // Badges on tabs
        badgeAll: document.getElementById('badge-all'),
        badgeWatching: document.getElementById('badge-watching'),
        badgeCompleted: document.getElementById('badge-completed'),
        badgeDropped: document.getElementById('badge-dropped'),
        badgePlantowatch: document.getElementById('badge-plantowatch'),
        badgeFavorites: document.getElementById('badge-favorites'),

        // Search & Filters
        searchInput: document.getElementById('search-input'),
        btnClearSearch: document.getElementById('btn-clear-search'),
        sortSelect: document.getElementById('sort-select'),
        filterTabs: document.querySelectorAll('.filter-tab'),
        popularGenrePills: document.getElementById('popular-genre-pills'),
        btnViewGrid: document.getElementById('btn-view-grid'),
        btnViewList: document.getElementById('btn-view-list'),

        // Display sections
        animeContainer: document.getElementById('anime-container'),
        loadingState: document.getElementById('loading-state'),
        errorState: document.getElementById('error-state'),
        errorMessage: document.getElementById('error-message'),
        btnRetry: document.getElementById('btn-retry'),
        emptyState: document.getElementById('empty-state'),
        emptySubtitle: document.getElementById('empty-subtitle'),
        btnEmptyAdd: document.getElementById('btn-empty-add'),

        // Add/Edit Modal
        animeModal: document.getElementById('anime-modal'),
        modalHeading: document.getElementById('modal-heading'),
        animeForm: document.getElementById('anime-form'),
        formAnimeId: document.getElementById('form-anime-id'),
        formTitle: document.getElementById('form-title'),
        formStatus: document.getElementById('form-status'),
        formRating: document.getElementById('form-rating'),
        formEpisodesWatched: document.getElementById('form-episodes-watched'),
        formTotalEpisodes: document.getElementById('form-total-episodes'),
        formGenres: document.getElementById('form-genres'),
        formIsFavorite: document.getElementById('form-is-favorite'),
        formNotes: document.getElementById('form-notes'),
        formGlobalError: document.getElementById('form-global-error'),
        btnSubmitText: document.getElementById('btn-submit-text'),
        btnSubmitAnime: document.getElementById('btn-submit-anime'),
        btnOpenAddModal: document.getElementById('btn-open-add-modal'),
        btnCloseModal: document.getElementById('btn-close-modal'),
        btnCancelModal: document.getElementById('btn-cancel-modal'),
        modalTagChips: document.getElementById('modal-tag-chips'),

        // External Metadata Form Fields
        formExternalId: document.getElementById('form-external-id'),
        formPosterUrl: document.getElementById('form-poster-url'),
        formMalRating: document.getElementById('form-mal-rating'),
        formExternalSource: document.getElementById('form-external-source'),

        // External Jikan/MAL Search Components
        malSearchInput: document.getElementById('mal-search-input'),
        btnMalSearch: document.getElementById('btn-mal-search'),
        btnMalSearchText: document.getElementById('btn-mal-search-text'),
        malSearchStatus: document.getElementById('mal-search-status'),
        malSearchResults: document.getElementById('mal-search-results'),
        malSelectedPreview: document.getElementById('mal-selected-preview'),
        malPreviewPoster: document.getElementById('mal-preview-poster'),
        malPreviewTitle: document.getElementById('mal-preview-title'),
        malPreviewScore: document.getElementById('mal-preview-score'),
        malPreviewEps: document.getElementById('mal-preview-eps'),
        malPreviewYear: document.getElementById('mal-preview-year'),
        btnClearMalSelection: document.getElementById('btn-clear-mal-selection'),

        // Delete Modal
        deleteModal: document.getElementById('delete-modal'),
        deleteAnimeTitle: document.getElementById('delete-anime-title'),
        deleteAnimeId: document.getElementById('delete-anime-id'),
        btnConfirmDelete: document.getElementById('btn-confirm-delete'),
        btnCloseDeleteModal: document.getElementById('btn-close-delete-modal'),
        btnCancelDelete: document.getElementById('btn-cancel-delete'),

        // Toast Container
        toastContainer: document.getElementById('toast-container')
    };

    /**
     * Display a floating toast notification.
     */
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        let icon = 'ℹ️';
        if (type === 'success') icon = '✓';
        if (type === 'error') icon = '⚠️';

        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-text">${escapeHtml(message)}</span>
        `;

        elements.toastContainer.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(15px)';
            setTimeout(() => toast.remove(), 250);
        }, 3200);
    }

    /**
     * Escape HTML strings to prevent XSS.
     */
    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = String(str);
        return div.innerHTML;
    }

    /**
     * Format a rating number.
     */
    function formatRating(rating) {
        if (rating === null || rating === undefined || rating === '') {
            return '<span class="unrated-badge">Unrated</span>';
        }
        return `★ ${rating}/10`;
    }

    /**
     * Build and render anime cards into DOM.
     * Renders saved poster (with local fallback) and separate My Rating vs MAL Rating.
     */
    function renderCards() {
        const filtered = AnimeFilters.apply(AppState.allAnime);

        if (AppState.isLoading) {
            elements.loadingState.style.display = 'block';
            elements.emptyState.style.display = 'none';
            elements.errorState.style.display = 'none';
            elements.animeContainer.innerHTML = '';
            return;
        }

        elements.loadingState.style.display = 'none';

        if (filtered.length === 0) {
            elements.emptyState.style.display = 'block';
            elements.animeContainer.innerHTML = '';

            if (AppState.allAnime.length === 0) {
                elements.emptySubtitle.textContent = 'Your watchlist is currently empty. Start tracking your first anime now!';
                elements.btnEmptyAdd.style.display = 'inline-flex';
            } else {
                elements.emptySubtitle.textContent = 'No anime matched your current search and filter criteria.';
                elements.btnEmptyAdd.style.display = 'none';
            }
            return;
        }

        elements.emptyState.style.display = 'none';
        elements.errorState.style.display = 'none';

        // Apply view mode
        elements.animeContainer.className = AnimeFilters.state.viewMode === 'list' 
            ? 'anime-grid list-view' 
            : 'anime-grid';

        const cardsHtml = filtered.map(item => {
            const visual = AnimeVisuals.getVisualForAnime(item.id, item.title);
            const statusClass = 'status-' + item.status.toLowerCase().replace(/\s+/g, '');
            const isFav = Boolean(item.is_favorite);

            // Progress Bar calculation
            const watched = item.episodes_watched || 0;
            const total = item.total_episodes || 0;
            let pct = 0;
            let progressLabel = `${watched}`;
            if (total > 0) {
                pct = Math.min(100, Math.round((watched / total) * 100));
                progressLabel = `${watched} / ${total} eps`;
            } else {
                progressLabel = `${watched} eps (airing)`;
            }

            // Genre tags
            const genreTags = (item.genres || '')
                .split(',')
                .map(g => g.trim())
                .filter(Boolean)
                .map(g => `<span class="card-genre-tag">${escapeHtml(g)}</span>`)
                .join('');

            // Poster image handling with local fallback
            const hasPoster = Boolean(item.poster_url);
            const posterHtml = hasPoster 
                ? `
                    <img 
                        src="${escapeHtml(item.poster_url)}" 
                        alt="${escapeHtml(item.title)} poster" 
                        class="anime-poster-img" 
                        loading="lazy" 
                        onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                    >
                    <div class="anime-cover-gradient" style="display: none; background: ${visual.gradient};">
                        <div class="anime-cover-watermark">${visual.glyph}</div>
                    </div>
                    <div class="anime-cover-overlay"></div>
                `
                : `
                    <div class="anime-cover-gradient" style="background: ${visual.gradient};">
                        <div class="anime-cover-watermark">${visual.glyph}</div>
                    </div>
                    <div class="anime-cover-overlay"></div>
                `;

            // Separate Ratings: User Personal Rating vs MyAnimeList Rating
            const myRatingHtml = `
                <span class="my-rating-badge" title="Your personal rating: ${item.rating ? item.rating + '/10' : 'Unrated'}">
                    <span class="my-rating-label">My:</span>
                    <span>${item.rating ? '★ ' + item.rating + '/10' : 'Unrated'}</span>
                </span>
            `;

            const malRatingHtml = (item.mal_rating !== null && item.mal_rating !== undefined)
                ? `
                    <span class="mal-rating-badge" title="MyAnimeList Community Score: ${Number(item.mal_rating).toFixed(2)}/10">
                        <span class="mal-source-tag">MAL</span>
                        <span>★ ${Number(item.mal_rating).toFixed(2)}</span>
                    </span>
                `
                : '';

            return `
                <article class="anime-card" data-id="${item.id}">
                    <div class="anime-cover">
                        ${posterHtml}
                        
                        <div class="anime-cover-top">
                            <div class="ratings-group">
                                ${myRatingHtml}
                                ${malRatingHtml}
                            </div>
                            <button 
                                type="button" 
                                class="btn-star-fav ${isFav ? 'is-favorite' : ''}" 
                                data-action="toggle-fav" 
                                data-id="${item.id}"
                                title="${isFav ? 'Remove from favorites' : 'Add to favorites'}"
                                aria-label="Toggle favorite"
                            >
                                ★
                            </button>
                        </div>
                    </div>

                    <div class="anime-card-body">
                        <div class="anime-card-title-row">
                            <h3 class="anime-card-title">${escapeHtml(item.title)}</h3>
                            <span class="status-badge ${statusClass}">
                                <span class="status-badge-dot"></span>
                                ${escapeHtml(item.status)}
                            </span>
                        </div>

                        <!-- Episode Progress Box -->
                        <div class="anime-progress-section">
                            <div class="progress-header">
                                <span class="progress-text">Progress</span>
                                <span class="progress-counter">${progressLabel}</span>
                            </div>
                            <div class="progress-bar-bg" role="progressbar" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100">
                                <div class="progress-bar-fill ${statusClass}" style="width: ${pct}%;"></div>
                            </div>
                            <div class="progress-actions">
                                <span class="progress-pct">${pct}% completed</span>
                                <div class="quick-episode-buttons">
                                    <button 
                                        type="button" 
                                        class="btn-ep-step" 
                                        data-action="step-episode" 
                                        data-delta="-1" 
                                        data-id="${item.id}"
                                        title="Decrease 1 episode"
                                        aria-label="Decrease episode progress"
                                    >
                                        -1
                                    </button>
                                    <button 
                                        type="button" 
                                        class="btn-ep-step" 
                                        data-action="step-episode" 
                                        data-delta="1" 
                                        data-id="${item.id}"
                                        title="Increase 1 episode"
                                        aria-label="Increase episode progress"
                                    >
                                        +1
                                    </button>
                                </div>
                            </div>
                        </div>

                        ${genreTags ? `<div class="anime-card-genres">${genreTags}</div>` : ''}

                        ${item.notes ? `
                            <div class="anime-card-notes">
                                "${escapeHtml(item.notes)}"
                            </div>
                        ` : ''}
                    </div>

                    <div class="anime-card-footer">
                        <button type="button" class="btn-card-action action-edit" data-action="edit" data-id="${item.id}">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                            </svg>
                            <span>Edit</span>
                        </button>
                        <button type="button" class="btn-card-action action-delete" data-action="delete" data-id="${item.id}">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="3 6 5 6 21 6"></polyline>
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            </svg>
                            <span>Delete</span>
                        </button>
                    </div>
                </article>
            `;
        }).join('');

        elements.animeContainer.innerHTML = cardsHtml;
    }

    /**
     * Update all dashboard stats and filter counts.
     */
    function updateStatsDisplay(stats) {
        if (!stats) return;

        elements.statTotalCount.textContent = stats.total_anime || 0;
        elements.statWatchingCount.textContent = stats.status_distribution?.['Watching'] || 0;
        elements.statCompletedCount.textContent = stats.status_distribution?.['Completed'] || 0;
        elements.statDroppedCount.textContent = stats.status_distribution?.['Dropped'] || 0;

        const avg = stats.average_rating ? Number(stats.average_rating).toFixed(1) : '0.0';
        elements.statAvgRating.innerHTML = `${avg}<span class="stat-sub">/10</span>`;

        elements.statTotalEpisodes.textContent = stats.total_episodes_watched || 0;
        elements.statFavoritesCount.textContent = stats.total_favorites || 0;
        elements.statPlantowatchCount.textContent = stats.status_distribution?.['Plan to Watch'] || 0;

        const total = stats.total_anime || 0;
        const completed = stats.status_distribution?.['Completed'] || 0;
        const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0;
        elements.statCompletionRate.textContent = `${completionRate}%`;

        // Update Tab Badges
        const counts = AnimeFilters.computeCounts(AppState.allAnime);
        elements.badgeAll.textContent = counts.all;
        elements.badgeWatching.textContent = counts.watching;
        elements.badgeCompleted.textContent = counts.completed;
        elements.badgeDropped.textContent = counts.dropped;
        elements.badgePlantowatch.textContent = counts.plantowatch;
        elements.badgeFavorites.textContent = counts.favorites;

        // Update Chart
        if (window.AnimeCharts) {
            AnimeCharts.update(stats.status_distribution || {});
        }
    }

    /**
     * Fetch complete state from backend and refresh views.
     */
    async function loadDashboard() {
        AppState.isLoading = true;
        elements.loadingState.style.display = 'block';
        elements.errorState.style.display = 'none';

        try {
            const [animeResponse, statsResponse] = await Promise.all([
                AnimeAPI.getAll(),
                AnimeAPI.getStats()
            ]);

            AppState.allAnime = animeResponse.data || [];
            AppState.isLoading = false;

            updateStatsDisplay(statsResponse.data);
            renderCards();

            // Check health status dot
            AnimeAPI.checkHealth()
                .then(h => {
                    if (h.status === 'healthy') {
                        elements.systemStatusDot.style.backgroundColor = '#10b981';
                        elements.systemStatusText.textContent = 'SQLite Active';
                    }
                })
                .catch(() => {
                    elements.systemStatusDot.style.backgroundColor = '#f59e0b';
                    elements.systemStatusText.textContent = 'Degraded';
                });

        } catch (error) {
            AppState.isLoading = false;
            elements.loadingState.style.display = 'none';
            elements.errorState.style.display = 'block';
            elements.errorMessage.textContent = error.message || 'Failed to load watchlist data.';
        }
    }

    /**
     * Modal Form Helpers
     */
    function clearFormErrors() {
        document.querySelectorAll('.field-error').forEach(el => el.textContent = '');
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        elements.formGlobalError.style.display = 'none';
        elements.formGlobalError.textContent = '';
    }

    function resetMalSearch() {
        elements.malSearchInput.value = '';
        elements.malSearchStatus.style.display = 'none';
        elements.malSearchStatus.textContent = '';
        elements.malSearchResults.style.display = 'none';
        elements.malSearchResults.innerHTML = '';
        elements.btnMalSearchText.textContent = 'Search';
        elements.btnMalSearch.disabled = false;
        AppState.malSearchResults = [];
    }

    function setSelectedMalPreview(title, posterUrl, score, eps, year) {
        if (title || posterUrl) {
            elements.malPreviewPoster.src = posterUrl || '';
            elements.malPreviewPoster.onerror = () => { elements.malPreviewPoster.src = ''; };
            elements.malPreviewTitle.textContent = title || 'Linked Anime';
            elements.malPreviewScore.textContent = score ? `★ MAL: ${Number(score).toFixed(2)}` : 'MAL: Unrated';
            elements.malPreviewEps.textContent = eps ? `${eps} eps` : 'Ongoing';
            elements.malPreviewYear.textContent = year ? `${year}` : '';
            elements.malSelectedPreview.style.display = 'flex';
        } else {
            elements.malSelectedPreview.style.display = 'none';
        }
    }

    function clearSelectedMalData() {
        elements.formExternalId.value = '';
        elements.formPosterUrl.value = '';
        elements.formMalRating.value = '';
        elements.formExternalSource.value = 'MyAnimeList';
        elements.malSelectedPreview.style.display = 'none';
    }

    function openModal(mode = 'add', anime = null) {
        clearFormErrors();
        resetMalSearch();
        elements.animeForm.reset();

        if (mode === 'edit' && anime) {
            AppState.editingId = anime.id;
            elements.modalHeading.textContent = 'Edit Anime Details';
            elements.btnSubmitText.textContent = 'Update Anime';

            elements.formAnimeId.value = anime.id;
            elements.formTitle.value = anime.title || '';
            elements.formStatus.value = anime.status || 'Watching';
            elements.formRating.value = anime.rating !== null ? anime.rating : '';
            elements.formEpisodesWatched.value = anime.episodes_watched || 0;
            elements.formTotalEpisodes.value = anime.total_episodes || 0;
            elements.formGenres.value = anime.genres || '';
            elements.formIsFavorite.checked = Boolean(anime.is_favorite);
            elements.formNotes.value = anime.notes || '';

            // External metadata
            elements.formExternalId.value = anime.external_id || '';
            elements.formPosterUrl.value = anime.poster_url || '';
            elements.formMalRating.value = anime.mal_rating !== null ? anime.mal_rating : '';
            elements.formExternalSource.value = anime.external_source || 'MyAnimeList';

            if (anime.poster_url || anime.external_id) {
                setSelectedMalPreview(
                    anime.title,
                    anime.poster_url,
                    anime.mal_rating,
                    anime.total_episodes,
                    null
                );
            } else {
                elements.malSelectedPreview.style.display = 'none';
            }
        } else {
            AppState.editingId = null;
            elements.modalHeading.textContent = 'Add New Anime';
            elements.btnSubmitText.textContent = 'Save Anime';

            elements.formAnimeId.value = '';
            elements.formTitle.value = '';
            elements.formStatus.value = 'Watching';
            elements.formRating.value = '';
            elements.formEpisodesWatched.value = 0;
            elements.formTotalEpisodes.value = 0;
            elements.formGenres.value = '';
            elements.formIsFavorite.checked = false;
            elements.formNotes.value = '';

            clearSelectedMalData();
        }

        elements.animeModal.classList.add('open');
        elements.animeModal.setAttribute('aria-hidden', 'false');
        setTimeout(() => elements.formTitle.focus(), 100);
    }

    function closeModal() {
        elements.animeModal.classList.remove('open');
        elements.animeModal.setAttribute('aria-hidden', 'true');
        AppState.editingId = null;
        resetMalSearch();
    }

    function openDeleteModal(anime) {
        if (!anime) return;
        AppState.deletingId = anime.id;
        elements.deleteAnimeTitle.textContent = anime.title;
        elements.deleteAnimeId.value = anime.id;
        elements.deleteModal.classList.add('open');
        elements.deleteModal.setAttribute('aria-hidden', 'false');
    }

    function closeDeleteModal() {
        elements.deleteModal.classList.remove('open');
        elements.deleteModal.setAttribute('aria-hidden', 'true');
        AppState.deletingId = null;
    }

    /**
     * Execute Search on Jikan / MyAnimeList API
     */
    async function performMalSearch(query) {
        const cleanQuery = (query || '').trim();
        if (!cleanQuery) {
            elements.malSearchStatus.className = 'mal-search-status info';
            elements.malSearchStatus.textContent = 'Please enter an anime title to search.';
            elements.malSearchStatus.style.display = 'block';
            elements.malSearchResults.style.display = 'none';
            return;
        }

        elements.btnMalSearchText.textContent = '...';
        elements.btnMalSearch.disabled = true;
        elements.malSearchStatus.className = 'mal-search-status loading';
        elements.malSearchStatus.textContent = `Searching MyAnimeList for "${cleanQuery}"...`;
        elements.malSearchStatus.style.display = 'block';
        elements.malSearchResults.style.display = 'none';

        try {
            const res = await AnimeAPI.searchExternal(cleanQuery);
            elements.btnMalSearchText.textContent = 'Search';
            elements.btnMalSearch.disabled = false;

            const items = res.data || [];
            AppState.malSearchResults = items;

            if (items.length === 0) {
                elements.malSearchStatus.className = 'mal-search-status info';
                elements.malSearchStatus.textContent = `No anime matching "${cleanQuery}" found on MyAnimeList.`;
                elements.malSearchStatus.style.display = 'block';
                elements.malSearchResults.style.display = 'none';
                return;
            }

            elements.malSearchStatus.style.display = 'none';
            elements.malSearchResults.style.display = 'flex';

            elements.malSearchResults.innerHTML = items.map((item, idx) => {
                const yearLabel = item.year ? ` (${item.year})` : '';
                const epsLabel = item.episodes ? `${item.episodes} eps` : 'Ongoing';
                const scoreLabel = item.mal_rating ? `★ MAL ${Number(item.mal_rating).toFixed(2)}` : 'MAL: Unrated';
                const thumb = item.poster_url || '';

                return `
                    <div class="mal-result-card" data-idx="${idx}" role="option" tabindex="0">
                        ${thumb ? `<img src="${escapeHtml(thumb)}" alt="" class="mal-result-thumb" onerror="this.style.display='none';">` : ''}
                        <div class="mal-result-info">
                            <div class="mal-result-title">${escapeHtml(item.title)}${yearLabel}</div>
                            <div class="mal-result-meta">
                                <span class="mal-badge-score">${scoreLabel}</span>
                                <span>• ${epsLabel}</span>
                                <span>• ${escapeHtml(item.genres || 'Anime')}</span>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');

        } catch (err) {
            elements.btnMalSearchText.textContent = 'Search';
            elements.btnMalSearch.disabled = false;
            elements.malSearchStatus.className = 'mal-search-status error';
            elements.malSearchStatus.textContent = err.message || 'Failed to connect to anime search service.';
            elements.malSearchStatus.style.display = 'block';
            elements.malSearchResults.style.display = 'none';
        }
    }

    /**
     * Handle Jikan Search Selection
     */
    elements.malSearchResults.addEventListener('click', (e) => {
        const card = e.target.closest('.mal-result-card');
        if (!card) return;

        const idx = parseInt(card.dataset.idx, 10);
        const selected = AppState.malSearchResults[idx];
        if (!selected) return;

        // Auto-populate form fields
        elements.formTitle.value = selected.title || '';
        elements.formTotalEpisodes.value = selected.episodes || 0;
        elements.formGenres.value = selected.genres || '';
        elements.formPosterUrl.value = selected.poster_url || '';
        elements.formExternalId.value = selected.external_id || '';
        elements.formMalRating.value = selected.mal_rating !== null ? selected.mal_rating : '';
        elements.formExternalSource.value = selected.external_source || 'MyAnimeList';

        // Show Preview Pill
        setSelectedMalPreview(
            selected.title,
            selected.poster_url,
            selected.mal_rating,
            selected.episodes,
            selected.year
        );

        // Hide Results List
        elements.malSearchResults.style.display = 'none';
        elements.malSearchStatus.style.display = 'none';
        elements.malSearchInput.value = '';

        showToast(`Auto-filled metadata for "${selected.title}"!`, 'success');
        elements.formStatus.focus();
    });

    // Clear external MAL metadata
    elements.btnClearMalSelection.addEventListener('click', () => {
        clearSelectedMalData();
        showToast('Cleared external MyAnimeList data link.', 'info');
    });

    // MAL Search Button & Enter key
    elements.btnMalSearch.addEventListener('click', () => {
        performMalSearch(elements.malSearchInput.value);
    });

    elements.malSearchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            performMalSearch(elements.malSearchInput.value);
        }
    });

    // Debounced Autocomplete
    elements.malSearchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        clearTimeout(AppState.malSearchTimeout);
        if (val.length >= 3) {
            AppState.malSearchTimeout = setTimeout(() => {
                performMalSearch(val);
            }, 450);
        } else if (val.length === 0) {
            elements.malSearchResults.style.display = 'none';
            elements.malSearchStatus.style.display = 'none';
        }
    });

    /**
     * Frontend Form Validation
     */
    function validateForm() {
        clearFormErrors();
        let isValid = true;

        const title = elements.formTitle.value.trim();
        if (!title) {
            elements.formTitle.classList.add('is-invalid');
            document.getElementById('error-form-title').textContent = 'Title is required.';
            isValid = false;
        }

        const ratingVal = elements.formRating.value.trim();
        if (ratingVal !== '') {
            const num = Number(ratingVal);
            if (isNaN(num) || !Number.isInteger(num) || num < 1 || num > 10) {
                elements.formRating.classList.add('is-invalid');
                document.getElementById('error-form-rating').textContent = 'Personal rating must be an integer from 1 to 10.';
                isValid = false;
            }
        }

        const watchedVal = Number(elements.formEpisodesWatched.value);
        if (isNaN(watchedVal) || watchedVal < 0) {
            elements.formEpisodesWatched.classList.add('is-invalid');
            document.getElementById('error-form-episodes-watched').textContent = 'Watched episodes must be 0 or more.';
            isValid = false;
        }

        const totalVal = Number(elements.formTotalEpisodes.value);
        if (isNaN(totalVal) || totalVal < 0) {
            elements.formTotalEpisodes.classList.add('is-invalid');
            document.getElementById('error-form-total-episodes').textContent = 'Total episodes must be 0 or more.';
            isValid = false;
        }

        if (totalVal > 0 && watchedVal > totalVal) {
            elements.formEpisodesWatched.classList.add('is-invalid');
            document.getElementById('error-form-episodes-watched').textContent = `Watched episodes cannot exceed total (${totalVal}).`;
            isValid = false;
        }

        return isValid;
    }

    /**
     * Handle Form Submission (Add or Edit)
     */
    elements.animeForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        if (!validateForm()) return;

        const payload = {
            title: elements.formTitle.value.trim(),
            status: elements.formStatus.value,
            rating: elements.formRating.value.trim() !== '' ? parseInt(elements.formRating.value, 10) : null,
            episodes_watched: parseInt(elements.formEpisodesWatched.value, 10) || 0,
            total_episodes: parseInt(elements.formTotalEpisodes.value, 10) || 0,
            genres: elements.formGenres.value.trim(),
            is_favorite: elements.formIsFavorite.checked,
            notes: elements.formNotes.value.trim(),
            // External metadata
            external_id: elements.formExternalId.value ? parseInt(elements.formExternalId.value, 10) : null,
            poster_url: elements.formPosterUrl.value.trim() || null,
            mal_rating: elements.formMalRating.value ? parseFloat(elements.formMalRating.value) : null,
            external_source: elements.formExternalSource.value.trim() || 'MyAnimeList'
        };

        elements.btnSubmitAnime.disabled = true;
        elements.btnSubmitText.textContent = 'Saving...';

        try {
            if (AppState.editingId) {
                await AnimeAPI.update(AppState.editingId, payload);
                showToast(`"${payload.title}" updated successfully!`, 'success');
            } else {
                await AnimeAPI.create(payload);
                showToast(`"${payload.title}" added to your watchlist!`, 'success');
            }

            closeModal();
            await loadDashboard();
        } catch (error) {
            if (error.details) {
                for (const [field, msg] of Object.entries(error.details)) {
                    const errEl = document.getElementById(`error-form-${field}`);
                    const inputEl = document.getElementById(`form-${field}`);
                    if (errEl) errEl.textContent = msg;
                    if (inputEl) inputEl.classList.add('is-invalid');
                }
            }
            elements.formGlobalError.style.display = 'block';
            elements.formGlobalError.textContent = error.message || 'Error saving anime.';
        } finally {
            elements.btnSubmitAnime.disabled = false;
            elements.btnSubmitText.textContent = AppState.editingId ? 'Update Anime' : 'Save Anime';
        }
    });

    /**
     * Confirm Delete Anime
     */
    elements.btnConfirmDelete.addEventListener('click', async () => {
        if (!AppState.deletingId) return;

        elements.btnConfirmDelete.disabled = true;
        try {
            await AnimeAPI.delete(AppState.deletingId);
            showToast('Anime removed from watchlist.', 'info');
            closeDeleteModal();
            await loadDashboard();
        } catch (error) {
            showToast(error.message || 'Failed to delete anime', 'error');
        } finally {
            elements.btnConfirmDelete.disabled = false;
        }
    });

    /**
     * Card Delegated Actions (Favorite, Progress +/- 1, Edit, Delete)
     */
    elements.animeContainer.addEventListener('click', async (e) => {
        const targetBtn = e.target.closest('button');
        if (!targetBtn) return;

        const action = targetBtn.dataset.action;
        const animeId = parseInt(targetBtn.dataset.id, 10);
        if (!action || isNaN(animeId)) return;

        const anime = AppState.allAnime.find(a => a.id === animeId);

        // 1. Toggle Favorite
        if (action === 'toggle-fav') {
            try {
                const res = await AnimeAPI.toggleFavorite(animeId);
                const updated = res.data;
                const idx = AppState.allAnime.findIndex(a => a.id === animeId);
                if (idx !== -1) AppState.allAnime[idx] = updated;

                renderCards();
                const statsRes = await AnimeAPI.getStats();
                updateStatsDisplay(statsRes.data);
                showToast(res.message, 'success');
            } catch (err) {
                showToast(err.message || 'Could not toggle favorite', 'error');
            }
        }

        // 2. Step Episode Progress
        if (action === 'step-episode') {
            const delta = parseInt(targetBtn.dataset.delta, 10);
            try {
                const res = await AnimeAPI.updateProgress(animeId, delta);
                const updated = res.data;
                const idx = AppState.allAnime.findIndex(a => a.id === animeId);
                if (idx !== -1) AppState.allAnime[idx] = updated;

                renderCards();
                const statsRes = await AnimeAPI.getStats();
                updateStatsDisplay(statsRes.data);
            } catch (err) {
                showToast(err.message || 'Could not update progress', 'error');
            }
        }

        // 3. Edit Anime
        if (action === 'edit') {
            if (anime) openModal('edit', anime);
        }

        // 4. Delete Anime
        if (action === 'delete') {
            if (anime) openDeleteModal(anime);
        }
    });

    /**
     * Filter and Search Event Handlers
     */
    elements.searchInput.addEventListener('input', (e) => {
        const val = e.target.value;
        AnimeFilters.setSearch(val);
        elements.btnClearSearch.style.display = val ? 'block' : 'none';
        renderCards();
    });

    elements.btnClearSearch.addEventListener('click', () => {
        elements.searchInput.value = '';
        AnimeFilters.setSearch('');
        elements.btnClearSearch.style.display = 'none';
        renderCards();
        elements.searchInput.focus();
    });

    elements.sortSelect.addEventListener('change', (e) => {
        AnimeFilters.setSort(e.target.value);
        renderCards();
    });

    // Status Filter Tabs
    elements.filterTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            elements.filterTabs.forEach(t => {
                t.classList.remove('active');
                t.setAttribute('aria-selected', 'false');
            });
            tab.classList.add('active');
            tab.setAttribute('aria-selected', 'true');

            if (tab.dataset.favorite === 'true') {
                AnimeFilters.setFavoritesOnly(true);
            } else {
                AnimeFilters.setStatus(tab.dataset.status);
            }
            renderCards();
        });
    });

    // Popular Genre Pills
    elements.popularGenrePills.addEventListener('click', (e) => {
        const pill = e.target.closest('.genre-pill');
        if (!pill) return;

        const genre = pill.dataset.genre;
        const isActive = pill.classList.contains('active');

        document.querySelectorAll('.genre-pill').forEach(p => p.classList.remove('active'));
        if (!isActive) {
            pill.classList.add('active');
            AnimeFilters.setGenre(genre);
        } else {
            AnimeFilters.setGenre(null);
        }
        renderCards();
    });

    // View Mode Toggle (Grid / List)
    elements.btnViewGrid.addEventListener('click', () => {
        elements.btnViewGrid.classList.add('active');
        elements.btnViewList.classList.remove('active');
        AnimeFilters.setViewMode('grid');
        renderCards();
    });

    elements.btnViewList.addEventListener('click', () => {
        elements.btnViewList.classList.add('active');
        elements.btnViewGrid.classList.remove('active');
        AnimeFilters.setViewMode('list');
        renderCards();
    });

    // Quick tag chips in modal
    elements.modalTagChips.addEventListener('click', (e) => {
        const chip = e.target.closest('.form-tag-chip');
        if (!chip) return;

        const tag = chip.dataset.tag;
        const current = elements.formGenres.value.trim();
        const currentList = current ? current.split(',').map(s => s.trim()) : [];

        if (!currentList.includes(tag)) {
            currentList.push(tag);
            elements.formGenres.value = currentList.join(', ');
        }
    });

    // Modal Triggers
    elements.btnOpenAddModal.addEventListener('click', () => openModal('add'));
    elements.btnEmptyAdd.addEventListener('click', () => openModal('add'));
    elements.btnCloseModal.addEventListener('click', closeModal);
    elements.btnCancelModal.addEventListener('click', closeModal);

    elements.btnCloseDeleteModal.addEventListener('click', closeDeleteModal);
    elements.btnCancelDelete.addEventListener('click', closeDeleteModal);

    elements.btnRetry.addEventListener('click', loadDashboard);

    // Close on backdrop click
    elements.animeModal.addEventListener('click', (e) => {
        if (e.target === elements.animeModal) closeModal();
    });
    elements.deleteModal.addEventListener('click', (e) => {
        if (e.target === elements.deleteModal) closeDeleteModal();
    });

    // ESC key closes modals
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeDeleteModal();
        }
    });

    // Initial Load
    loadDashboard();
});
