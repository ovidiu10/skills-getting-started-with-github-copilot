"""
Test utilities and helper functions for the test suite.
"""
from typing import Dict, Any


def assert_activity_structure(activity_data: Dict[str, Any]) -> None:
    """Assert that an activity has the correct structure."""
    required_fields = ["description", "schedule", "max_participants", "participants"]
    
    for field in required_fields:
        assert field in activity_data, f"Missing required field: {field}"
    
    assert isinstance(activity_data["description"], str), "Description should be a string"
    assert isinstance(activity_data["schedule"], str), "Schedule should be a string"
    assert isinstance(activity_data["max_participants"], int), "Max participants should be an integer"
    assert isinstance(activity_data["participants"], list), "Participants should be a list"
    assert activity_data["max_participants"] > 0, "Max participants should be positive"


def get_activity_participant_count(activities_data: Dict[str, Any], activity_name: str) -> int:
    """Get the current participant count for an activity."""
    return len(activities_data[activity_name]["participants"])


def get_activity_spots_remaining(activities_data: Dict[str, Any], activity_name: str) -> int:
    """Get the number of spots remaining for an activity."""
    activity = activities_data[activity_name]
    return activity["max_participants"] - len(activity["participants"])


def is_participant_registered(activities_data: Dict[str, Any], activity_name: str, email: str) -> bool:
    """Check if a participant is registered for an activity."""
    return email in activities_data[activity_name]["participants"]