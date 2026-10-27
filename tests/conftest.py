import pytest

from review_board import create_app, db


@pytest.fixture
def app(tmp_path):
    """A fresh app with an empty SQLite file in a temporary folder."""
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}",
        }
    )
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()
