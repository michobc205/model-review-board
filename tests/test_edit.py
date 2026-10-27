def test_the_edit_form_opens_with_the_saved_values(client, add_review):
    review_id = add_review(case_reference="CASE-7", decision="rejected", notes="Wrong label.")
    response = client.get(f"/reviews/{review_id}/edit")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Edit review CASE-7" in html
    assert "Wrong label." in html
    assert '<option value="rejected" selected>' in html


def test_a_review_can_be_approved_with_notes(client, add_review, get_review):
    review_id = add_review()
    response = client.post(
        f"/reviews/{review_id}/edit", data={"decision": "approved", "notes": "Checked the source data."}
    )
    assert response.status_code == 302
    review = get_review(review_id)
    assert review.decision == "approved"
    assert review.notes == "Checked the source data."


def test_a_review_can_be_rejected(client, add_review, get_review):
    review_id = add_review()
    client.post(f"/reviews/{review_id}/edit", data={"decision": "rejected", "notes": "Does not match."})
    assert get_review(review_id).decision == "rejected"


def test_the_saved_decision_is_visible_in_another_session(app, client, add_review):
    review_id = add_review(case_reference="CASE-8")
    client.post(f"/reviews/{review_id}/edit", data={"decision": "approved", "notes": "Fine."})
    other_browser = app.test_client()
    html = other_browser.get("/").get_data(as_text=True)
    assert "CASE-8" in html
    assert '<span class="badge approved">approved</span>' in html
    assert "Fine." in html


def test_the_updated_message_and_totals_after_saving(client, add_review):
    review_id = add_review(case_reference="CASE-9")
    response = client.post(
        f"/reviews/{review_id}/edit", data={"decision": "approved", "notes": ""}, follow_redirects=True
    )
    html = response.get_data(as_text=True)
    assert "Review CASE-9 was updated." in html
    assert '<div class="total approved"><span class="number">1</span>' in html
    assert '<div class="total pending"><span class="number">0</span>' in html


def test_an_unknown_decision_is_rejected(client, add_review, get_review):
    review_id = add_review()
    response = client.post(f"/reviews/{review_id}/edit", data={"decision": "maybe", "notes": "x"})
    assert response.status_code == 400
    assert "Decision must be one of: pending, approved, rejected." in response.get_data(as_text=True)
    assert get_review(review_id).decision == "pending"


def test_too_long_notes_are_rejected(client, add_review, get_review):
    review_id = add_review()
    response = client.post(f"/reviews/{review_id}/edit", data={"decision": "approved", "notes": "x" * 2001})
    assert response.status_code == 400
    assert get_review(review_id).notes == ""


def test_editing_an_unknown_review_gives_404(client):
    assert client.get("/reviews/999/edit").status_code == 404
    assert client.post("/reviews/999/edit", data={"decision": "approved"}).status_code == 404
