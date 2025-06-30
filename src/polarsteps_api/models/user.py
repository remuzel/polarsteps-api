from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, Union

from pydantic import BaseModel, field_validator

if TYPE_CHECKING:
    from polarsteps_api.models.trip import Location, Trip


class Stats(BaseModel):
    continents: list[str]
    country_codes: list[str]
    country_count: int
    furthest_place_from_home_country: Optional[str]
    furthest_place_from_home_km: Optional[int]
    furthest_place_from_home_location: Optional[str]
    km_count: Optional[Union[str, float]]
    last_trip_end_date: Optional[float]
    like_count: Optional[int]
    step_count: Optional[int]
    time_traveled_in_seconds: Optional[int]
    trip_count: Optional[int]
    world_percentage: Optional[float]

    @field_validator("last_trip_end_date", mode="before")
    @classmethod
    def validate_timestamps(cls, v: Any) -> Any:
        """Validate timestamp fields."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                # Parse ISO datetime string to timestamp
                dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                return dt.timestamp()
            except ValueError:
                # If parsing fails, try to return as is
                return v
        if isinstance(v, (int, float)) and v < 0:
            raise ValueError("Timestamp cannot be negative")
        return v


class User(BaseModel):
    id: int
    uuid: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None
    profile_image_path: Optional[str] = None
    profile_image_thumb_path: Optional[str] = None
    living_location: Optional["Location"] = None
    living_location_id: Optional[int] = None
    living_location_name: Optional[str] = None
    locale: Optional[str] = None
    visibility: Optional[int] = None
    creation_date: Optional[float] = None
    temperature_is_celsius: Optional[bool] = True
    unit_is_km: Optional[bool] = True
    country_count: Optional[int] = 0
    country_count_public: Optional[int] = 0
    country_count_followers: Optional[int] = 0
    has_multiple_devices: Optional[bool] = False
    fb_id: Optional[str] = None
    google_id: Optional[str] = None
    last_modified: Optional[float] = None
    synchronized: Optional[bool] = None
    mashup: Optional[Union[bool, dict[str, Any]]] = None
    mashup_user_id: Optional[int] = None
    traveller_type: Optional[str] = None
    currency: Optional[str] = None
    saved_spots: Optional[list[dict[str, Any]]] = []
    stats: Optional["Stats"] = None
    followers: Optional[list["User"]] = []
    followees: Optional[list["User"]] = []
    follow_requests: Optional[list["User"]] = []
    sent_follow_requests: Optional[list["User"]] = []
    alltrips: Optional[list["Trip"]] = []

    @field_validator("creation_date", "last_modified", mode="before")
    @classmethod
    def validate_timestamps(cls, v: Any) -> Any:
        """Validate timestamp fields."""
        if v is None:
            return v
        if isinstance(v, str):
            try:
                # Parse ISO datetime string to timestamp
                dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
                return dt.timestamp()
            except ValueError:
                # If parsing fails, try to return as is
                return v
        if isinstance(v, (int, float)) and v < 0:
            raise ValueError("Timestamp cannot be negative")
        return v

    @property
    def is_popular(self) -> bool:
        n_followers = len(self.followers or [])
        n_followees = len(self.followees or [])
        return n_followees > n_followers

    def to_summary(self) -> dict:
        """Return a compact summary of the user"""
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "description": self.description,
            "profile_image_path": self.profile_image_path,
            "living_location": self.living_location.model_dump(
                exclude={"uuid", "precision"}
            )
            if self.living_location
            else "Unknown",
            "country_count": self.country_count,
            "trip_count": len(self.alltrips or []),
            "followers": [follower.username for follower in (self.followers or [])],
            "followers_count": len(self.followers or []),
            "followees": [followee.username for followee in (self.followees or [])],
            "followees_count": len(self.followees or []),
            "is_popular": self.is_popular,
            "stats": self.stats.model_dump() if self.stats else "Unknown",
        }

    def to_trips_summary(self) -> dict:
        """Return user info with trip summaries only"""
        summary = self.to_summary()
        summary["trips"] = [
            trip.to_summary() for trip in (self.alltrips or []) if not trip.is_deleted
        ]
        return summary
