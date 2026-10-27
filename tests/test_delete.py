def test_the_delete_page_asks_first_and_deletes_nothing(client, add_review, count_reviews):
    review_id = add_review(case_reference="CASE-5")
    response = client.get(f"/reviews/{review_id}/delete")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Delete review CASE-5?" in html
    assert 'method="post"' in html
    assert "Yes, delete this review" in html
    assert count_reviews() == 1


def test_a_post_request_deletes_the_review(client, add_review, count_reviews, get_review):
    review_id = add_review(case_reference="CASE-6")
    response = client.post(f"/reviews/{review_id}/delete")
    assert response.status_code == 302
    assert count_reviews() == 0
    assert get_review(review_id) is None


def test_the_dashboard_confirms_the_deletion(client, add_review):
    review_id = add_review(case_reference="CASE-6")
    response = client.post(f"/reviews/{review_id}/delete", follow_redirects=True)
    html = response.get_data(as_text=True)
    assert "Review CASE-6 was deleted." in html
    assert "No reviews yet" in html


def test_only_the_chosen_review_is_deleted(client, add_review, get_review):
    keep = add_review(case_reference="KEEP")
    drop = add_review(case_reference="DROP")
    client.post(f"/reviews/{drop}/delete")
    assert get_review(keep) is not None
    assert get_review(drop) is None


def test_deleting_an_unknown_review_gives_404(client):
    assert client.get("/reviews/999/delete").status_code == 404
    assert client.post("/reviews/999/delete").status_code == 404


def test_the_dashboard_links_only_to_the_confirmation_page(client, add_review):
    review_id = add_review()
    html = client.get("/").get_data(as_text=True)
    assert f'href="/reviews/{review_id}/delete"' in html
    assert "<form" not in html


def test_other_methods_cannot_delete(client, add_review, count_reviews):
    review_id = add_review()
    assert client.delete(f"/reviews/{review_id}/delete").status_code == 405
    assert client.put(f"/reviews/{review_id}/delete").status_code == 405
    assert count_reviews() == 1
