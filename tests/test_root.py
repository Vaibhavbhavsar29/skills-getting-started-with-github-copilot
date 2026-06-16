class TestRootEndpoint:
    """Test GET / endpoint using AAA pattern"""

    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_status = 307
        expected_location = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == expected_status
        assert response.headers["location"] == expected_location

    def test_root_redirect_resolves_to_html(self, client):
        # Arrange
        expected_content_type = "text/html"
        
        # Act
        response = client.get("/", follow_redirects=True)
        
        # Assert
        assert response.status_code == 200
        assert expected_content_type in response.headers.get("content-type", "")
