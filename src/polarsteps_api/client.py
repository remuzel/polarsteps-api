import os
from typing import Optional, Union

import requests
from cachetools import TTLCache
from dotenv import load_dotenv

from polarsteps_api.models.base import BaseRequest, BaseResponse
from polarsteps_api.models.request import GetTripRequest, GetUserByUsernameRequest
from polarsteps_api.models.response import TripResponse, UserResponse


class HTTPClient:
    def __init__(
        self,
        base_url: str,
        remember_token: str,
    ):
        self.base_url = base_url.rstrip("/")
        self.remember_token = remember_token
        self.session = requests.Session()

        # Set default headers from config
        headers = {
            "User-Agent": "PolarstepsClient/1.0",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Cookie": f"remember_token={remember_token}",
        }

        self.session.headers.update(headers)

    def execute(self, request: BaseRequest) -> BaseResponse:
        url = f"{self.base_url}{request.get_endpoint()}"

        # Merge request headers with session headers
        headers = {**self.session.headers, **request.headers}

        try:
            response = self.session.request(
                method=request.get_method(),
                url=url,
                headers=headers,
            )

            # Try to parse JSON, fallback to text
            try:
                data = response.json()
            except ValueError:
                data = response.text

            return BaseResponse(
                data=data,
                status_code=response.status_code,
                headers=dict(response.headers),
            )

        except requests.RequestException as e:
            # Return error response
            return BaseResponse(data={"error": str(e)}, status_code=0, headers={})


class PolarstepsClient:
    env_token: str = "POLARSTEPS_REMEMBER_TOKEN"
    base_url: str = "https://api.polarsteps.com"

    def __init__(
        self,
        remember_token: Optional[str] = None,
        cache_ttl: int = 300,  # 5 minutes,
        cache_maxsize: int = 1_000,
    ):
        if not remember_token:
            load_dotenv()
            remember_token = os.environ.get(self.env_token)
        if not remember_token:
            raise ValueError(
                "Remember token must be provided either directly or via configuration"
            )

        self.http_client = HTTPClient(
            base_url=self.base_url,
            remember_token=remember_token,
        )
        self._cache: TTLCache[str, Union[TripResponse, UserResponse]] = TTLCache(
            maxsize=cache_maxsize, ttl=cache_ttl
        )

    def get_trip(self, trip_id: str) -> TripResponse:
        # Check the cache first
        cached_response = self._cache.get(trip_id)
        if cached_response is not None and isinstance(cached_response, TripResponse):
            return cached_response

        # Cache miss - make the API call
        request = GetTripRequest(trip_id)
        response = self.http_client.execute(request)

        trip_response = TripResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if trip_response.is_success:
            self._cache[trip_id] = trip_response

        return trip_response

    def get_user_by_username(self, username: str) -> UserResponse:
        # Check the cache first
        cached_response = self._cache.get(username)
        if cached_response is not None and isinstance(cached_response, UserResponse):
            return cached_response

        # Cache miss - make the API call
        request = GetUserByUsernameRequest(username)
        response = self.http_client.execute(request)

        user_response = UserResponse(
            data=response.data,
            status_code=response.status_code,
            headers=response.headers,
        )

        # Avoid caching error responses
        if user_response.is_success:
            self._cache[username] = user_response

        return user_response
