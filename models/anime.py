import os
import sqlite3
from typing import Dict, Any, List, Optional, Tuple

VALID_STATUSES = ['Watching', 'Completed', 'Dropped', 'Plan to Watch']
ALLOWED_SORT_FIELDS = {
    'title': 'title',
    'rating': 'rating',
    'episodes_watched': 'episodes_watched',
    'status': 'status',
    'created_at': 'created_at',
    'updated_at': 'updated_at',
    'mal_rating': 'mal_rating'
}

DEFAULT_SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'schema.sql')

STARTER_ANIME = [
    {
        'title': 'Frieren: Beyond Journey\'s End',
        'status': 'Completed',
        'rating': 10,
        'episodes_watched': 28,
        'total_episodes': 28,
        'genres': 'Adventure, Drama, Fantasy',
        'is_favorite': 1,
        'notes': 'Absolute masterpiece of storytelling, pacing, and emotional depth.',
        'external_id': 52991,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1015/138062l.jpg',
        'mal_rating': 9.32,
        'external_source': 'MyAnimeList'
    },
    {
        'title': 'Jujutsu Kaisen',
        'status': 'Completed',
        'rating': 9,
        'episodes_watched': 24,
        'total_episodes': 24,
        'genres': 'Action, Fantasy',
        'is_favorite': 1,
        'notes': 'Super fluid animation and dynamic cursed energy combat.',
        'external_id': 40748,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1171/109222l.jpg',
        'mal_rating': 8.61,
        'external_source': 'MyAnimeList'
    },
    {
        'title': 'Solo Leveling',
        'status': 'Watching',
        'rating': 8,
        'episodes_watched': 9,
        'total_episodes': 12,
        'genres': 'Action, Fantasy',
        'is_favorite': 1,
        'notes': 'High-octane dungeon raids and great soundtrack.',
        'external_id': 52299,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1598/141566l.jpg',
        'mal_rating': 8.27,
        'external_source': 'MyAnimeList'
    },
    {
        'title': 'Attack on Titan',
        'status': 'Completed',
        'rating': 10,
        'episodes_watched': 25,
        'total_episodes': 25,
        'genres': 'Action, Drama, Suspense',
        'is_favorite': 1,
        'notes': 'One of the best modern anime narratives ever written.',
        'external_id': 16498,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/10/47347l.jpg',
        'mal_rating': 8.55,
        'external_source': 'MyAnimeList'
    },
    {
        'title': 'Chainsaw Man',
        'status': 'Completed',
        'rating': 9,
        'episodes_watched': 12,
        'total_episodes': 12,
        'genres': 'Action, Fantasy',
        'is_favorite': 0,
        'notes': 'Super cinematic directing and chaotic energy.',
        'external_id': 44511,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1806/126216l.jpg',
        'mal_rating': 8.46,
        'external_source': 'MyAnimeList'
    },
    {
        'title': 'Demon Slayer: Kimetsu no Yaiba',
        'status': 'Watching',
        'rating': 8,
        'episodes_watched': 20,
        'total_episodes': 26,
        'genres': 'Action, Fantasy',
        'is_favorite': 0,
        'notes': 'Ufotable visual spectacle as always.',
        'external_id': 38000,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1286/99889l.jpg',
        'mal_rating': 8.48,
        'external_source': 'MyAnimeList'
    },
    {
        'title': 'Naruto',
        'status': 'Completed',
        'rating': 9,
        'episodes_watched': 220,
        'total_episodes': 220,
        'genres': 'Action, Adventure, Fantasy',
        'is_favorite': 1,
        'notes': 'Childhood classic, chunin exams arc was legendary.',
        'external_id': 20,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/13/17405l.jpg',
        'mal_rating': 7.99,
        'external_source': 'MyAnimeList'
    },
    {
        'title': 'Steins;Gate',
        'status': 'Plan to Watch',
        'rating': None,
        'episodes_watched': 0,
        'total_episodes': 24,
        'genres': 'Drama, Sci-Fi, Suspense',
        'is_favorite': 1,
        'notes': 'Recommended by multiple friends for time-travel narrative.',
        'external_id': 9253,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1935/127974l.jpg',
        'mal_rating': 9.07,
        'external_source': 'MyAnimeList'
    }
]


def get_db(db_path: str) -> sqlite3.Connection:
    """Create and return a configured SQLite connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str, schema_path: Optional[str] = None, seed: bool = True) -> None:
    """Initialize SQLite tables, apply migrations safely, and seed starter records."""
    if schema_path is None:
        schema_path = DEFAULT_SCHEMA_PATH

    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    with get_db(db_path) as conn:
        # Create base table from schema if not present
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())

        # Migration: safely ensure external metadata columns exist on existing databases
        cur = conn.execute("PRAGMA table_info(anime)")
        existing_cols = {col['name'] for col in cur.fetchall()}

        if 'external_id' not in existing_cols:
            conn.execute("ALTER TABLE anime ADD COLUMN external_id INTEGER")
        if 'poster_url' not in existing_cols:
            conn.execute("ALTER TABLE anime ADD COLUMN poster_url TEXT")
        if 'mal_rating' not in existing_cols:
            conn.execute("ALTER TABLE anime ADD COLUMN mal_rating REAL")
        if 'external_source' not in existing_cols:
            conn.execute("ALTER TABLE anime ADD COLUMN external_source TEXT DEFAULT 'MyAnimeList'")

        conn.execute("CREATE INDEX IF NOT EXISTS idx_anime_external_id ON anime(external_id)")
        
        # Gently update starter records if their poster is missing
        for item in STARTER_ANIME:
            conn.execute("""
                UPDATE anime 
                SET external_id = ?, poster_url = ?, mal_rating = ?, external_source = 'MyAnimeList'
                WHERE title LIKE ? AND (poster_url IS NULL OR poster_url = '')
            """, (item.get('external_id'), item.get('poster_url'), item.get('mal_rating'), f"%{item['title'][:8]}%"))

        conn.commit()

        # Seed starter data if empty
        if seed:
            cur = conn.execute("SELECT COUNT(*) AS count FROM anime")
            if cur.fetchone()['count'] == 0:
                for item in STARTER_ANIME:
                    conn.execute("""
                        INSERT INTO anime (
                            title, status, rating, episodes_watched, total_episodes, 
                            genres, is_favorite, notes, external_id, poster_url, mal_rating, external_source
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        item['title'],
                        item['status'],
                        item['rating'],
                        item['episodes_watched'],
                        item['total_episodes'],
                        item['genres'],
                        item['is_favorite'],
                        item['notes'],
                        item.get('external_id'),
                        item.get('poster_url'),
                        item.get('mal_rating'),
                        item.get('external_source', 'MyAnimeList')
                    ))
                conn.commit()


def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert an SQLite Row object to a clean Python dictionary."""
    if row is None:
        return None
    d = dict(row)
    d['is_favorite'] = bool(d.get('is_favorite', 0))
    if 'mal_rating' in d and d['mal_rating'] is not None:
        d['mal_rating'] = round(float(d['mal_rating']), 2)
    return d


def validate_anime_data(data: Any, is_update: bool = False) -> Tuple[bool, Dict[str, str], Dict[str, Any]]:
    """
    Validate anime payload including external metadata.
    Returns (is_valid, errors_dict, cleaned_data).
    """
    errors: Dict[str, str] = {}
    cleaned: Dict[str, Any] = {}

    if not isinstance(data, dict):
        return False, {'payload': 'Request payload must be a JSON object'}, {}

    # Title validation
    if 'title' in data or not is_update:
        raw_title = data.get('title')
        if not raw_title or not isinstance(raw_title, str) or not raw_title.strip():
            errors['title'] = 'Title is required and cannot be empty.'
        elif len(raw_title.strip()) > 200:
            errors['title'] = 'Title must be 200 characters or less.'
        else:
            cleaned['title'] = raw_title.strip()

    # Status validation
    if 'status' in data or not is_update:
        raw_status = data.get('status')
        if not raw_status or raw_status not in VALID_STATUSES:
            errors['status'] = f"Status must be one of: {', '.join(VALID_STATUSES)}."
        else:
            cleaned['status'] = raw_status

    # Rating validation (personal rating 1 to 10 or None)
    if 'rating' in data:
        raw_rating = data.get('rating')
        if raw_rating is None or raw_rating == '' or raw_rating == 'null':
            cleaned['rating'] = None
        else:
            try:
                rating_val = int(raw_rating)
                if rating_val < 1 or rating_val > 10:
                    errors['rating'] = 'Personal rating must be an integer between 1 and 10.'
                else:
                    cleaned['rating'] = rating_val
            except (ValueError, TypeError):
                errors['rating'] = 'Personal rating must be a valid integer between 1 and 10.'
    elif not is_update:
        cleaned['rating'] = None

    # Episodes watched validation
    if 'episodes_watched' in data:
        raw_watched = data.get('episodes_watched')
        try:
            watched_val = int(raw_watched) if raw_watched is not None else 0
            if watched_val < 0:
                errors['episodes_watched'] = 'Watched episodes count must be 0 or greater.'
            else:
                cleaned['episodes_watched'] = watched_val
        except (ValueError, TypeError):
            errors['episodes_watched'] = 'Watched episodes count must be a non-negative integer.'
    elif not is_update:
        cleaned['episodes_watched'] = 0

    # Total episodes validation
    if 'total_episodes' in data:
        raw_total = data.get('total_episodes')
        try:
            total_val = int(raw_total) if raw_total is not None else 0
            if total_val < 0:
                errors['total_episodes'] = 'Total episodes must be 0 or greater (0 for unknown/ongoing).'
            else:
                cleaned['total_episodes'] = total_val
        except (ValueError, TypeError):
            errors['total_episodes'] = 'Total episodes must be a non-negative integer.'
    elif not is_update:
        cleaned['total_episodes'] = 0

    # Cross-field episode validation
    watched = cleaned.get('episodes_watched', 0)
    total = cleaned.get('total_episodes', 0)
    if total > 0 and watched > total:
        errors['episodes_watched'] = f'Watched episodes ({watched}) cannot exceed total episodes ({total}).'

    # Auto-adjust status if watched equals total episodes
    if total > 0 and watched == total and cleaned.get('status') == 'Watching':
        cleaned['status'] = 'Completed'

    # Genres validation
    if 'genres' in data:
        raw_genres = data.get('genres')
        if isinstance(raw_genres, list):
            cleaned['genres'] = ', '.join([str(g).strip() for g in raw_genres if str(g).strip()])
        elif isinstance(raw_genres, str):
            cleaned['genres'] = raw_genres.strip()
        else:
            cleaned['genres'] = ''
    elif not is_update:
        cleaned['genres'] = ''

    # Favorite status validation
    if 'is_favorite' in data:
        raw_fav = data.get('is_favorite')
        if isinstance(raw_fav, bool):
            cleaned['is_favorite'] = 1 if raw_fav else 0
        elif str(raw_fav).lower() in ('1', 'true', 'yes'):
            cleaned['is_favorite'] = 1
        else:
            cleaned['is_favorite'] = 0
    elif not is_update:
        cleaned['is_favorite'] = 0

    # Notes validation
    if 'notes' in data:
        raw_notes = data.get('notes')
        cleaned['notes'] = str(raw_notes).strip() if raw_notes else ''
    elif not is_update:
        cleaned['notes'] = ''

    # External Metadata (external_id, poster_url, mal_rating, external_source)
    if 'external_id' in data:
        raw_ext_id = data.get('external_id')
        if raw_ext_id is not None and str(raw_ext_id).strip():
            try:
                cleaned['external_id'] = int(raw_ext_id)
            except (ValueError, TypeError):
                cleaned['external_id'] = None
        else:
            cleaned['external_id'] = None
    elif not is_update:
        cleaned['external_id'] = None

    if 'poster_url' in data:
        raw_poster = data.get('poster_url')
        if raw_poster and isinstance(raw_poster, str) and raw_poster.strip():
            cleaned['poster_url'] = raw_poster.strip()
        else:
            cleaned['poster_url'] = None
    elif not is_update:
        cleaned['poster_url'] = None

    if 'mal_rating' in data:
        raw_mal = data.get('mal_rating')
        if raw_mal is not None and raw_mal != '' and raw_mal != 'null':
            try:
                mal_val = float(raw_mal)
                if 0.0 <= mal_val <= 10.0:
                    cleaned['mal_rating'] = round(mal_val, 2)
                else:
                    cleaned['mal_rating'] = None
            except (ValueError, TypeError):
                cleaned['mal_rating'] = None
        else:
            cleaned['mal_rating'] = None
    elif not is_update:
        cleaned['mal_rating'] = None

    if 'external_source' in data:
        raw_source = data.get('external_source')
        cleaned['external_source'] = str(raw_source).strip() if raw_source else 'MyAnimeList'
    elif not is_update:
        cleaned['external_source'] = 'MyAnimeList'

    is_valid = len(errors) == 0
    return is_valid, errors, cleaned


class AnimeModel:
    """Data Access Object for Anime records with external metadata support."""

    @staticmethod
    def get_all(
        db_path: str,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = 'title',
        sort_order: str = 'asc',
        is_favorite: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        query = "SELECT * FROM anime WHERE 1=1"
        params: List[Any] = []

        if status and status in VALID_STATUSES:
            query += " AND status = ?"
            params.append(status)

        if is_favorite is not None:
            query += " AND is_favorite = ?"
            params.append(1 if is_favorite else 0)

        if search and search.strip():
            query += " AND (title LIKE ? OR genres LIKE ?)"
            term = f"%{search.strip()}%"
            params.extend([term, term])

        # Sorting
        sort_col = ALLOWED_SORT_FIELDS.get(sort_by.lower(), 'title')
        order_direction = 'DESC' if str(sort_order).lower() == 'desc' else 'ASC'

        # Special NULL handling for ratings: NULL ratings at the bottom
        if sort_col in ('rating', 'mal_rating'):
            query += f" ORDER BY {sort_col} IS NULL, {sort_col} {order_direction}, title ASC"
        else:
            query += f" ORDER BY {sort_col} {order_direction}"

        with get_db(db_path) as conn:
            cur = conn.execute(query, params)
            return [row_to_dict(r) for r in cur.fetchall()]

    @staticmethod
    def get_by_id(db_path: str, anime_id: int) -> Optional[Dict[str, Any]]:
        with get_db(db_path) as conn:
            cur = conn.execute("SELECT * FROM anime WHERE id = ?", (anime_id,))
            row = cur.fetchone()
            return row_to_dict(row)

    @staticmethod
    def create(db_path: str, cleaned_data: Dict[str, Any]) -> Dict[str, Any]:
        with get_db(db_path) as conn:
            cur = conn.execute("""
                INSERT INTO anime (
                    title, status, rating, episodes_watched, total_episodes, 
                    genres, is_favorite, notes, external_id, poster_url, mal_rating, external_source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                cleaned_data['title'],
                cleaned_data['status'],
                cleaned_data.get('rating'),
                cleaned_data.get('episodes_watched', 0),
                cleaned_data.get('total_episodes', 0),
                cleaned_data.get('genres', ''),
                cleaned_data.get('is_favorite', 0),
                cleaned_data.get('notes', ''),
                cleaned_data.get('external_id'),
                cleaned_data.get('poster_url'),
                cleaned_data.get('mal_rating'),
                cleaned_data.get('external_source', 'MyAnimeList')
            ))
            anime_id = cur.lastrowid
            conn.commit()

        return AnimeModel.get_by_id(db_path, anime_id)

    @staticmethod
    def update(db_path: str, anime_id: int, cleaned_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = AnimeModel.get_by_id(db_path, anime_id)
        if not existing:
            return None

        # Build update query dynamically
        fields = []
        params = []
        allowed_keys = [
            'title', 'status', 'rating', 'episodes_watched', 'total_episodes',
            'genres', 'is_favorite', 'notes', 'external_id', 'poster_url', 'mal_rating', 'external_source'
        ]
        for key in allowed_keys:
            if key in cleaned_data:
                fields.append(f"{key} = ?")
                params.append(cleaned_data[key])

        if not fields:
            return existing

        fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(anime_id)

        query = f"UPDATE anime SET {', '.join(fields)} WHERE id = ?"

        with get_db(db_path) as conn:
            conn.execute(query, params)
            conn.commit()

        return AnimeModel.get_by_id(db_path, anime_id)

    @staticmethod
    def delete(db_path: str, anime_id: int) -> bool:
        with get_db(db_path) as conn:
            cur = conn.execute("DELETE FROM anime WHERE id = ?", (anime_id,))
            conn.commit()
            return cur.rowcount > 0

    @staticmethod
    def toggle_favorite(db_path: str, anime_id: int) -> Optional[Dict[str, Any]]:
        existing = AnimeModel.get_by_id(db_path, anime_id)
        if not existing:
            return None

        new_fav = 0 if existing['is_favorite'] else 1
        with get_db(db_path) as conn:
            conn.execute(
                "UPDATE anime SET is_favorite = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_fav, anime_id)
            )
            conn.commit()

        return AnimeModel.get_by_id(db_path, anime_id)

    @staticmethod
    def increment_episode(db_path: str, anime_id: int, delta: int = 1) -> Optional[Dict[str, Any]]:
        existing = AnimeModel.get_by_id(db_path, anime_id)
        if not existing:
            return None

        watched = max(0, existing['episodes_watched'] + delta)
        total = existing['total_episodes']

        if total > 0 and watched > total:
            watched = total

        new_status = existing['status']
        if total > 0 and watched == total:
            new_status = 'Completed'
        elif watched > 0 and existing['status'] in ('Plan to Watch', 'Dropped') and delta > 0:
            new_status = 'Watching'

        with get_db(db_path) as conn:
            conn.execute("""
                UPDATE anime
                SET episodes_watched = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (watched, new_status, anime_id))
            conn.commit()

        return AnimeModel.get_by_id(db_path, anime_id)

    @staticmethod
    def get_stats(db_path: str) -> Dict[str, Any]:
        """
        Calculate aggregated stats.
        Note: Average rating strictly uses personal ratings ('rating'), never external scores.
        """
        with get_db(db_path) as conn:
            cur = conn.execute("""
                SELECT 
                    COUNT(*) AS total_anime,
                    ROUND(AVG(rating), 1) AS average_rating,
                    SUM(episodes_watched) AS total_episodes_watched,
                    SUM(CASE WHEN is_favorite = 1 THEN 1 ELSE 0 END) AS total_favorites
                FROM anime
            """)
            summary = cur.fetchone()

            cur_status = conn.execute("""
                SELECT status, COUNT(*) AS count
                FROM anime
                GROUP BY status
            """)
            status_rows = cur_status.fetchall()

            status_counts = {s: 0 for s in VALID_STATUSES}
            for row in status_rows:
                status_counts[row['status']] = row['count']

            total_anime = summary['total_anime'] or 0
            avg_rating = summary['average_rating']
            avg_rating_val = float(avg_rating) if avg_rating is not None else 0.0

            return {
                'total_anime': total_anime,
                'average_rating': avg_rating_val,
                'total_episodes_watched': summary['total_episodes_watched'] or 0,
                'total_favorites': summary['total_favorites'] or 0,
                'status_distribution': status_counts
            }
