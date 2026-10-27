import pytest

from review_board.validation import validate_new_review, validate_update


def form(**changes):
    values = {
        "case_reference": "CASE-1",
        "prediction": "Loan approved",
        "confidence": "0.5",
        "input_summary": "A short summary.",
    }
    values.update(changes)
    return values


def test_a_correct_form_has_no_errors():
    cleaned, errors = validate_new_review(form())
    assert errors == {}
    assert cleaned["confidence"] == 0.5
    assert cleaned["case_reference"] == "CASE-1"


@pytest.mark.parametrize("field", ["case_reference", "prediction", "input_summary", "confidence"])
def test_every_field_is_required(field):
    _, errors = validate_new_review(form(**{field: ""}))
    assert field in errors
    assert "required" in errors[field]


def test_spaces_only_count_as_empty():
    _, errors = validate_new_review(form(case_reference="   "))
    assert "case_reference" in errors


def test_spaces_around_a_value_are_removed():
    cleaned, errors = validate_new_review(form(case_reference="  CASE-9  "))
    assert errors == {}
    assert cleaned["case_reference"] == "CASE-9"


@pytest.mark.parametrize("value", ["0", "1", "0.0", "1.0", "0.85", "0,85"])
def test_confidence_between_0_and_1_is_accepted(value):
    cleaned, errors = validate_new_review(form(confidence=value))
    assert errors == {}
    assert 0 <= cleaned["confidence"] <= 1


@pytest.mark.parametrize("value", ["-0.01", "1.01", "2", "-1", "abc", "nan", "inf", "0.8.5"])
def test_confidence_outside_0_and_1_or_not_a_number_is_rejected(value):
    _, errors = validate_new_review(form(confidence=value))
    assert "between 0 and 1" in errors["confidence"]


def test_too_long_text_is_rejected():
    _, errors = validate_new_review(form(case_reference="x" * 101))
    assert "at most 100" in errors["case_reference"]


def test_all_problems_are_reported_together():
    _, errors = validate_new_review(
        {"case_reference": "", "prediction": "", "confidence": "9", "input_summary": ""}
    )
    assert set(errors) == {"case_reference", "prediction", "confidence", "input_summary"}


@pytest.mark.parametrize("decision", ["pending", "approved", "rejected"])
def test_the_three_decisions_are_allowed(decision):
    cleaned, errors = validate_update({"decision": decision, "notes": "ok"})
    assert errors == {}
    assert cleaned["decision"] == decision


@pytest.mark.parametrize("decision", ["", "maybe", "APPROVED", "approve"])
def test_other_decisions_are_rejected(decision):
    _, errors = validate_update({"decision": decision, "notes": ""})
    assert "pending, approved, rejected" in errors["decision"]


def test_notes_are_optional():
    cleaned, errors = validate_update({"decision": "approved"})
    assert errors == {}
    assert cleaned["notes"] == ""


def test_too_long_notes_are_rejected():
    _, errors = validate_update({"decision": "approved", "notes": "x" * 2001})
    assert "at most 2000" in errors["notes"]
