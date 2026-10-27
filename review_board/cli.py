"""Commands for the `flask` program: initialize and fill the database."""
import click

from . import db
from .models import Review

SAMPLE_REVIEWS = [
    {
        "case_reference": "CASE-1001",
        "prediction": "Loan approved",
        "confidence": 0.91,
        "input_summary": "Applicant with stable income, four years at the same employer.",
    },
    {
        "case_reference": "CASE-1002",
        "prediction": "Flagged as fraud",
        "confidence": 0.67,
        "input_summary": "Three card payments in two countries within one hour.",
    },
    {
        "case_reference": "CASE-1003",
        "prediction": "Low risk",
        "confidence": 0.98,
        "input_summary": "Repeat customer, no late payments in 24 months.",
        "decision": Review.APPROVED,
        "notes": "Checked against the account history.",
    },
]


def register_commands(app):
    """Add the commands to the app: `flask --app review_board init-db` and `seed-db`."""

    @app.cli.command("init-db")
    def init_db():
        """Create the database tables (safe to run again)."""
        db.create_all()
        click.echo("Initialized the database.")

    @app.cli.command("seed-db")
    def seed_db():
        """Add three sample reviews, but only if the table is empty."""
        if db.session.query(Review).count() > 0:
            click.echo("The database already has reviews. Nothing added.")
            return
        db.session.add_all(Review(**data) for data in SAMPLE_REVIEWS)
        db.session.commit()
        click.echo(f"Added {len(SAMPLE_REVIEWS)} sample reviews.")
