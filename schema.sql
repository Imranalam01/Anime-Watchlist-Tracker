-- AniTrack SQLite Database Schema

CREATE TABLE IF NOT EXISTS anime (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL COLLATE NOCASE,
    status TEXT NOT NULL CHECK(status IN ('Watching', 'Completed', 'Dropped', 'Plan to Watch')),
    rating INTEGER CHECK(rating IS NULL OR (rating >= 1 AND rating <= 10)),
    episodes_watched INTEGER NOT NULL DEFAULT 0 CHECK(episodes_watched >= 0),
    total_episodes INTEGER NOT NULL DEFAULT 0 CHECK(total_episodes >= 0),
    genres TEXT DEFAULT '',
    is_favorite INTEGER NOT NULL DEFAULT 0 CHECK(is_favorite IN (0, 1)),
    notes TEXT DEFAULT '',
    external_id INTEGER,
    poster_url TEXT,
    mal_rating REAL,
    external_source TEXT DEFAULT 'MyAnimeList',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_anime_status ON anime(status);
CREATE INDEX IF NOT EXISTS idx_anime_rating ON anime(rating);
CREATE INDEX IF NOT EXISTS idx_anime_favorite ON anime(is_favorite);
CREATE INDEX IF NOT EXISTS idx_anime_title ON anime(title);
