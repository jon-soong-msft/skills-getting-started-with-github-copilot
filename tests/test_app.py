import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

initial_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: initialize clean activity store for each test
    app_module.activities = copy.deepcopy(initial_activities)
    yield


def test_get_activities_returns_initial_data():
    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_success():
    # Arrange
    email = "alex@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    after = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert email in after[activity_name]["participants"]


def test_signup_for_activity_already_signed_up():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_nonexistent_activity():
    # Act
    response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_success():
    # Arrange
    participant = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{participant}")
    after = client.get("/activities").json()

    # Assert
    assert response.status_code == 200
    assert participant not in after[activity_name]["participants"]


def test_remove_participant_not_found_activity():
    # Act
    response = client.delete("/activities/NotExist/participants/test@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_not_signed_up():
    # Act
    response = client.delete("/activities/Chess Club/participants/not-a-user@mergington.edu")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
