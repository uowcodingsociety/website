import pytest

import codesoc


@pytest.fixture
def client():
    codesoc.app.config["TESTING"] = True
    return codesoc.app.test_client()


def test_cpp_moved_from_coming_soon_to_available(client):
    html = client.get("/learn/courses").get_data(as_text=True)
    assert '<a href="#cpp">' in html
    assert html.count("whitecpp.png") == 1
    # The coloured icon is now only used on the C++ card, not under "Coming Soon"
    assert html.count("cppicon.png") == 1
    assert html.index("cppicon.png") > html.index('id="cpp"')


def test_cpp_card_links_to_course(client):
    html = client.get("/learn/courses").get_data(as_text=True)
    assert 'id="cpp"' in html
    assert '<a href="/learn/courses/cpp/">' in html


def test_feedback_form_offers_cpp(client):
    html = client.get("/learn/courses").get_data(as_text=True)
    assert '<option value="C++">C++</option>' in html
