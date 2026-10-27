def test_the_create_form_opens(client):
    response = client.get("/reviews/new")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    for field in ("case_reference", "prediction", "confidence", "input_summary"):
        assert f'name="{field}"' in html


def test_a_valid_form_creates_a_review(client, valid_form, count_reviews, get_review):
    response = client.post("/reviews/new", data=valid_form)
    assert response.status_code == 302
    assert count_reviews() == 1
    review = get_review(1)
    assert review.case_reference == "CASE-2001"
    assert review.confidence == 0.75
    assert review.decision == "pending"
    assert review.notes == ""


def test_after_creating_the_dashboard_shows_the_review(client, valid_form):
    response = client.post("/reviews/new", data=valid_form, follow_redirects=True)
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Review CASE-2001 was created." in html
    assert "Flagged as fraud" in html


def test_an_empty_form_is_rejected_with_messages(client, count_reviews):
    response = client.post("/reviews/new", data={})
    html = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "The review was not saved." in html
    assert "Case reference is required." in html
    assert "Prediction is required." in html
    assert "Confidence is required." in html
    assert "Input summary is required." in html
    assert count_reviews() == 0


def test_confidence_outside_the_range_is_rejected(client, valid_form, count_reviews):
    valid_form["confidence"] = "1.5"
    response = client.post("/reviews/new", data=valid_form)
    assert response.status_code == 400
    assert "between 0 and 1" in response.get_data(as_text=True)
    assert count_reviews() == 0


def test_a_rejected_form_keeps_what_the_user_typed(client, valid_form):
    valid_form["confidence"] = "abc"
    html = client.post("/reviews/new", data=valid_form).get_data(as_text=True)
    assert 'value="CASE-2001"' in html
    assert 'value="abc"' in html
    assert "Two payments from two countries." in html


def test_the_decision_cannot_be_set_when_creating(client, valid_form, get_review):
    valid_form["decision"] = "approved"
    client.post("/reviews/new", data=valid_form)
    assert get_review(1).decision == "pending"
