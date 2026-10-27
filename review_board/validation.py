"""Checks of the form data. Each function returns (clean values, errors)."""
import math

from .models import Review

MAX_CASE_REFERENCE = 100
MAX_PREDICTION = 200
MAX_INPUT_SUMMARY = 1000
MAX_NOTES = 2000


def _text(form, name):
    """The value of a form field, without spaces at the start and the end."""
    return (form.get(name) or "").strip()


def validate_new_review(form):
    """Check the form for a new review: case reference, prediction, confidence, summary."""
    cleaned, errors = {}, {}

    required_texts = (
        ("case_reference", "Case reference", MAX_CASE_REFERENCE),
        ("prediction", "Prediction", MAX_PREDICTION),
        ("input_summary", "Input summary", MAX_INPUT_SUMMARY),
    )
    for field, label, max_length in required_texts:
        value = _text(form, field)
        if not value:
            errors[field] = f"{label} is required."
        elif len(value) > max_length:
            errors[field] = f"{label} must have at most {max_length} characters."
        else:
            cleaned[field] = value

    raw = _text(form, "confidence")
    if not raw:
        errors["confidence"] = "Confidence is required."
    else:
        try:
            number = float(raw.replace(",", "."))
        except ValueError:
            number = None
        if number is None or not math.isfinite(number) or not 0 <= number <= 1:
            errors["confidence"] = (
                "Confidence must be a number between 0 and 1, for example 0.85."
            )
        else:
            cleaned["confidence"] = number

    return cleaned, errors


def validate_update(form):
    """Check the form that changes a review: the decision and the notes."""
    cleaned, errors = {}, {}

    decision = _text(form, "decision")
    if decision not in Review.DECISIONS:
        errors["decision"] = "Decision must be one of: " + ", ".join(Review.DECISIONS) + "."
    else:
        cleaned["decision"] = decision

    notes = _text(form, "notes")
    if len(notes) > MAX_NOTES:
        errors["notes"] = f"Notes must have at most {MAX_NOTES} characters."
    else:
        cleaned["notes"] = notes

    return cleaned, errors
