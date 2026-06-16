class TestGetActivities:
    """Test GET /activities endpoint using AAA pattern"""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_minimum_count = 1
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert response.status_code == 200
        assert isinstance(activities, dict)
        assert len(activities) >= expected_minimum_count
        
        # Verify each activity has required structure
        for activity_name, activity_data in activities.items():
            assert all(field in activity_data for field in required_fields)
            assert isinstance(activity_data["participants"], list)

    def test_activities_contain_sample_participants(self, client):
        # Arrange
        # No specific arrangement needed for this test
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        activities_with_participants = [
            activity for activity in activities.values()
            if len(activity["participants"]) > 0
        ]
        assert len(activities_with_participants) > 0, "At least one activity should have participants"


class TestSignupForActivity:
    """Test POST /activities/{activity_name}/signup endpoint using AAA pattern"""

    def test_signup_adds_participant_successfully(self, client):
        # Arrange
        activity_name = "Chess%20Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]
        assert "Signed up" in response.json()["message"]

    def test_signup_prevents_duplicate_registration(self, client):
        # Arrange
        activity_name = "Chess%20Club"
        email = "duplicate@mergington.edu"
        
        # Act - First signup
        response_first = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Second signup with same email
        response_second = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response_first.status_code == 200
        assert response_second.status_code == 400
        assert "already signed up" in response_second.json()["detail"].lower()

    def test_signup_fails_for_nonexistent_activity(self, client):
        # Arrange
        activity_name = "Nonexistent%20Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_accepts_various_email_formats(self, client):
        # Arrange
        test_emails = [
            "simple@mergington.edu",
            "with.dot@mergington.edu",
            "with+plus@mergington.edu",
        ]
        activity_name = "Programming%20Class"
        
        # Act & Assert
        for email in test_emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200


class TestRemoveParticipant:
    """Test DELETE /activities/{activity_name}/participants endpoint using AAA pattern"""

    def test_remove_participant_deletes_from_activity(self, client):
        # Arrange
        activity_name = "Chess%20Club"
        email = "removeme@mergington.edu"
        
        # Add participant first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

    def test_remove_participant_fails_if_not_registered(self, client):
        # Arrange
        activity_name = "Chess%20Club"
        email = "nobody@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_remove_from_nonexistent_activity_returns_error(self, client):
        # Arrange
        activity_name = "Fake%20Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404

    def test_participant_can_be_readded_after_removal(self, client):
        # Arrange
        activity_name = "Chess%20Club"
        email = "readd@mergington.edu"
        signup_endpoint = f"/activities/{activity_name}/signup"
        remove_endpoint = f"/activities/{activity_name}/participants"
        
        # Act - Add participant
        response_add1 = client.post(signup_endpoint, params={"email": email})
        
        # Act - Remove participant
        response_remove = client.delete(remove_endpoint, params={"email": email})
        
        # Act - Add participant again
        response_add2 = client.post(signup_endpoint, params={"email": email})
        
        # Assert
        assert response_add1.status_code == 200
        assert response_remove.status_code == 200
        assert response_add2.status_code == 200


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error conditions using AAA pattern"""

    def test_special_characters_in_activity_names_handled(self, client):
        # Arrange
        response_activities = client.get("/activities")
        activities = response_activities.json()
        email = "test@mergington.edu"
        
        # Act & Assert
        for activity_name in list(activities.keys())[:2]:  # Test first 2 activities
            encoded_name = activity_name.replace(" ", "%20")
            response = client.post(
                f"/activities/{encoded_name}/signup",
                params={"email": email}
            )
            # Should succeed or fail gracefully
            assert response.status_code in [200, 400]

    def test_get_activities_is_idempotent(self, client):
        # Arrange
        # No arrangement needed
        
        # Act - First call
        response1 = client.get("/activities")
        data1 = response1.json()
        
        # Act - Second call
        response2 = client.get("/activities")
        data2 = response2.json()
        
        # Assert
        assert data1 == data2, "GET activities should return same data on subsequent calls"

    def test_signup_multiple_participants_for_same_activity(self, client):
        # Arrange
        activity_name = "Gym%20Class"
        emails = [
            "participant1@mergington.edu",
            "participant2@mergington.edu",
            "participant3@mergington.edu",
        ]
        
        # Act
        responses = [
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            for email in emails
        ]
        
        # Assert
        assert all(response.status_code == 200 for response in responses)
        
        # Verify all are added
        activities_response = client.get("/activities")
        activity_data = activities_response.json()[activity_name.replace("%20", " ")]
        assert all(email in activity_data["participants"] for email in emails)
