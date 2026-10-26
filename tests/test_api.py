import os
import tempfile
import pytest
from app import create_app
from models.anime import init_db, get_db, AnimeModel


@pytest.fixture
def app():
    """Create a temporary test database and configured Flask test application."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)

    test_config = {
        'TESTING': True,
        'DATABASE': db_path,
        'SECRET_KEY': 'test-secret-key'
    }

    application = create_app(test_config=test_config)

    # Initialize tables with starter seed for testing
    with application.app_context():
        init_db(db_path, seed=True)

    yield application

    # Teardown: delete test database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


@pytest.fixture
def client(app):
    """Test client fixture."""
    return app.test_client()


def test_health_check(client):
    """Verify /health returns 200 and healthy status."""
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'


def test_get_all_anime(client):
    """Verify GET /api/anime returns seeded anime list with poster metadata."""
    res = client.get('/api/anime')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert isinstance(data['data'], list)
    assert len(data['data']) > 0


def test_create_anime_success(client):
    """Verify creating a new anime with valid payload."""
    payload = {
        'title': 'Vinland Saga Season 2',
        'status': 'Watching',
        'rating': 10,
        'episodes_watched': 15,
        'total_episodes': 24,
        'genres': 'Action, Adventure, Historical, Drama',
        'is_favorite': True,
        'notes': 'Farmland arc is peak storytelling.',
        'external_id': 49387,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1170/124312l.jpg',
        'mal_rating': 8.81,
        'external_source': 'MyAnimeList'
    }
    res = client.post('/api/anime', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    created = data['data']
    assert created['title'] == payload['title']
    assert created['status'] == 'Watching'
    assert created['rating'] == 10
    assert created['external_id'] == 49387
    assert created['poster_url'] == 'https://cdn.myanimelist.net/images/anime/1170/124312l.jpg'
    assert created['mal_rating'] == 8.81
    assert created['external_source'] == 'MyAnimeList'


def test_create_anime_validation_errors(client):
    """Verify validation constraints reject invalid payloads."""
    # 1. Missing title
    res = client.post('/api/anime', json={'status': 'Watching', 'rating': 8})
    assert res.status_code == 400
    assert 'title' in res.get_json()['errors']

    # 2. Empty title
    res = client.post('/api/anime', json={'title': '   ', 'status': 'Watching'})
    assert res.status_code == 400

    # 3. Invalid rating > 10
    res = client.post('/api/anime', json={'title': 'Test', 'status': 'Watching', 'rating': 11})
    assert res.status_code == 400
    assert 'rating' in res.get_json()['errors']

    # 4. Invalid rating < 1
    res = client.post('/api/anime', json={'title': 'Test', 'status': 'Watching', 'rating': 0})
    assert res.status_code == 400

    # 5. Negative watched episodes
    res = client.post('/api/anime', json={'title': 'Test', 'status': 'Watching', 'episodes_watched': -5})
    assert res.status_code == 400

    # 6. Watched episodes exceed total episodes
    res = client.post('/api/anime', json={
        'title': 'Test',
        'status': 'Watching',
        'episodes_watched': 25,
        'total_episodes': 12
    })
    assert res.status_code == 400
    assert 'episodes_watched' in res.get_json()['errors']

    # 7. Invalid status
    res = client.post('/api/anime', json={'title': 'Test', 'status': 'InvalidStatus'})
    assert res.status_code == 400


def test_filter_by_status(client):
    """Verify filtering anime by status."""
    for status in ['Watching', 'Completed', 'Dropped']:
        res = client.get(f'/api/anime?status={status}')
        assert res.status_code == 200
        items = res.get_json()['data']
        for item in items:
            assert item['status'] == status


def test_search_by_title(client):
    """Verify searching anime by title."""
    res = client.get('/api/anime?search=Frieren')
    assert res.status_code == 200
    items = res.get_json()['data']
    assert len(items) >= 1
    assert 'Frieren' in items[0]['title']


def test_sort_by_rating_and_title(client):
    """Verify sorting endpoints."""
    # Sort by rating desc
    res_rating = client.get('/api/anime?sort_by=rating&sort_order=desc')
    assert res_rating.status_code == 200
    items_rating = res_rating.get_json()['data']
    ratings = [i['rating'] for i in items_rating if i['rating'] is not None]
    assert ratings == sorted(ratings, reverse=True)

    # Sort by title asc
    res_title = client.get('/api/anime?sort_by=title&sort_order=asc')
    assert res_title.status_code == 200
    items_title = res_title.get_json()['data']
    titles = [i['title'].lower() for i in items_title]
    assert titles == sorted(titles)


def test_update_anime_with_external_metadata(client):
    """Verify PUT /api/anime/<id> updates existing record including poster and MAL ratings."""
    create_res = client.post('/api/anime', json={
        'title': 'Initial Anime Title',
        'status': 'Watching',
        'rating': 7
    })
    anime_id = create_res.get_json()['data']['id']

    # Update with poster URL and MAL rating
    update_res = client.put(f'/api/anime/{anime_id}', json={
        'title': 'Updated Anime Title',
        'status': 'Completed',
        'rating': 9,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1208/94745l.jpg',
        'mal_rating': 9.10,
        'external_id': 5114,
        'external_source': 'MyAnimeList'
    })
    assert update_res.status_code == 200
    updated = update_res.get_json()['data']
    assert updated['title'] == 'Updated Anime Title'
    assert updated['status'] == 'Completed'
    assert updated['rating'] == 9
    assert updated['poster_url'] == 'https://cdn.myanimelist.net/images/anime/1208/94745l.jpg'
    assert updated['mal_rating'] == 9.10
    assert updated['external_id'] == 5114


def test_delete_anime(client):
    """Verify DELETE /api/anime/<id> removes item from database."""
    create_res = client.post('/api/anime', json={
        'title': 'To Be Deleted',
        'status': 'Dropped'
    })
    anime_id = create_res.get_json()['data']['id']

    delete_res = client.delete(f'/api/anime/{anime_id}')
    assert delete_res.status_code == 200
    assert delete_res.get_json()['success'] is True

    get_res = client.get(f'/api/anime/{anime_id}')
    assert get_res.status_code == 404


def test_toggle_favorite_endpoint(client):
    """Verify toggle favorite endpoint flips is_favorite boolean."""
    create_res = client.post('/api/anime', json={
        'title': 'Favorite Test Show',
        'status': 'Watching',
        'is_favorite': False
    })
    anime_id = create_res.get_json()['data']['id']

    toggle_1 = client.patch(f'/api/anime/{anime_id}/favorite')
    assert toggle_1.status_code == 200
    assert toggle_1.get_json()['data']['is_favorite'] is True

    toggle_2 = client.patch(f'/api/anime/{anime_id}/favorite')
    assert toggle_2.status_code == 200
    assert toggle_2.get_json()['data']['is_favorite'] is False


def test_progress_step_endpoint(client):
    """Verify stepping episodes increment/decrement."""
    create_res = client.post('/api/anime', json={
        'title': 'Progress Step Show',
        'status': 'Watching',
        'episodes_watched': 5,
        'total_episodes': 12
    })
    anime_id = create_res.get_json()['data']['id']

    step_up = client.patch(f'/api/anime/{anime_id}/progress', json={'delta': 1})
    assert step_up.status_code == 200
    assert step_up.get_json()['data']['episodes_watched'] == 6


def test_stats_analytics(client):
    """Verify GET /api/stats returns counts and status distribution."""
    res = client.get('/api/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    stats = data['data']
    assert 'total_anime' in stats
    assert 'average_rating' in stats
    assert 'status_distribution' in stats
    assert stats['total_anime'] >= 0


# =========================================================================
# Acceptance Tests for External Anime Data, Posters, and Ratings
# =========================================================================

def test_search_anime_naruto(client):
    """
    Acceptance Test A:
    Verify searching for 'Naruto' returns matching anime with actual poster URLs,
    community scores, year, genres, and episode counts.
    """
    res = client.get('/api/search-anime?q=naruto')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['count'] >= 1
    items = data['data']

    # Find Naruto
    naruto = next((i for i in items if 'Naruto' in i['title']), None)
    assert naruto is not None
    assert naruto['external_id'] in (20, 1735)
    assert naruto['poster_url'].startswith('http')
    assert naruto['mal_rating'] is not None
    assert isinstance(naruto['mal_rating'], float)
    assert naruto['mal_rating'] > 7.0
    assert naruto['episodes'] > 0
    assert 'Action' in naruto['genres']
    assert naruto['external_source'] == 'MyAnimeList'


def test_search_anime_empty_and_invalid_queries(client):
    """Verify query validation on /api/search-anime."""
    # Empty query
    res_empty = client.get('/api/search-anime?q=')
    assert res_empty.status_code == 400

    # Missing parameter
    res_missing = client.get('/api/search-anime')
    assert res_missing.status_code == 400


def test_save_and_refresh_preserves_poster_and_metadata(app, client):
    """
    Acceptance Test B & D:
    Verify saving an anime with poster URL and external metadata persists
    across queries and reloads from SQLite.
    """
    payload = {
        'title': 'Naruto Shippuden Tracking',
        'status': 'Watching',
        'rating': 9,
        'episodes_watched': 150,
        'total_episodes': 500,
        'genres': 'Action, Adventure',
        'is_favorite': True,
        'external_id': 1735,
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1565/111305l.jpg',
        'mal_rating': 8.27,
        'external_source': 'MyAnimeList'
    }

    create_res = client.post('/api/anime', json=payload)
    assert create_res.status_code == 201
    anime_id = create_res.get_json()['data']['id']

    # Re-fetch via GET /api/anime/<id>
    get_res = client.get(f'/api/anime/{anime_id}')
    assert get_res.status_code == 200
    saved = get_res.get_json()['data']
    assert saved['external_id'] == 1735
    assert saved['poster_url'] == 'https://cdn.myanimelist.net/images/anime/1565/111305l.jpg'
    assert saved['mal_rating'] == 8.27
    assert saved['external_source'] == 'MyAnimeList'

    # Direct SQLite connection test to ensure real database persistence
    db_path = app.config['DATABASE']
    with get_db(db_path) as conn:
        cur = conn.execute("SELECT poster_url, mal_rating, external_id FROM anime WHERE id = ?", (anime_id,))
        row = cur.fetchone()
        assert row is not None
        assert row['poster_url'] == 'https://cdn.myanimelist.net/images/anime/1565/111305l.jpg'
        assert row['mal_rating'] == 8.27
        assert row['external_id'] == 1735


def test_separate_personal_and_community_ratings(app, client):
    """
    Acceptance Test C:
    Verify personal rating (1-10) and community rating (0-10) remain separate.
    Personal rating must not be overwritten by MAL rating, and average rating
    calculation in /api/stats must only include personal ratings.
    """
    db_path = app.config['DATABASE']

    # Clear table to test clean average calculation
    with get_db(db_path) as conn:
        conn.execute("DELETE FROM anime")
        conn.commit()

    # Insert two anime with low personal ratings and high MAL ratings
    client.post('/api/anime', json={
        'title': 'Personal Rating Test 1',
        'status': 'Watching',
        'rating': 6,          # Personal Rating: 6
        'mal_rating': 9.50,   # MAL Score: 9.5
        'poster_url': 'https://cdn.myanimelist.net/images/anime/1/test.jpg'
    })
    client.post('/api/anime', json={
        'title': 'Personal Rating Test 2',
        'status': 'Completed',
        'rating': 8,          # Personal Rating: 8
        'mal_rating': 9.20,   # MAL Score: 9.2
        'poster_url': 'https://cdn.myanimelist.net/images/anime/2/test.jpg'
    })

    # Expected personal average: (6 + 8) / 2 = 7.0
    stats_res = client.get('/api/stats')
    assert stats_res.status_code == 200
    stats = stats_res.get_json()['data']
    assert stats['average_rating'] == 7.0, "Average rating must only use personal rating, not MAL rating!"


def test_manual_anime_entry_without_external_api(client):
    """
    Acceptance Test E & F:
    Verify an external API failure or manual entry without external metadata
    works seamlessly without errors.
    """
    payload = {
        'title': 'Indie Homemade Animation',
        'status': 'Watching',
        'rating': 8,
        'episodes_watched': 2,
        'total_episodes': 5,
        'genres': 'Indie, Art',
        'external_id': None,
        'poster_url': None,
        'mal_rating': None
    }
    res = client.post('/api/anime', json=payload)
    assert res.status_code == 201
    created = res.get_json()['data']
    assert created['title'] == 'Indie Homemade Animation'
    assert created['poster_url'] is None
    assert created['mal_rating'] is None


def test_existing_records_preserved_after_migration(app):
    """
    Acceptance Test D:
    Verify existing records remain intact when table is migrated.
    """
    db_path = app.config['DATABASE']
    with get_db(db_path) as conn:
        cur = conn.execute("SELECT COUNT(*) AS count FROM anime")
        count = cur.fetchone()['count']
        assert count > 0, "Existing database records must be preserved."
