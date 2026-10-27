def test_the_dashboard_opens(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_an_empty_database_shows_the_empty_state(client):
    html = client.get("/").get_data(as_text=True)
    assert "No reviews yet" in html
    assert "Create the first review" in html


def test_the_dashboard_shows_all_reviews(client, add_review):
    add_review(case_reference="CASE-A", prediction="Low risk")
    add_review(case_reference="CASE-B", prediction="High risk")
    html = client.get("/").get_data(as_text=True)
    assert "CASE-A" in html and "CASE-B" in html
    assert "Low risk" in html and "High risk" in html
    assert "No reviews yet" not in html


def test_the_dashboard_shows_the_confidence_with_two_decimals(client, add_review):
    add_review(confidence=0.9)
    assert "0.90" in client.get("/").get_data(as_text=True)


def test_the_newest_review_comes_first(client, add_review):
    add_review(case_reference="OLDER")
    add_review(case_reference="NEWER")
    html = client.get("/").get_data(as_text=True)
    assert html.index("NEWER") < html.index("OLDER")


def test_status_totals_count_every_decision(client, add_review):
    add_review(decision="pending")
    add_review(decision="pending")
    add_review(decision="approved")
    add_review(decision="rejected")
    html = client.get("/").get_data(as_text=True)
    assert '<div class="total"><span class="number">4</span>' in html
    assert '<div class="total pending"><span class="number">2</span>' in html
    assert '<div class="total approved"><span class="number">1</span>' in html
    assert '<div class="total rejected"><span class="number">1</span>' in html


def test_totals_are_zero_when_there_are_no_reviews(client):
    html = client.get("/").get_data(as_text=True)
    assert '<div class="total pending"><span class="number">0</span>' in html


def test_the_stylesheet_is_served(client):
    response = client.get("/static/style.css")
    assert response.status_code == 200
    response.close()


def test_text_from_a_form_is_escaped_in_the_page(client, add_review):
    add_review(case_reference="<script>alert(1)</script>")
    html = client.get("/").get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_an_unknown_page_gives_a_friendly_404(client):
    response = client.get("/nothing-here")
    assert response.status_code == 404
    assert "Page not found" in response.get_data(as_text=True)
