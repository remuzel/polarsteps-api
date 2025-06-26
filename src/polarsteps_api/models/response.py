from typing import Any, Optional

from polarsteps_api.models.base import BaseResponse
from polarsteps_api.models.trip import Trip
from polarsteps_api.models.user import User


class TripResponse(BaseResponse):
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]) -> None:
        super().__init__(data, status_code, headers)
        # Only create Trip model if response is successful and data is valid
        if self.is_success and data:
            try:
                self.trip: Optional[Trip] = Trip(**data)
            except Exception as e:
                print("Failed to serialize TripResponse: ", e)
                self.trip = None
        else:
            self.trip = None


class UserResponse(BaseResponse):
    def __init__(self, data: Any, status_code: int, headers: dict[str, str]) -> None:
        super().__init__(data, status_code, headers)
        # Only create UserData model if response is successful and data is valid
        if self.is_success and data:
            try:
                self.user: Optional[User] = User(**data)
            except Exception as e:
                print("Failed to serialize UserResponse: ", e)
                self.user = None
        else:
            self.user = None
