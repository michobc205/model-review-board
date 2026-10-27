"""Checks of the files that decide what Render creates, and what it costs."""
import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def blueprint():
    return yaml.safe_load((ROOT / "render.yaml").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def web(blueprint):
    return blueprint["services"][0]


@pytest.fixture(scope="module")
def database(blueprint):
    return blueprint["databases"][0]


def env_var(web, key):
    matches = [item for item in web["envVars"] if item["key"] == key]
    assert len(matches) == 1, f"{key} must be defined exactly once"
    return matches[0]


def test_the_blueprint_has_one_web_service_and_one_database(blueprint):
    assert len(blueprint["services"]) == 1
    assert len(blueprint["databases"]) == 1
    assert blueprint["services"][0]["type"] == "web"


def test_the_web_service_uses_the_native_python_runtime(web):
    assert web["runtime"] == "python"


def test_both_plans_are_free_and_written_down(web, database):
    # If a plan is left out, Render may choose a paid one.
    assert web["plan"] == "free"
    assert database["plan"] == "free"


def test_the_service_and_the_database_are_in_the_same_region(web, database):
    assert web["region"] == database["region"]


def test_the_build_command_installs_the_requirements(web):
    assert web["buildCommand"] == "pip install -r requirements.txt"


def test_the_start_command_creates_the_tables_and_then_starts_gunicorn(web):
    command = web["startCommand"]
    assert command.index("init-db") < command.index("gunicorn")
    assert "&&" in command


def test_the_start_command_listens_on_the_port_that_render_gives(web):
    assert "--bind 0.0.0.0:$PORT" in web["startCommand"]


def test_the_start_command_names_an_app_factory_that_exists(web):
    from review_board import create_app

    assert "review_board:create_app()" in web["startCommand"]
    assert callable(create_app)


def test_the_health_check_path_is_the_health_route(web):
    assert web["healthCheckPath"] == "/health"


def test_database_url_comes_from_the_database_and_is_never_written_down(web, database):
    item = env_var(web, "DATABASE_URL")
    assert "value" not in item
    assert item["fromDatabase"]["name"] == database["name"]
    assert item["fromDatabase"]["property"] == "connectionString"


def test_secret_key_is_generated_and_never_written_down(web):
    item = env_var(web, "SECRET_KEY")
    assert item.get("generateValue") is True
    assert "value" not in item


def test_the_python_version_is_a_full_version(web):
    assert re.fullmatch(r"\d+\.\d+\.\d+", str(env_var(web, "PYTHON_VERSION")["value"]))


def test_no_environment_variable_with_a_secret_name_has_a_written_value(web):
    for item in web["envVars"]:
        if re.search(r"SECRET|PASSWORD|TOKEN|URL|KEY", item["key"]):
            assert "value" not in item, f"{item['key']} must not have a written value"


def test_the_blueprint_contains_no_connection_string():
    text = (ROOT / "render.yaml").read_text(encoding="utf-8")
    assert "postgres://" not in text
    assert "postgresql://" not in text


def test_the_project_has_no_docker_files_and_no_docker_runtime(web):
    assert web["runtime"] != "docker"
    for name in ("Dockerfile", "docker-compose.yaml", "docker-compose.yml", ".dockerignore"):
        assert not (ROOT / name).exists(), f"{name} must not exist"


def test_gitignore_keeps_secrets_and_database_files_out():
    lines = [line.strip() for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()]
    assert ".env" in lines
    assert "*.db" in lines


def test_env_example_has_only_placeholders():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    values = dict(
        line.split("=", 1) for line in text.splitlines() if "=" in line and not line.startswith("#")
    )
    assert values["DATABASE_URL"].startswith("sqlite:///")
    assert "change-me" in values["SECRET_KEY"]
    assert "postgres" not in text


def test_the_requirements_have_the_deployment_packages():
    text = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "gunicorn" in text
    assert "psycopg" in text
    assert "flask-sqlalchemy" in text
