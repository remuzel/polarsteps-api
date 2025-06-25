from .request import GetTripRequest, GetUserByUsernameRequest
from .response import TripResponse, UserResponse
from .trip import Location, MediaItem, Step, TravelTrackerDevice, Trip
from .user import Stats, User

# Rebuild models to resolve forward references
User.model_rebuild()
Trip.model_rebuild()

__all__ = [
    "GetTripRequest",
    "GetUserByUsernameRequest",
    "TripResponse",
    "UserResponse",
    "Location",
    "MediaItem",
    "Step",
    "TravelTrackerDevice",
    "Trip",
    "User",
    "Stats",
]
