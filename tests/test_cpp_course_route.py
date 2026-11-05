import pytest

import codesoc


@pytest.fixture
def client():
    codesoc.app.config["TESTING"] = True
    return codesoc.app.test_client()


def test_cpp_course_path_without_slash_redirects(client):
    resp = client.get("/learn/courses/cpp")
    assert resp.status_code == 308
    assert resp.headers["Location"] == "/learn/courses/cpp/"


def test_course_pages_are_not_served_by_flask(client):
    # PythonAnywhere's static file mapping answers /learn/courses/cpp/ before Flask sees it
    assert client.get("/learn/courses/cpp/").status_code == 404
