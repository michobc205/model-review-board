import pytest

from review_board import create_app, db
from review_board.models import Review


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


@pytest.fixture
def client(app):
    """A browser stand-in that talks to the app."""
    return app.test_client()


@pytest.fixture
def add_review(app):
    """Save a review in the test database and return its id."""

    def _add(**changes):
        values = {
            "case_reference": "CASE-1",
            "prediction": "Loan approved",
            "confidence": 0.9,
            "input_summary": "A short summary of the input.",
        }
        values.update(changes)
        with app.app_context():
            review = Review(**values)
            db.session.add(review)
            db.session.commit()
            return review.id

    return _add


@pytest.fixture
def get_review(app):
    """Read one review from the test database (or None)."""

    def _get(review_id):
        with app.app_context():
            return db.session.get(Review, review_id)

    return _get


@pytest.fixture
def count_reviews(app):
    """Count the reviews in the test database."""

    def _count():
        with app.app_context():
            return db.session.query(Review).count()

    return _count


VALID_FORM = {
    "case_reference": "CASE-2001",
    "prediction": "Flagged as fraud",
    "confidence": "0.75",
    "input_summary": "Two payments from two countries.",
}


@pytest.fixture
def valid_form():
    """A copy of a correct form for a new review."""
    return dict(VALID_FORM)
