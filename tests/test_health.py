from review_board import create_app


def test_health_is_ok_when_the_database_answers(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "ok"}


def test_health_gives_an_error_status_when_the_database_cannot_be_reached(tmp_path):
    # The folder does not exist, so SQLite cannot open the file.
    broken = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'missing' / 'x.db'}"}
    )
    response = broken.test_client().get("/health")
    assert response.status_code == 503
    assert response.get_json() == {"status": "error", "database": "unreachable"}


def test_health_does_not_show_the_database_address(tmp_path):
    broken = create_app(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'missing' / 'x.db'}"}
    )
    text = broken.test_client().get("/health").get_data(as_text=True)
    assert "sqlite" not in text and "missing" not in text
