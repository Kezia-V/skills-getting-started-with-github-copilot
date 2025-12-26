import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]


def test_signup_success():
    # Use a new email
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]

    # Check if added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    # Second signup
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_unregister_success():
    # First signup
    client.post("/activities/Programming Class/signup?email=unregistertest@mergington.edu")
    # Then unregister
    response = client.delete("/activities/Programming Class/signup?email=unregistertest@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered unregistertest@mergington.edu from Programming Class" in data["message"]

    # Check if removed
    response = client.get("/activities")
    data = response.json()
    assert "unregistertest@mergington.edu" not in data["Programming Class"]["participants"]


def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess Club/signup?email=nosignup@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"