# AniTrack — Full-Stack Anime Watchlist Tracker

AniTrack is a responsive, modern dark-themed Anime Watchlist Tracker built with Python Flask, SQLite, vanilla JavaScript, HTML5, CSS3, and Chart.js.

## Tech Stack
- **Backend:** Python Flask with REST APIs
- **Database:** SQLite with parameterized queries & schema constraints
- **Frontend:** Vanilla JavaScript (ES6+ modular architecture), Semantic HTML5, Vanilla CSS3 (Custom Dark Anime Aesthetic)
- **Charts:** Chart.js (Doughnut status distribution chart with interactive tooltips)
- **Testing:** Pytest (13 automated API & persistence tests)


## Features
1. **MyAnimeList (Jikan API) Search & Autocomplete**: In-modal title search with auto-complete. Queries external Jikan API (`https://api.jikan.moe/v4`) with 10-minute caching, rate-limit handling, and offline resilience.
2. **Auto-Fill & Poster Loading**: Selecting a search result automatically fills title, official poster image URL, total episodes, genres, year, and community score into the form.
3. **Dual Rating System**: Displays **My Rating** (personal 1–10 score) and **MyAnimeList Rating** (external community 0–10 score) separately on every anime card. External ratings never alter or pollute personal average rating calculations.
4. **Add Anime**: Title, status (*Watching*, *Completed*, *Dropped*, *Plan to Watch*), personal rating (1–10), watched & total episodes, genres, favorite toggle, external metadata, and notes.
5. **Edit Anime**: Modal editing with form pre-population, validation, and instantaneous update.
6. **Delete Anime**: Accessible confirmation modal with title confirmation.
7. **Status Filtering**: Live tabs for *All*, *Watching*, *Completed*, *Dropped*, *Plan to Watch*, and *Favorites* with real-time item counter badges.
8. **Real-Time Search**: Instant search matching title or genres with a 1-click clear button.
9. **Sorting**: Sort by Title (A→Z, Z→A), Rating (High→Low, Low→High), Episodes Watched, and Recently Added.
10. **Summary Analytics**: Summary cards for Total Anime, Watching, Completed, Dropped, and Personal Average Rating (/10).
11. **Chart.js Distribution Chart**: Modern dark anime-themed doughnut chart with animated percentages and tooltips.
12. **Episode Progress**: Progress bar with percentage, episode count (e.g. `12 / 24 eps`), and quick `+1` / `-1` step buttons.
13. **Toggle Favorites**: 1-click golden star toggle (★) with micro-animation.
14. **Two-Tier Validation**: Full input validation on both frontend and backend.
15. **SQLite Persistence**: Complete data persistence across page refreshes and server restarts, with automatic schema migration for `external_id`, `poster_url`, `mal_rating`, and `external_source`.
16. **Responsive Design**: Responsive layout using CSS Grid and Flexbox for desktop, tablet, and mobile.
17. **State Handling**: Shimmer loading skeletons, animated empty state with quick CTA, and floating toast notifications.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check endpoint returning database connectivity status |
| `GET` | `/api/stats` | Aggregated dashboard statistics and status distribution |
| `GET` | `/api/search-anime` | Search external anime on MyAnimeList via Jikan API (`?q=<title>`) |
| `GET` | `/api/anime` | List anime with optional filters (`status`, `search`, `sort_by`, `sort_order`, `favorite`) |
| `GET` | `/api/anime/<id>` | Fetch details of a single anime record |
| `POST` | `/api/anime` | Create a new anime record |
| `PUT` | `/api/anime/<id>` | Update an existing anime record |
| `DELETE` | `/api/anime/<id>` | Delete an anime record |
| `PATCH` | `/api/anime/<id>/favorite` | Toggle favorite flag |
| `PATCH` | `/api/anime/<id>/progress` | Increment/decrement episode progress |

---

## Setup & Execution

### 1. Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### 2. Run Automated Tests
```bash
py -m pytest tests/test_api.py -v
```

### 3. Launch Development Server
```bash
py app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your web browser.
