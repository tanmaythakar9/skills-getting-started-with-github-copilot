from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

INITIAL_ACTIVITIES = deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_all_activities(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["max_participants"] == 12
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant(client):
    email = "test.student@mergington.edu"
    response = client.post(
        "/activities/Chess%20Club/signup?email=test.student%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for Chess Club"
    }

    activities_response = client.get("/activities").json()
    assert email in activities_response["Chess Club"]["participants"]


def test_duplicate_signup_returns_400(client):
    email = "emma@mergington.edu"

    first = client.post(
        "/activities/Programming%20Class/signup?email=emma%40mergington.edu"
    )
    assert first.status_code == 400
    assert first.json()["detail"] == "Student already signed up"


def test_remove_participant_unregisters_student(client):
    email = "daniel@mergington.edu"
    response = client.delete(
        "/activities/Chess%20Club/participants?email=daniel%40mergington.edu"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Chess Club"}

    activities_response = client.get("/activities").json()
    assert email not in activities_response["Chess Club"]["participants"]
