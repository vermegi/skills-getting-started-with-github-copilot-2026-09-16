import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from app import activities, app


client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_collection():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert expected_activity in response.json()
    assert "participants" in response.json()[expected_activity]
    assert "waitlist" in response.json()[expected_activity]


def test_signup_adds_student_to_activity():
    # Arrange
    activity_name = "Soccer Team"
    email = "signup-test@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert response.json()["status"] == "registered"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_unknown_activity():
    # Arrange
    activity_name = "Unknown Club"
    email = "unknown-activity@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_rejects_duplicate_student():
    # Arrange
    activity_name = "Chess Club"
    email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_waitlists_student_when_activity_is_full():
    # Arrange
    activity_name = "Science Club"
    original_participants = activities[activity_name]["participants"][:]
    original_waitlist = activities[activity_name]["waitlist"][:]
    activities[activity_name]["participants"] = [
        f"student-{number}@mergington.edu"
        for number in range(activities[activity_name]["max_participants"])
    ]
    activities[activity_name]["waitlist"] = []
    email = "full-activity@mergington.edu"

    try:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "waitlisted"
        assert response.json()["waitlist_position"] == 1
        assert email in activities[activity_name]["waitlist"]
        assert email not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants
        activities[activity_name]["waitlist"] = original_waitlist


def test_signup_rejects_student_already_on_waitlist():
    # Arrange
    activity_name = "Science Club"
    original_participants = activities[activity_name]["participants"][:]
    original_waitlist = activities[activity_name]["waitlist"][:]
    activities[activity_name]["participants"] = [
        f"student-{number}@mergington.edu"
        for number in range(activities[activity_name]["max_participants"])
    ]
    email = "duplicate-waitlist@mergington.edu"
    activities[activity_name]["waitlist"] = [email]

    try:
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already on the waitlist for this activity"
    finally:
        activities[activity_name]["participants"] = original_participants
        activities[activity_name]["waitlist"] = original_waitlist


def test_unregister_promotes_first_waitlisted_student():
    # Arrange
    activity_name = "Basketball Team"
    original_participants = activities[activity_name]["participants"][:]
    original_waitlist = activities[activity_name]["waitlist"][:]
    participants = [
        f"player-{number}@mergington.edu"
        for number in range(activities[activity_name]["max_participants"])
    ]
    activities[activity_name]["participants"] = participants[:]
    activities[activity_name]["waitlist"] = [
        "waiting-first@mergington.edu",
        "waiting-second@mergington.edu",
    ]

    try:
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": participants[0]},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["promoted"] == "waiting-first@mergington.edu"
        assert "waiting-first@mergington.edu" in activities[activity_name]["participants"]
        assert activities[activity_name]["waitlist"] == ["waiting-second@mergington.edu"]
        assert participants[0] not in activities[activity_name]["participants"]
    finally:
        activities[activity_name]["participants"] = original_participants
        activities[activity_name]["waitlist"] = original_waitlist


def test_unregister_removes_student_from_waitlist():
    # Arrange
    activity_name = "Drama Club"
    email = "waitlist-withdraw@mergington.edu"
    original_waitlist = activities[activity_name]["waitlist"][:]
    activities[activity_name]["waitlist"] = [email]

    try:
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "removed_from_waitlist"
        assert email not in activities[activity_name]["waitlist"]
    finally:
        activities[activity_name]["waitlist"] = original_waitlist


def test_unregister_removes_student_from_activity():
    # Arrange
    activity_name = "Art Club"
    email = "unregister-test@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert response.json()["promoted"] is None
    assert email not in activities[activity_name]["participants"]


def test_unregister_rejects_unknown_activity():
    # Arrange
    activity_name = "Unknown Club"
    email = "unknown-activity@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_nonparticipant():
    # Arrange
    activity_name = "Debate Club"
    email = "nonparticipant@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"