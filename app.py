import os
from flask import Flask, render_template, jsonify
from config import Config, DevelopmentConfig, TestingConfig
from models.anime import init_db
from routes.anime_routes import anime_bp


def create_app(test_config=None) -> Flask:
    """Application factory for AniTrack."""
    app = Flask(__name__, static_folder='static', template_folder='templates')

    if test_config is None:
        env = os.environ.get('FLASK_ENV', 'development')
        if env == 'testing':
            app.config.from_object(TestingConfig)
        else:
            app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_mapping(test_config)

    # Initialize SQLite database automatically
    with app.app_context():
        db_path = app.config['DATABASE']
        seed_data = not app.config.get('TESTING', False)
        init_db(db_path, seed=seed_data)

    # Register blueprints
    app.register_blueprint(anime_bp)

    @app.route('/')
    def index():
        """Render the main AniTrack dashboard."""
        return render_template('index.html')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    print("=" * 60)
    print(f" AniTrack Anime Watchlist running on: http://127.0.0.1:{port}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=port, debug=True)
