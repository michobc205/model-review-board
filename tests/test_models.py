from review_board import db
from review_board.models import Review


def make_review(**changes):
    values = {
        "case_reference": "CASE-1",
        "prediction": "Loan approved",
        "confidence": 0.9,
        "input_summary": "A short summary of the input.",
    }
    values.update(changes)
    return Review(**values)


def test_the_allowed_decisions():
    assert Review.DECISIONS == ("pending", "approved", "rejected")


def test_a_saved_review_can_be_read_back(app):
    with app.app_context():
        db.session.add(make_review())
        db.session.commit()
        review = db.session.get(Review, 1)
        assert review.case_reference == "CASE-1"
        assert review.prediction == "Loan approved"
        assert review.confidence == 0.9


def test_a_new_review_starts_as_pending_with_empty_notes(app):
    with app.app_context():
        db.session.add(make_review())
        db.session.commit()
        review = db.session.get(Review, 1)
        assert review.decision == "pending"
        assert review.notes == ""


def test_a_new_review_has_both_dates(app):
    with app.app_context():
        db.session.add(make_review())
        db.session.commit()
        review = db.session.get(Review, 1)
        assert review.created_at is not None
        assert review.updated_at is not None


def test_changing_a_review_updates_the_date(app):
    with app.app_context():
        db.session.add(make_review())
        db.session.commit()
        review = db.session.get(Review, 1)
        first = review.updated_at
        review.decision = "approved"
        review.notes = "Looks right."
        db.session.commit()
        db.session.refresh(review)
        assert review.decision == "approved"
        assert review.updated_at >= first
