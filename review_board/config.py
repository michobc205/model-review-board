"""Settings of the app, read from environment variables."""
import os

DEFAULT_DATABASE_URL = "sqlite:///review_board.db"


def normalize_database_url(url: str) -> str:
    """Make a database URL work with the `psycopg` driver.

    Render and other hosts hand out URLs that start with `postgres://` or
    `postgresql://`. SQLAlchemy needs `postgresql+psycopg://` for the driver
    that this project installs. SQLite and other URLs stay as they are.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


def get_database_url(env=None) -> str:
    """Return the database URL: `DATABASE_URL` if set, else a local SQLite file."""
    env = os.environ if env is None else env
    return normalize_database_url(env.get("DATABASE_URL") or DEFAULT_DATABASE_URL)
