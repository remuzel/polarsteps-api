from unittest.mock import Mock, patch

import pytest
import requests

from polarsteps_api.client import HTTPClient, PolarstepsClient
from polarsteps_api.models.base import BaseRequest, BaseResponse
from polarsteps_api.models.request import GetTripRequest, GetUserByUsernameRequest
from polarsteps_api.models.response import TripResponse, UserResponse


@pytest.fixture
def mock_successful_response():
    """Fixture for successful HTTP response."""
    mock_response = Mock()
    mock_response.json.return_value = {"id": "123", "name": "test"}
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    return mock_response


@pytest.fixture
def mock_text_response():
    """Fixture for successful text response (non-JSON)."""
    mock_response = Mock()
    mock_response.json.side_effect = ValueError("No JSON object could be decoded")
    mock_response.text = "plain text response"
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/plain"}
    return mock_response


@pytest.fixture
def http_client():
    """Fixture for HTTPClient instance."""
    return HTTPClient("https://api.example.com", "test_token")


@pytest.fixture
def mock_request():
    """Fixture for mock BaseRequest."""
    mock_req = Mock(spec=BaseRequest)
    mock_req.get_endpoint.return_value = "/test"
    mock_req.get_method.return_value = "GET"
    mock_req.headers = {}
    return mock_req


def assert_response_matches(
    response, expected_data, expected_status=200, expected_headers=None
):
    """Helper function for response verification."""
    assert response.data == expected_data
    assert response.status_code == expected_status
    if expected_headers:
        assert response.headers == expected_headers


def assert_required_headers_present(headers, remember_token="test_token"):
    """Helper function to verify required headers are present."""
    required_headers = {
        "User-Agent": "PolarstepsClient/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Cookie": f"remember_token={remember_token}",
    }

    for key, value in required_headers.items():
        assert headers[key] == value


class TestHTTPClient:
    """Test cases for HTTPClient class."""

    @pytest.mark.parametrize(
        "base_url,expected",
        [
            ("https://api.example.com/", "https://api.example.com"),
            ("https://api.example.com", "https://api.example.com"),
        ],
    )
    def test_init_handles_base_url(self, base_url, expected):
        """Test that HTTPClient handles base_url correctly."""
        client = HTTPClient(base_url, "test_token")
        assert client.base_url == expected

    def test_init_sets_attributes_and_headers(self, http_client):
        """Test that HTTPClient sets all attributes and headers correctly."""
        assert http_client.remember_token == "test_token"
        assert isinstance(http_client.session, requests.Session)

        # Verify required headers
        assert_required_headers_present(http_client.session.headers)

    @patch("requests.Session.request")
    def test_execute_successful_responses(
        self, mock_request_method, http_client, mock_request
    ):
        """Test execute method with successful JSON and text responses."""
        # Test JSON response
        mock_request_method.return_value = Mock(
            json=lambda: {"id": "123", "name": "test"},
            status_code=200,
            headers={"Content-Type": "application/json"},
        )

        response = http_client.execute(mock_request)
        assert_response_matches(
            response,
            {"id": "123", "name": "test"},
            200,
            {"Content-Type": "application/json"},
        )

        # Test text response
        text_mock = Mock()
        text_mock.json.side_effect = ValueError("No JSON")
        text_mock.text = "plain text"
        text_mock.status_code = 200
        text_mock.headers = {"Content-Type": "text/plain"}
        mock_request_method.return_value = text_mock

        response = http_client.execute(mock_request)
        assert_response_matches(
            response, "plain text", 200, {"Content-Type": "text/plain"}
        )

    @patch("requests.Session.request")
    def test_execute_request_exception(
        self, mock_request_method, http_client, mock_request
    ):
        """Test execute method when requests raises an exception."""
        mock_request_method.side_effect = requests.RequestException("Connection error")

        response = http_client.execute(mock_request)
        assert_response_matches(response, {"error": "Connection error"}, 0, {})

    @patch("requests.Session.request")
    def test_execute_merges_headers(self, mock_request_method, http_client):
        """Test that execute method merges request headers with session headers."""
        mock_request_method.return_value = Mock(json=dict, status_code=200, headers={})

        # Create request with custom headers
        mock_req = Mock(spec=BaseRequest)
        mock_req.get_endpoint.return_value = "/test"
        mock_req.get_method.return_value = "POST"
        mock_req.headers = {
            "Custom-Header": "custom-value",
            "Accept": "application/xml",  # Override session header
        }

        http_client.execute(mock_req)

        # Verify headers were merged correctly
        call_args = mock_request_method.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["url"] == "https://api.example.com/test"

        headers = call_args[1]["headers"]
        assert headers["User-Agent"] == "PolarstepsClient/1.0"
        assert headers["Accept"] == "application/xml"  # Overridden by request
        assert headers["Content-Type"] == "application/json"
        assert headers["Cookie"] == "remember_token=test_token"
        assert headers["Custom-Header"] == "custom-value"


class TestPolarstepsClient:
    """Test cases for PolarstepsClient class."""

    def test_init_with_remember_token(self):
        """Test PolarstepsClient initialization with provided remember_token."""
        client = PolarstepsClient(remember_token="test_token")
        assert isinstance(client.http_client, HTTPClient)
        assert client.http_client.remember_token == "test_token"
        assert client.http_client.base_url == "https://api.polarsteps.com"

    @pytest.mark.parametrize(
        "env_value,should_raise",
        [
            ("valid_token", False),
            ("", True),
            (None, True),
        ],
    )
    @patch("polarsteps_api.client.load_dotenv")
    def test_init_with_env_token(
        self, mock_load_dotenv, env_value, should_raise, monkeypatch
    ):
        """Test PolarstepsClient initialization with various environment token values."""
        if env_value is not None:
            monkeypatch.setenv("POLARSTEPS_REMEMBER_TOKEN", env_value)
        else:
            monkeypatch.delenv("POLARSTEPS_REMEMBER_TOKEN", raising=False)

        if should_raise:
            with pytest.raises(ValueError, match="Remember token must be provided"):
                PolarstepsClient()
        else:
            client = PolarstepsClient()
            assert client.http_client.remember_token == env_value

        mock_load_dotenv.assert_called_once()

    @patch("polarsteps_api.client.load_dotenv")
    def test_init_none_token_loads_from_env(self, mock_load_dotenv, monkeypatch):
        """Test PolarstepsClient initialization with None token loads from environment."""
        monkeypatch.setenv("POLARSTEPS_REMEMBER_TOKEN", "env_token")

        client = PolarstepsClient(remember_token=None)
        assert client.http_client.remember_token == "env_token"
        mock_load_dotenv.assert_called_once()

    @pytest.mark.parametrize(
        "method_name,request_class,response_class,test_id",
        [
            ("get_trip", GetTripRequest, TripResponse, "trip123"),
            (
                "get_user_by_username",
                GetUserByUsernameRequest,
                UserResponse,
                "testuser",
            ),
        ],
    )
    @patch("polarsteps_api.client.HTTPClient")
    def test_api_methods(
        self,
        mock_http_client_class,
        method_name,
        request_class,
        response_class,
        test_id,
    ):
        """Test API methods (get_trip and get_user_by_username)."""
        # Setup mock HTTP client
        mock_http_client = Mock()
        mock_response = BaseResponse(
            data={"id": test_id, "name": f"Test {test_id}"},
            status_code=200,
            headers={"Content-Type": "application/json"},
        )
        mock_http_client.execute.return_value = mock_response
        mock_http_client_class.return_value = mock_http_client

        # Create client and call method
        client = PolarstepsClient(remember_token="test_token")
        method = getattr(client, method_name)
        result = method(test_id)

        # Verify result
        assert isinstance(result, response_class)
        assert result.data == {"id": test_id, "name": f"Test {test_id}"}
        assert result.status_code == 200
        assert result.headers == {"Content-Type": "application/json"}

        # Verify HTTP client was called correctly
        mock_http_client.execute.assert_called_once()
        request_arg = mock_http_client.execute.call_args[0][0]
        assert isinstance(request_arg, request_class)

    def test_class_attributes(self):
        """Test that class attributes are set correctly."""
        assert PolarstepsClient.env_token == "POLARSTEPS_REMEMBER_TOKEN"
        assert PolarstepsClient.base_url == "https://api.polarsteps.com"


class TestIntegration:
    """Integration test for complete client flow."""

    @pytest.mark.parametrize(
        "method_name,test_id,expected_endpoint",
        [
            ("get_trip", "trip123", "https://api.polarsteps.com/trips/trip123"),
            (
                "get_user_by_username",
                "testuser",
                "https://api.polarsteps.com/users/byusername/testuser",
            ),
        ],
    )
    @patch("requests.Session.request")
    def test_complete_request_flow(
        self, mock_request, method_name, test_id, expected_endpoint
    ):
        """Test complete flow from PolarstepsClient to HTTP request."""
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": 123,
            "uuid": f"{method_name}-uuid-123",
            "name": f"Test {method_name}",
        }
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_request.return_value = mock_response

        # Create client and make request
        client = PolarstepsClient(remember_token="test_token")
        method = getattr(client, method_name)
        result = method(test_id)

        # Verify the complete flow
        expected_data = {
            "id": 123,
            "uuid": f"{method_name}-uuid-123",
            "name": f"Test {method_name}",
        }
        assert_response_matches(result, expected_data, 200)

        # Verify HTTP request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == expected_endpoint

        # Check that required headers are present
        assert_required_headers_present(call_args[1]["headers"])

    @patch("requests.Session.request")
    def test_error_handling_flow(self, mock_request):
        """Test error handling throughout the complete flow."""
        mock_request.side_effect = requests.ConnectionError("Network error")

        client = PolarstepsClient(remember_token="test_token")
        result = client.get_trip("trip123")

        # Verify error is handled properly
        assert isinstance(result, TripResponse)
        assert_response_matches(result, {"error": "Network error"}, 0, {})
