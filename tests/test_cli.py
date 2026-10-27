from sqlalchemy import inspect

from review_board import create_app, db
from review_board.models import Review


def test_init_db_creates_the_review_table(tmp_path):
    app = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'new.db'}"}
    )
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert result.exit_code == 0
    assert "Initialized" in result.output
    with app.app_context():
        assert "review" in inspect(db.engine).get_table_names()
        db.engine.dispose()


def test_init_db_can_run_twice(app):
    runner = app.test_cli_runner()
    assert runner.invoke(args=["init-db"]).exit_code == 0
    assert runner.invoke(args=["init-db"]).exit_code == 0


def test_seed_db_adds_three_reviews_once(app):
    runner = app.test_cli_runner()
    first = runner.invoke(args=["seed-db"])
    assert "Added 3" in first.output
    second = runner.invoke(args=["seed-db"])
    assert "already has reviews" in second.output
    with app.app_context():
        assert db.session.query(Review).count() == 3
