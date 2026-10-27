"""The database model: one table, `review`."""
from datetime import datetime, timezone

from . import db


def utc_now() -> datetime:
    """The current time in UTC."""
    return datetime.now(timezone.utc)


class Review(db.Model):
    """One review of one model prediction."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    DECISIONS = (PENDING, APPROVED, REJECTED)

    id = db.Column(db.Integer, primary_key=True)
    case_reference = db.Column(db.String(100), nullable=False)
    prediction = db.Column(db.String(200), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    input_summary = db.Column(db.Text, nullable=False)
    decision = db.Column(db.String(20), nullable=False, default=PENDING)
    notes = db.Column(db.Text, nullable=False, default="")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )

    def __repr__(self) -> str:
        return f"<Review {self.id} {self.case_reference} {self.decision}>"
