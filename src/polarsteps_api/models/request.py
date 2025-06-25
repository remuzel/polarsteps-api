from typing import Any

from polarsteps_api.models.base import BaseRequest


class GetTripRequest(BaseRequest):
    def __init__(self, trip_id: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.trip_id = trip_id

    def get_endpoint(self) -> str:
        return f"/trips/{self.trip_id}"

    def get_method(self) -> str:
        return "GET"


class GetUserByUsernameRequest(BaseRequest):
    def __init__(self, username: str, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.username = username

    def get_endpoint(self) -> str:
        return f"/users/byusername/{self.username}"

    def get_method(self) -> str:
        return "GET"
