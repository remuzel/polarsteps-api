from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from pydantic import BaseModel, field_validator, model_validator

if TYPE_CHECKING:
    from polarsteps_api.models.user import User


class CoverPhoto(BaseModel):
    id: int
    uuid: str
    path: Optional[str] = None
    small_thumbnail_path: Optional[str] = None
    large_thumbnail_path: Optional[str] = None
    type: Optional[int] = None
    full_res_unavailable: Optional[bool] = False
    last_modified: Optional[float] = None
    trip_id: Optional[int] = None
    media_id: Optional[int] = None

    @field_validator("last_modified", mode="before")
    @classmethod
    def validate_last_modified(cls, v: Any) -> Any:
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


class Location(BaseModel):
    id: Optional[int] = None
    uuid: Optional[str] = None
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    detail: Optional[str] = None
    full_detail: Optional[str] = None
    administrative_area: Optional[str] = None
    locality: Optional[str] = None
    precision: Optional[float] = None


class MediaItem(BaseModel):
    id: int
    uuid: str
    type: int
    path: Optional[str] = None
    cdn_path: Optional[str] = None
    small_thumbnail_path: Optional[str] = None
    large_thumbnail_path: Optional[str] = None
    full_res_width: Optional[float] = None
    full_res_height: Optional[float] = None
    full_res_unavailable: Optional[bool] = False
    aspect_ratio: Optional[float] = None
    description: Optional[str] = None
    duration: Optional[float] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    order: Optional[int] = None
    step_id: Optional[int] = None
    is_deleted: Optional[bool] = False


class Step(BaseModel):
    id: int
    uuid: str
    trip_id: int
    location: Optional[Location] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    slug: Optional[str] = None
    display_slug: Optional[str] = None
    description: Optional[str] = None
    creation_time: Optional[float] = None
    type: Optional[int] = None
    supertype: Optional[str] = None
    timezone_id: Optional[str] = None
    weather_condition: Optional[str] = None
    weather_temperature: Optional[float] = None
    views: Optional[int] = 0
    comment_count: Optional[int] = 0
    location_id: Optional[int] = None
    is_deleted: Optional[bool] = False
    fb_publish_status: Optional[str] = None
    open_graph_id: Optional[str] = None
    main_media_item_path: Optional[str] = None
    media: Optional[list[MediaItem]] = []
    user_likes: Optional[list[dict[str, Any]]] = []

    def to_summary(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "timestamp": datetime.fromtimestamp(self.creation_time or 0).strftime(
                "%Y/%m/%d %H:%M:%S"
            ),
            "location": self.location.model_dump(
                exclude={"uuid", "precision", "full_detail", "administrative_area"}
            )
            if self.location
            else {},
            "weather": {
                "condition": self.weather_condition,
                "temperature": self.weather_temperature,
            },
            "views": self.views,
            "comments": self.comment_count,
            "likes": len(self.user_likes or []),
        }


class TravelTrackerDevice(BaseModel):
    id: int
    uuid: str
    device_name: Optional[str] = None
    trip_id: Optional[int] = None
    tracking_status: Optional[int] = None
    enabled: Optional[bool] = None


class TripBuddy(BaseModel):
    """Simplified model for trip buddies that come as limited dictionaries"""

    buddy_user_id: int
    uuid: str
    username: Optional[str] = (
        None  # Make username optional since it's missing from API response
    )


# TODO - Figure out circular dependencies (with User and Trip)
class Trip(BaseModel):
    id: int
    uuid: str
    name: Optional[str] = None
    display_name: Optional[str] = None
    slug: Optional[str] = None
    display_slug: Optional[str] = None
    summary: Optional[str] = None
    start_date: Optional[float] = None
    end_date: Optional[float] = None
    creation_time: Optional[float] = None
    last_modified: Optional[float] = None
    total_km: Optional[float] = 0.0
    step_count: Optional[int] = 0
    views: Optional[int] = 0
    visibility: Optional[int] = None
    timezone_id: Optional[str] = None
    cover_photo: Optional[CoverPhoto] = None
    cover_photo_path: Optional[str] = None
    cover_photo_thumb_path: Optional[str] = None
    user_id: Optional[int] = None
    user: Optional["User"] = None
    all_steps: Optional[list[Step]] = []
    travel_tracker_device: Optional[TravelTrackerDevice] = None
    is_deleted: Optional[bool] = False
    language: Optional[str] = None
    type: Optional[int] = None
    fb_publish_status: Optional[str] = None
    feature_date: Optional[float] = None
    feature_text: Optional[str] = None
    featured: Optional[bool] = None
    featured_priority_for_new_users: Optional[int] = None
    future_timeline_last_modified: Optional[float] = None
    open_graph_id: Optional[str] = None
    planned_steps_visible: Optional[bool] = True
    synchronized: Optional[bool] = None
    country_count: Optional[int] = 0
    like_count: Optional[int] = 0
    quality_score: Optional[float] = None
    has_ordered_travel_book: Optional[bool] = None
    mashup_user_id: Optional[int] = None
    meta_data: Optional[dict[str, Any]] = {}
    planned_countries: Optional[list[dict[str, Any]]] = []
    planned_steps: Optional[list["Step"]] = []
    route_segments: Optional[list[dict[str, Any]]] = []
    trip_buddies: Optional[list[TripBuddy]] = []
    trip_buddies_accepted_invited: Optional[list[TripBuddy]] = []

    @field_validator(
        "start_date",
        "end_date",
        "creation_time",
        "last_modified",
        "future_timeline_last_modified",
        mode="before",
    )
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

    @model_validator(mode="after")
    def validate_country_count(self) -> "Trip":
        """Override the default country_count method which seems invalid"""
        if self.country_count and self.country_count > 0:
            # If the field seems correctly set, keep it
            return self
        if self.all_steps is None:
            # If there are no steps, set it to 0
            self.country_count = 0
            return self
        countries = set()
        for step in self.all_steps:
            # Aggregate the countries from each step
            if step and step.location and step.location.country_code:
                countries.add(step.location.country_code)

        self.country_count = len(countries)
        return self

    @property
    def datetime_start(self) -> datetime:
        return datetime.fromtimestamp(self.start_date or 0)

    @property
    def datetime_end(self) -> datetime:
        return datetime.fromtimestamp(self.end_date or 0)

    @property
    def length_days(self) -> str:
        length = (self.datetime_end - self.datetime_start).days + 1
        return f"{length} day{'' if length == 1 else 's'}"

    @property
    def is_shared_trip(self) -> Optional[bool]:
        buddies = self.trip_buddies
        return buddies is not None and len(buddies) > 0

    def to_summary(self) -> dict:
        """Return a compact summary of the trip"""
        y_m_d_format = "%Y/%m/%d"
        return {
            "id": self.id,
            "name": self.name,
            "summary": self.summary,
            "start_date": self.datetime_start.strftime(y_m_d_format),
            "end_date": self.datetime_end.strftime(y_m_d_format),
            "length_days": self.length_days,
            "total_km": self.total_km,
            "step_count": self.step_count,
            "country_count": self.country_count,
            "views": self.views,
            "like_count": self.like_count,
            "is_shared_trip": self.is_shared_trip,
            "cover_photo_path": self.cover_photo_path,
        }

    def to_detailed_summary(self, n_steps: int = 5) -> dict:
        """Return a more detailed summary including key steps"""
        steps = (
            [
                step
                for step in self.all_steps
                if len(step.name or "") > 0 and not step.is_deleted
            ]
            if self.all_steps
            else []
        )
        summary = self.to_summary()
        summary.update(
            {
                "steps": [step.to_summary() for step in steps[:n_steps]],
                "trip_buddies": [buddy.username for buddy in (self.trip_buddies or [])],
                "trip_buddies_count": len(self.trip_buddies or []),
                "media_count": sum(
                    len(step.media or []) for step in (self.all_steps or [])
                ),
            }
        )
        return summary
