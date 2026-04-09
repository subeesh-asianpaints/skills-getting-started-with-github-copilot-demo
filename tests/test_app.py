from fastapi.testclient import TestClient
from src.app import app, activities
import copy
import pytest

client = TestClient(app, follow_redirects=False)
original_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    global activities
    activities.clear()
    activities.update(copy.deepcopy(original_activities))

def test_get_activities():
    # Arrange
    # Activities are reset by fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    assert email in activities[activity]["participants"]

def test_signup_duplicate():
    # Arrange
    email = "michael@mergington.edu"  # Already signed up for Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_invalid_activity():
    # Arrange
    email = "test@test.com"
    activity = "NonExistentActivity"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_success():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    assert email not in activities[activity]["participants"]

def test_unregister_invalid_activity():
    # Arrange
    email = "test@test.com"
    activity = "NonExistentActivity"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_not_signed_up():
    # Arrange
    email = "notsigned@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")

    # Assert
    assert response.status_code == 404
    result = response.json()
    assert "not signed up" in result["detail"]

def test_root_redirect():
    # Arrange
    # No special setup needed

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"