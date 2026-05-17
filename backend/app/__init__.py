from flask import Flask
from flask import request

from .api.comic import comic_bp
from .api.export import export_bp
from .api.health import health_bp
from .api.story import story_bp
from .config import load_dotenv


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    _register_local_cors(app)
    app.register_blueprint(comic_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(story_bp)
    return app


def _register_local_cors(app: Flask) -> None:
    @app.after_request
    def add_local_cors_headers(response):
        origin = request.headers.get("Origin", "")
        if origin in {"http://localhost:3000", "http://127.0.0.1:3000"}:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,OPTIONS"
        return response
