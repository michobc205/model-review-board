"""The pages of the app. Only POST requests change data."""
from flask import (
    Blueprint,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func, text
from sqlalchemy.exc import SQLAlchemyError

from . import db
from .models import Review
from .validation import validate_new_review, validate_update

bp = Blueprint("main", __name__)


@bp.get("/")
def dashboard():
    """All reviews, newest first, and the number of reviews per decision."""
    reviews = db.session.scalars(
        db.select(Review).order_by(Review.created_at.desc(), Review.id.desc())
    ).all()
    counts = dict(
        db.session.execute(
            db.select(Review.decision, func.count()).group_by(Review.decision)
        ).all()
    )
    totals = {decision: counts.get(decision, 0) for decision in Review.DECISIONS}
    totals["all"] = len(reviews)
    return render_template("index.html", reviews=reviews, totals=totals)


@bp.route("/reviews/new", methods=["GET", "POST"])
def new_review():
    """GET shows the empty form. POST checks it and saves a new review."""
    if request.method == "POST":
        cleaned, errors = validate_new_review(request.form)
        if errors:
            return render_template("new.html", errors=errors, values=request.form), 400
        review = Review(**cleaned)
        db.session.add(review)
        db.session.commit()
        flash(f"Review {review.case_reference} was created.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("new.html", errors={}, values={})


@bp.route("/reviews/<int:review_id>/edit", methods=["GET", "POST"])
def edit_review(review_id):
    """GET shows the form. POST saves the new decision and notes."""
    review = db.get_or_404(Review, review_id)
    if request.method == "POST":
        cleaned, errors = validate_update(request.form)
        if errors:
            return (
                render_template("edit.html", review=review, errors=errors, values=request.form),
                400,
            )
        review.decision = cleaned["decision"]
        review.notes = cleaned["notes"]
        db.session.commit()
        flash(f"Review {review.case_reference} was updated.", "success")
        return redirect(url_for("main.dashboard"))
    values = {"decision": review.decision, "notes": review.notes}
    return render_template("edit.html", review=review, errors={}, values=values)


@bp.route("/reviews/<int:review_id>/delete", methods=["GET", "POST"])
def delete_review(review_id):
    """GET asks "are you sure?" and deletes nothing. POST deletes the review."""
    review = db.get_or_404(Review, review_id)
    if request.method == "POST":
        reference = review.case_reference
        db.session.delete(review)
        db.session.commit()
        flash(f"Review {reference} was deleted.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("confirm_delete.html", review=review)


@bp.get("/health")
def health():
    """200 if the database answers, 503 if it does not."""
    try:
        db.session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Health check failed: the database is not reachable.")
        return jsonify(status="error", database="unreachable"), 503
    return jsonify(status="ok", database="ok")
