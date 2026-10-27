from review_board.config import (
    DEFAULT_DATABASE_URL,
    get_database_url,
    normalize_database_url,
)


def test_default_is_a_local_sqlite_file():
    assert get_database_url({}) == DEFAULT_DATABASE_URL
    assert DEFAULT_DATABASE_URL.startswith("sqlite:///")


def test_an_empty_database_url_falls_back_to_sqlite():
    assert get_database_url({"DATABASE_URL": ""}) == DEFAULT_DATABASE_URL


def test_database_url_from_the_environment_is_used():
    assert get_database_url({"DATABASE_URL": "sqlite:///other.db"}) == "sqlite:///other.db"


def test_postgresql_url_gets_the_psycopg_driver():
    url = "postgresql://user:pw@host:5432/db"
    assert normalize_database_url(url) == "postgresql+psycopg://user:pw@host:5432/db"


def test_old_postgres_scheme_is_fixed_too():
    url = "postgres://user:pw@host/db"
    assert normalize_database_url(url) == "postgresql+psycopg://user:pw@host/db"


def test_url_with_a_driver_stays_as_it_is():
    url = "postgresql+psycopg://user:pw@host/db"
    assert normalize_database_url(url) == url
