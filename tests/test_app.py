import pytest
import copy
from fastapi.testclient import TestClient

from src.app import app, activities

# Store original activities for resetting between tests
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities dict to original state before each test."""
    global activities
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))

# Create test client
client = TestClient(app)

# Test GET /activities
def test_get_activities():
    """Test retrieving all activities."""
    # Arrange - activities are reset by fixture

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 9  # Current number of activities
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Verify structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

# Test POST /activities/{activity_name}/signup - success
def test_signup_success():
    """Test successful signup for an activity."""
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in data["message"]
    # Verify data was updated
    assert len(activities[activity_name]["participants"]) == initial_count + 1
    assert email in activities[activity_name]["participants"]

# Test POST /activities/{activity_name}/signup - duplicate
def test_signup_duplicate():
    """Test signup fails when student is already signed up."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]
    # Verify data unchanged
    assert len(activities[activity_name]["participants"]) == initial_count

# Test POST /activities/{activity_name}/signup - non-existent activity
def test_signup_non_existent_activity():
    """Test signup fails for non-existent activity."""
    # Arrange
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

# Test POST /activities/{activity_name}/signup - activity with spaces
def test_signup_activity_with_spaces():
    """Test signup works for activity names with spaces."""
    # Arrange
    activity_name = "Programming Class"  # Has space
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert email in activities[activity_name]["participants"]

# Test DELETE /activities/{activity_name}/participants/{email} - success
def test_remove_participant_success():
    """Test successful removal of a participant."""
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email in data["message"]
    # Verify data was updated
    assert len(activities[activity_name]["participants"]) == initial_count - 1
    assert email not in activities[activity_name]["participants"]

# Test DELETE /activities/{activity_name}/participants/{email} - non-existent activity
def test_remove_participant_non_existent_activity():
    """Test removal fails for non-existent activity."""
    # Arrange
    activity_name = "NonExistent Club"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

# Test DELETE /activities/{activity_name}/participants/{email} - participant not found
def test_remove_participant_not_found():
    """Test removal fails when participant is not signed up."""
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"  # Not in participants
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "Participant not found" in data["detail"]
    # Verify data unchanged
    assert len(activities[activity_name]["participants"]) == initial_count

# Test DELETE /activities/{activity_name}/participants/{email} - activity with spaces
def test_remove_participant_activity_with_spaces():
    """Test removal works for activity names with spaces."""
    # Arrange
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Already in participants

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Removed" in data["message"]
    assert email not in activities[activity_name]["participants"]

# Test root redirect
def test_root_redirect():
    """Test root endpoint redirects to static page."""
    # Arrange - nothing

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200  # FastAPI handles redirect internally in test client
    # Note: TestClient follows redirects by default, so it returns the final response