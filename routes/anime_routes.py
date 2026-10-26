from flask import Blueprint, current_app, request, jsonify
from models.anime import AnimeModel, validate_anime_data, VALID_STATUSES
from services.jikan_service import JikanService

anime_bp = Blueprint('anime_api', __name__, url_prefix='')


def get_db_path() -> str:
    """Retrieve active database path from Flask app config."""
    return current_app.config['DATABASE']


@anime_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify service and database availability."""
    try:
        db_path = get_db_path()
        stats = AnimeModel.get_stats(db_path)
        return jsonify({
            'status': 'healthy',
            'service': 'AniTrack API',
            'database': 'connected',
            'total_tracked': stats['total_anime']
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@anime_bp.route('/api/search-anime', methods=['GET'])
def search_anime_external():
    """
    Search external anime data via Jikan (MyAnimeList).
    Query parameter: q=<anime_title>
    Returns normalized JSON with poster, community ratings, episode counts, etc.
    """
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({
            'success': False,
            'error': 'Missing required query parameter "q".'
        }), 400

    if len(query) > 100:
        return jsonify({
            'success': False,
            'error': 'Search query is too long (maximum 100 characters).'
        }), 400

    try:
        limit = min(int(request.args.get('limit', 10)), 20)
    except (ValueError, TypeError):
        limit = 10

    result = JikanService.search(query, limit=limit)
    status_code = 200 if result.get('success') else (503 if 'unreachable' in result.get('error', '').lower() else 400)
    return jsonify(result), status_code


@anime_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Return dashboard analytics and status distribution."""
    try:
        db_path = get_db_path()
        stats = AnimeModel.get_stats(db_path)
        return jsonify({
            'success': True,
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Failed to calculate stats: {str(e)}"
        }), 500


@anime_bp.route('/api/anime', methods=['GET'])
def get_anime_list():
    """
    List anime items with optional filtering, searching, and sorting.
    Query params: status, search, sort_by, sort_order, favorite
    """
    try:
        db_path = get_db_path()
        status = request.args.get('status')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'title')
        sort_order = request.args.get('sort_order', 'asc')
        fav_param = request.args.get('favorite')

        is_favorite = None
        if fav_param is not None and fav_param != '':
            is_favorite = fav_param.lower() in ('1', 'true', 'yes')

        if status and status not in VALID_STATUSES and status.lower() != 'all':
            return jsonify({
                'success': False,
                'error': f"Invalid status filter. Must be one of: {', '.join(VALID_STATUSES)} or 'all'."
            }), 400

        filter_status = None if (not status or status.lower() == 'all') else status

        anime_list = AnimeModel.get_all(
            db_path=db_path,
            status=filter_status,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            is_favorite=is_favorite
        )

        return jsonify({
            'success': True,
            'count': len(anime_list),
            'data': anime_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Failed to fetch anime list: {str(e)}"
        }), 500


@anime_bp.route('/api/anime/<int:anime_id>', methods=['GET'])
def get_anime_detail(anime_id: int):
    """Fetch details for a single anime record."""
    try:
        db_path = get_db_path()
        item = AnimeModel.get_by_id(db_path, anime_id)
        if not item:
            return jsonify({
                'success': False,
                'error': f"Anime with id {anime_id} not found."
            }), 404

        return jsonify({
            'success': True,
            'data': item
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Failed to retrieve anime: {str(e)}"
        }), 500


@anime_bp.route('/api/anime', methods=['POST'])
def create_anime():
    """Create a new anime entry in the tracker."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            'success': False,
            'error': 'Missing or invalid JSON payload.'
        }), 400

    is_valid, errors, cleaned = validate_anime_data(data, is_update=False)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'errors': errors
        }), 400

    try:
        db_path = get_db_path()
        created = AnimeModel.create(db_path, cleaned)
        return jsonify({
            'success': True,
            'message': f"'{created['title']}' added to your watchlist!",
            'data': created
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Database insertion failed: {str(e)}"
        }), 500


@anime_bp.route('/api/anime/<int:anime_id>', methods=['PUT'])
def update_anime(anime_id: int):
    """Update an existing anime entry."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            'success': False,
            'error': 'Missing or invalid JSON payload.'
        }), 400

    db_path = get_db_path()
    existing = AnimeModel.get_by_id(db_path, anime_id)
    if not existing:
        return jsonify({
            'success': False,
            'error': f"Anime with id {anime_id} not found."
        }), 404

    is_valid, errors, cleaned = validate_anime_data(data, is_update=True)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'errors': errors
        }), 400

    try:
        updated = AnimeModel.update(db_path, anime_id, cleaned)
        return jsonify({
            'success': True,
            'message': f"'{updated['title']}' updated successfully!",
            'data': updated
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Database update failed: {str(e)}"
        }), 500


@anime_bp.route('/api/anime/<int:anime_id>', methods=['DELETE'])
def delete_anime(anime_id: int):
    """Delete an anime entry from the watchlist."""
    try:
        db_path = get_db_path()
        existing = AnimeModel.get_by_id(db_path, anime_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': f"Anime with id {anime_id} not found."
            }), 404

        deleted = AnimeModel.delete(db_path, anime_id)
        if deleted:
            return jsonify({
                'success': True,
                'message': f"'{existing['title']}' was removed from your watchlist.",
                'id': anime_id
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': "Failed to delete record."
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Database error during deletion: {str(e)}"
        }), 500


@anime_bp.route('/api/anime/<int:anime_id>/favorite', methods=['PATCH'])
def toggle_favorite_route(anime_id: int):
    """Toggle favorite status for an anime."""
    try:
        db_path = get_db_path()
        updated = AnimeModel.toggle_favorite(db_path, anime_id)
        if not updated:
            return jsonify({
                'success': False,
                'error': f"Anime with id {anime_id} not found."
            }), 404

        status_text = "added to" if updated['is_favorite'] else "removed from"
        return jsonify({
            'success': True,
            'message': f"'{updated['title']}' {status_text} favorites.",
            'data': updated
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Failed to toggle favorite: {str(e)}"
        }), 500


@anime_bp.route('/api/anime/<int:anime_id>/progress', methods=['PATCH'])
def progress_anime(anime_id: int):
    """Increment or decrement episode progress."""
    data = request.get_json(silent=True) or {}
    delta = data.get('delta', 1)
    try:
        delta = int(delta)
    except (ValueError, TypeError):
        delta = 1

    try:
        db_path = get_db_path()
        updated = AnimeModel.increment_episode(db_path, anime_id, delta)
        if not updated:
            return jsonify({
                'success': False,
                'error': f"Anime with id {anime_id} not found."
            }), 404

        return jsonify({
            'success': True,
            'message': f"Progress updated: {updated['episodes_watched']}/{updated['total_episodes']}",
            'data': updated
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Failed to update episode progress: {str(e)}"
        }), 500
