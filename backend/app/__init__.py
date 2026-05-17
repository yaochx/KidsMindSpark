from flask import Flask

from .api.comic import comic_bp
from .api.export import export_bp
from .api.health import health_bp
from .api.story import story_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(comic_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(story_bp)
    return app
