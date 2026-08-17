from src import app as app_module


class TestRootAndActivities:
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_location = "/static/index.html"

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_location

    def test_static_index_is_served(self, client):
        # Arrange
        expected_title = "Mergington High School Activities"

        # Act
        response = client.get("/static/index.html")

        # Assert
        assert response.status_code == 200
        assert expected_title in response.text

    def test_get_activities_returns_seeded_activity_data(self, client):
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert response.status_code == 200
        assert expected_activity in activities
        assert activities[expected_activity]["description"]
        assert activities[expected_activity]["schedule"]
        assert activities[expected_activity]["max_participants"] == 12
        assert "michael@mergington.edu" in activities[expected_activity]["participants"]


class TestSignup:
    def test_signup_adds_participant(self, client):
        # Arrange
        activity = "Basketball Team"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Signed up {email} for {activity}"
        }
        assert email in app_module.activities[activity]["participants"]

    def test_signup_rejects_unknown_activity(self, client):
        # Arrange
        activity = "Missing Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_signup_rejects_duplicate_participant(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert response.json() == {
            "detail": "Student already signed up for this activity"
        }

    def test_signup_requires_email(self, client):
        # Arrange
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup")

        # Assert
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["query", "email"]


class TestUnregister:
    def test_unregister_removes_participant(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        assert response.json() == {
            "message": f"Unregistered {email} from {activity}"
        }
        assert email not in app_module.activities[activity]["participants"]

    def test_unregister_rejects_unknown_activity(self, client):
        # Arrange
        activity = "Missing Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_unregister_rejects_missing_participant(self, client):
        # Arrange
        activity = "Chess Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert response.json() == {
            "detail": "Student is not signed up for this activity"
        }

    def test_unregister_requires_email(self, client):
        # Arrange
        activity = "Chess Club"

        # Act
        response = client.delete(f"/activities/{activity}/signup")

        # Assert
        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["query", "email"]
