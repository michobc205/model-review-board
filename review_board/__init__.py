"""Model Review Board: a small Flask app that stores reviews of model predictions."""
import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from .config import get_database_url

db = SQLAlchemy()


def create_app(test_config=None):
    """Create the app. Pass `test_config` (a dict) to override settings in tests."""
    app = Flask(__name__)
    app.config.from_mapping(
        # Local development only. On Render, SECRET_KEY comes from the environment.
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-not-a-secret"),
        SQLALCHEMY_DATABASE_URI=get_database_url(),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    from . import models  # noqa: F401  (registers the Review table)
    from .cli import register_commands

    from .routes import bp

    app.register_blueprint(bp)
    register_commands(app)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    return app
