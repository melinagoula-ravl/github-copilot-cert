"""Test suite for the High School Activities Management API using AAA pattern."""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Created by fixture (client with 3 activities)
        Act: Make GET request to /activities
        Assert: Verify all activities are returned with correct structure
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_includes_all_fields(self, client):
        """
        Arrange: Created by fixture
        Act: Make GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_get_activities_includes_existing_participants(self, client):
        """
        Arrange: Created by fixture
        Act: Make GET request to /activities
        Assert: Verify participants are included in response
        """
        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """
        Arrange: Client with activities, new student email
        Act: Make POST request to signup endpoint
        Assert: Verify student is added and response indicates success
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_rejected(self, client):
        """
        Arrange: Client with activities, student already signed up
        Act: Attempt to sign up same student again
        Assert: Verify 400 error is returned with appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_invalid_activity_rejected(self, client):
        """
        Arrange: Client with activities, non-existent activity name
        Act: Attempt to sign up for non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Non Existent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_signup_multiple_students_success(self, client):
        """
        Arrange: Client with activities
        Act: Sign up two different students
        Assert: Verify both are added successfully
        """
        # Arrange
        activity_name = "Chess Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client):
        """
        Arrange: Client with activities, registered student
        Act: Make DELETE request to unregister endpoint
        Assert: Verify student is removed and response indicates success
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_registered_rejected(self, client):
        """
        Arrange: Client with activities, student not signed up
        Act: Attempt to unregister student who is not registered
        Assert: Verify 400 error is returned
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_invalid_activity_rejected(self, client):
        """
        Arrange: Client with activities, non-existent activity name
        Act: Attempt to unregister from non-existent activity
        Assert: Verify 404 error is returned
        """
        # Arrange
        activity_name = "Non Existent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_multiple_students(self, client):
        """
        Arrange: Client with activities
        Act: Sign up two students, then unregister both
        Assert: Verify both are removed successfully
        """
        # Arrange
        activity_name = "Chess Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Sign up both students
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})

        # Act
        response1 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 not in activities[activity_name]["participants"]
        assert email2 not in activities[activity_name]["participants"]


class TestIntegration:
    """Integration tests for combined workflows."""

    def test_signup_then_unregister_workflow(self, client):
        """
        Arrange: Client with activities
        Act: Sign up student, then unregister same student
        Assert: Verify student is not in participants after workflow
        """
        # Arrange
        activity_name = "Programming Class"
        email = "workflow@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert - Signed up
        assert signup_response.status_code == 200
        
        # Act - Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert - Unregistered
        assert unregister_response.status_code == 200
        
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_signup_unregister_signup_again(self, client):
        """
        Arrange: Client with activities
        Act: Sign up, unregister, then sign up same student again
        Assert: Verify student can re-enroll after unregistering
        """
        # Arrange
        activity_name = "Gym Class"
        email = "reregister@mergington.edu"

        # Act - First sign up
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200

        # Act - Unregister
        response2 = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200

        # Act - Re-register
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response3.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]
