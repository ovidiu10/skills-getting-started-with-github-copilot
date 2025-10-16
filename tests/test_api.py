"""
Tests for the Mergington High School Activities API endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client: TestClient):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client: TestClient, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) >= 9  # Should have at least 9 activities
        
        # Check that all activities have required fields
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_get_activities_includes_chess_club(self, client: TestClient, reset_activities):
        """Test that Chess Club is included in activities."""
        response = client.get("/activities")
        data = response.json()
        
        assert "Chess Club" in data
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignupEndpoint:
    """Tests for the signup endpoint."""
    
    def test_signup_for_existing_activity_success(self, client: TestClient, reset_activities, sample_email):
        """Test successful signup for an existing activity."""
        response = client.post(f"/activities/Soccer Team/signup?email={sample_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {sample_email} for Soccer Team"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert sample_email in activities_data["Soccer Team"]["participants"]
    
    def test_signup_for_nonexistent_activity_fails(self, client: TestClient, reset_activities, sample_email):
        """Test that signup for non-existent activity returns 404."""
        response = client.post(f"/activities/Nonexistent Activity/signup?email={sample_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_participant_fails(self, client: TestClient, reset_activities, sample_email):
        """Test that duplicate signup returns 400."""
        # First signup should succeed
        response1 = client.post(f"/activities/Soccer Team/signup?email={sample_email}")
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(f"/activities/Soccer Team/signup?email={sample_email}")
        assert response2.status_code == 400
        
        data = response2.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_with_existing_participant_fails(self, client: TestClient, reset_activities):
        """Test that signing up existing participant fails."""
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(f"/activities/Chess Club/signup?email={existing_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"
    
    def test_signup_with_url_encoded_activity_name(self, client: TestClient, reset_activities, sample_email):
        """Test signup with URL-encoded activity name."""
        import urllib.parse
        encoded_name = urllib.parse.quote("Art Workshop")
        
        response = client.post(f"/activities/{encoded_name}/signup?email={sample_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {sample_email} for Art Workshop"


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint."""
    
    def test_unregister_existing_participant_success(self, client: TestClient, reset_activities):
        """Test successful unregistration of existing participant."""
        existing_email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.delete(f"/activities/Chess Club/unregister?email={existing_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {existing_email} from Chess Club"
        
        # Verify the participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert existing_email not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client: TestClient, reset_activities, sample_email):
        """Test that unregister from non-existent activity returns 404."""
        response = client.delete(f"/activities/Nonexistent Activity/unregister?email={sample_email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_non_participant_fails(self, client: TestClient, reset_activities, sample_email):
        """Test that unregistering non-participant returns 400."""
        response = client.delete(f"/activities/Chess Club/unregister?email={sample_email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
    
    def test_unregister_with_url_encoded_activity_name(self, client: TestClient, reset_activities):
        """Test unregister with URL-encoded activity name."""
        import urllib.parse
        
        # First, sign up a user
        test_email = "test@mergington.edu"
        client.post(f"/activities/Art Workshop/signup?email={test_email}")
        
        # Then unregister with encoded name
        encoded_name = urllib.parse.quote("Art Workshop")
        response = client.delete(f"/activities/{encoded_name}/unregister?email={test_email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Unregistered {test_email} from Art Workshop"


class TestIntegrationWorkflows:
    """Integration tests for complete workflows."""
    
    def test_complete_signup_unregister_workflow(self, client: TestClient, reset_activities, sample_email):
        """Test complete workflow: signup -> verify -> unregister -> verify."""
        activity_name = "Basketball Club"
        
        # 1. Initial state - no participants
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        assert sample_email not in initial_data[activity_name]["participants"]
        
        # 2. Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={sample_email}")
        assert signup_response.status_code == 200
        
        # 3. Verify signup
        after_signup_response = client.get("/activities")
        after_signup_data = after_signup_response.json()
        assert sample_email in after_signup_data[activity_name]["participants"]
        
        # 4. Unregister
        unregister_response = client.delete(f"/activities/{activity_name}/unregister?email={sample_email}")
        assert unregister_response.status_code == 200
        
        # 5. Verify unregistration
        after_unregister_response = client.get("/activities")
        after_unregister_data = after_unregister_response.json()
        assert sample_email not in after_unregister_data[activity_name]["participants"]
    
    def test_multiple_participants_same_activity(self, client: TestClient, reset_activities):
        """Test multiple participants can join the same activity."""
        activity_name = "Drama Club"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Sign up multiple participants
        for email in emails:
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all participants are registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        participants = activities_data[activity_name]["participants"]
        
        for email in emails:
            assert email in participants
        
        assert len(participants) == 3
    
    def test_participant_can_join_multiple_activities(self, client: TestClient, reset_activities, sample_email):
        """Test that a participant can join multiple different activities."""
        activities_to_join = ["Soccer Team", "Drama Club", "Math Club"]
        
        # Sign up for multiple activities
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={sample_email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities_to_join:
            assert sample_email in activities_data[activity]["participants"]