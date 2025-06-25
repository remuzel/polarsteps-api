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

    @property
    def is_shared_trip(self) -> Optional[bool]:
        if not self.trip:
            return None
        buddies = self.trip.trip_buddies
        return buddies is not None and len(buddies) > 0


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

    @property
    def is_popular(self) -> bool:
        if not self.user:
            return False
        n_followers = len(self.user.followers or [])
        n_followees = len(self.user.followees or [])
        return n_followees > n_followers
