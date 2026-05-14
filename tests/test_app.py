import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# Save a deep copy of the initial activity state so tests can reset the in-memory database.
INITIAL_ACTIVITIES = copy.deepcopy(activities)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture(autouse=True)
def client():
    reset_activities()
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"], dict)
    assert data["Chess Club"]["max_participants"] == 12
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant(client):
    response = client.post("/activities/Chess%20Club/signup?email=student@example.com")

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up student@example.com for Chess Club"}
    assert "student@example.com" in activities["Chess Club"]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    existing_email = "michael@mergington.edu"
    response = client.post(f"/activities/Chess%20Club/signup?email={existing_email}")

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_delete_participant_removes_existing_participant(client):
    email = "daniel@mergington.edu"
    response = client.delete(f"/activities/Chess%20Club/participants?email={email}")

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_delete_missing_participant_returns_404(client):
    response = client.delete("/activities/Chess%20Club/participants?email=missing@example.com")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
