from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activity_state():
    original_participants = {
        name: list(details["participants"])
        for name, details in activities.items()
    }
    yield
    for name, details in activities.items():
        details["participants"] = list(original_participants[name])


def test_get_activities_returns_activity_catalog():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_is_rejected():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Unknown Activity/signup?email=test@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
