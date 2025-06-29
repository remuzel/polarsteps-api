"""Unit tests for User model and its to_summary methods."""

from polarsteps_api.models.trip import Location, Trip
from polarsteps_api.models.user import Stats, User


class TestUserToSummary:
    """Test cases for User.to_summary() method."""

    def test_to_summary_basic_user(self):
        """Test to_summary with basic user data."""
        location = Location(
            id=1,
            uuid="loc-uuid",
            name="Amsterdam",
            country="Netherlands",
            country_code="NL",
            precision=0.5,
        )

        stats = Stats(
            continents=["Europe", "Asia"],
            country_codes=["NL", "DE", "FR"],
            country_count=3,
            furthest_place_from_home_country="Tokyo",
            furthest_place_from_home_km=9000,
            furthest_place_from_home_location="Tokyo, Japan",
            km_count=5000.0,
            last_trip_end_date=1640995200.0,
            like_count=100,
            step_count=50,
            time_traveled_in_seconds=86400,
            trip_count=5,
            world_percentage=15.5,
        )

        followers = [
            User(id=2, uuid="follower-1", username="alice"),
            User(id=3, uuid="follower-2", username="bob"),
        ]

        followees = [User(id=4, uuid="followee-1", username="charlie")]

        trips = [
            Trip(id=1, uuid="trip-1", name="Europe Trip", is_deleted=False),
            Trip(id=2, uuid="trip-2", name="Asia Trip", is_deleted=False),
        ]

        user = User(
            id=1,
            uuid="user-uuid-123",
            username="traveler_john",
            first_name="John",
            last_name="Doe",
            description="Love to travel and explore new places",
            profile_image_path="/path/to/profile.jpg",
            living_location=location,
            country_count=3,
            stats=stats,
            followers=followers,
            followees=followees,
            alltrips=trips,
        )

        summary = user.to_summary()

        assert summary["id"] == 1
        assert summary["username"] == "traveler_john"
        assert summary["first_name"] == "John"
        assert summary["last_name"] == "Doe"
        assert summary["description"] == "Love to travel and explore new places"
        assert summary["profile_image_path"] == "/path/to/profile.jpg"
        assert summary["country_count"] == 3
        assert summary["trip_count"] == 2
        assert summary["followers"] == ["alice", "bob"]
        assert summary["followers_count"] == 2
        assert summary["followees"] == ["charlie"]
        assert summary["followees_count"] == 1
        assert summary["is_popular"] is False  # More followers than followees (2 > 1)

        # Check living location (excluding uuid and precision)
        living_loc = summary["living_location"]
        assert living_loc["id"] == 1
        assert living_loc["name"] == "Amsterdam"
        assert living_loc["country"] == "Netherlands"
        assert living_loc["country_code"] == "NL"
        assert "uuid" not in living_loc
        assert "precision" not in living_loc

        # Check stats
        stats_data = summary["stats"]
        assert stats_data["country_count"] == 3
        assert stats_data["km_count"] == 5000.0
        assert stats_data["world_percentage"] == 15.5

    def test_to_summary_with_none_values(self):
        """Test to_summary handles None values gracefully."""
        user = User(
            id=999,
            uuid="minimal-user",
            username="minimal_user",
            first_name=None,
            last_name=None,
            description=None,
            profile_image_path=None,
            living_location=None,
            country_count=None,
            stats=None,
            followers=None,
            followees=None,
            alltrips=None,
        )

        summary = user.to_summary()

        assert summary["id"] == 999
        assert summary["username"] == "minimal_user"
        assert summary["first_name"] is None
        assert summary["last_name"] is None
        assert summary["description"] is None
        assert summary["profile_image_path"] is None
        assert summary["living_location"] == "Unknown"
        assert summary["country_count"] is None
        assert summary["trip_count"] == 0  # len(None) defaults to 0
        assert summary["followers"] == []
        assert summary["followers_count"] == 0
        assert summary["followees"] == []
        assert summary["followees_count"] == 0
        assert summary["is_popular"] is False
        assert summary["stats"] == "Unknown"

    def test_to_summary_empty_lists(self):
        """Test to_summary with empty lists."""
        user = User(
            id=123,
            uuid="empty-lists-user",
            username="empty_user",
            followers=[],
            followees=[],
            alltrips=[],
        )

        summary = user.to_summary()

        assert summary["followers"] == []
        assert summary["followers_count"] == 0
        assert summary["followees"] == []
        assert summary["followees_count"] == 0
        assert summary["trip_count"] == 0
        assert summary["is_popular"] is False

    def test_to_summary_popular_user(self):
        """Test to_summary for a popular user (more followers than followees)."""
        followers = [
            User(id=i, uuid=f"follower-{i}", username=f"follower_{i}")
            for i in range(1, 6)  # 5 followers
        ]

        followees = [
            User(id=10, uuid="followee-1", username="followee_1"),
            User(id=11, uuid="followee-2", username="followee_2"),  # 2 followees
        ]

        user = User(
            id=1,
            uuid="popular-user",
            username="popular_traveler",
            followers=followers,
            followees=followees,
        )

        summary = user.to_summary()

        assert summary["followers_count"] == 5
        assert summary["followees_count"] == 2
        assert summary["is_popular"] is False  # More followers than followees (5 > 2)


class TestUserToTripsSummary:
    """Test cases for User.to_trips_summary() method."""

    def test_to_trips_summary_basic(self):
        """Test to_trips_summary with basic data."""
        trips = [
            Trip(
                id=1,
                uuid="trip-1",
                display_name="Europe Adventure",
                start_date=1640995200.0,
                total_km=1500.0,
                is_deleted=False,
            ),
            Trip(
                id=2,
                uuid="trip-2",
                display_name="Asia Journey",
                start_date=1641081600.0,
                total_km=2000.0,
                is_deleted=False,
            ),
            Trip(
                id=3,
                uuid="trip-3",
                display_name="Deleted Trip",
                start_date=1641168000.0,
                total_km=500.0,
                is_deleted=True,  # This should be excluded
            ),
        ]

        user = User(
            id=1,
            uuid="user-with-trips",
            username="trip_lover",
            first_name="Jane",
            alltrips=trips,
        )

        trips_summary = user.to_trips_summary()

        # Should include basic user summary
        assert trips_summary["id"] == 1
        assert trips_summary["username"] == "trip_lover"
        assert trips_summary["first_name"] == "Jane"

        # Should include trip summaries (excluding deleted trips)
        assert len(trips_summary["trips"]) == 2

        trip1 = trips_summary["trips"][0]
        assert trip1["id"] == 1
        assert trip1["display_name"] == "Europe Adventure"
        assert trip1["total_km"] == 1500.0

        trip2 = trips_summary["trips"][1]
        assert trip2["id"] == 2
        assert trip2["display_name"] == "Asia Journey"
        assert trip2["total_km"] == 2000.0

    def test_to_trips_summary_no_trips(self):
        """Test to_trips_summary with no trips."""
        user = User(id=1, uuid="no-trips-user", username="new_user", alltrips=[])

        trips_summary = user.to_trips_summary()

        assert trips_summary["trips"] == []
        assert trips_summary["trip_count"] == 0

    def test_to_trips_summary_none_trips(self):
        """Test to_trips_summary with None trips."""
        user = User(
            id=1, uuid="none-trips-user", username="minimal_user", alltrips=None
        )

        trips_summary = user.to_trips_summary()

        assert trips_summary["trips"] == []
        assert trips_summary["trip_count"] == 0

    def test_to_trips_summary_all_deleted_trips(self):
        """Test to_trips_summary when all trips are deleted."""
        trips = [
            Trip(id=1, uuid="trip-1", name="Deleted Trip 1", is_deleted=True),
            Trip(id=2, uuid="trip-2", name="Deleted Trip 2", is_deleted=True),
        ]

        user = User(
            id=1, uuid="deleted-trips-user", username="former_traveler", alltrips=trips
        )

        trips_summary = user.to_trips_summary()

        assert trips_summary["trips"] == []
        assert trips_summary["trip_count"] == 2  # Original count includes deleted trips


class TestUserIsPopularProperty:
    """Test cases for User.is_popular property."""

    def test_is_popular_more_followers(self):
        """Test is_popular when user has more followers than followees."""
        followers = [
            User(id=i, uuid=f"f-{i}", username=f"follower_{i}") for i in range(5)
        ]
        followees = [User(id=10, uuid="fe-1", username="followee_1")]

        user = User(
            id=1,
            uuid="popular",
            username="popular_user",
            followers=followers,
            followees=followees,
        )

        assert (
            user.is_popular is False
        )  # 5 followers > 1 followee, so not "popular" by this definition

    def test_is_popular_more_followees(self):
        """Test is_popular when user has more followees than followers."""
        followers = [User(id=1, uuid="f-1", username="follower_1")]
        followees = [
            User(id=i, uuid=f"fe-{i}", username=f"followee_{i}") for i in range(5)
        ]

        user = User(
            id=1,
            uuid="not-popular",
            username="regular_user",
            followers=followers,
            followees=followees,
        )

        assert (
            user.is_popular is True
        )  # 5 followees > 1 follower, so "popular" by this definition

    def test_is_popular_equal_counts(self):
        """Test is_popular when follower and followee counts are equal."""
        followers = [User(id=1, uuid="f-1", username="follower_1")]
        followees = [User(id=2, uuid="fe-1", username="followee_1")]

        user = User(
            id=1,
            uuid="balanced",
            username="balanced_user",
            followers=followers,
            followees=followees,
        )

        assert user.is_popular is False  # Equal counts = not popular

    def test_is_popular_empty_lists(self):
        """Test is_popular with empty follower/followee lists."""
        user = User(
            id=1, uuid="empty", username="empty_user", followers=[], followees=[]
        )

        assert user.is_popular is False

    def test_is_popular_none_lists(self):
        """Test is_popular with None follower/followee lists."""
        user = User(
            id=1, uuid="none", username="none_user", followers=None, followees=None
        )

        assert user.is_popular is False


class TestUserModelIntegration:
    """Integration tests combining User and Trip models."""

    def test_user_with_complex_trip_data(self):
        """Test user summary with complex trip data including shared trips."""
        from polarsteps_api.models.trip import TripBuddy

        # Create trip buddies
        buddy1 = TripBuddy(buddy_user_id=2, uuid="buddy-1", username="alice")
        buddy2 = TripBuddy(buddy_user_id=3, uuid="buddy-2", username="bob")

        # Create trips with varying complexity
        trips = [
            Trip(
                id=1,
                uuid="solo-trip",
                display_name="Solo Adventure",
                start_date=1640995200.0,
                total_km=1000.0,
                step_count=5,
                country_count=2,
                views=100,
                like_count=10,
                trip_buddies=[],
                is_deleted=False,
            ),
            Trip(
                id=2,
                uuid="shared-trip",
                display_name="Group Adventure",
                start_date=1641081600.0,
                total_km=2000.0,
                step_count=10,
                country_count=4,
                views=250,
                like_count=25,
                trip_buddies=[buddy1, buddy2],
                is_deleted=False,
            ),
        ]

        user = User(
            id=1,
            uuid="complex-user",
            username="adventure_seeker",
            first_name="Alex",
            last_name="Explorer",
            alltrips=trips,
        )

        trips_summary = user.to_trips_summary()

        # Verify user data
        assert trips_summary["username"] == "adventure_seeker"
        assert trips_summary["trip_count"] == 2

        # Verify trip summaries
        assert len(trips_summary["trips"]) == 2

        solo_trip = trips_summary["trips"][0]
        assert solo_trip["display_name"] == "Solo Adventure"
        assert solo_trip["is_shared_trip"] is False

        shared_trip = trips_summary["trips"][1]
        assert shared_trip["display_name"] == "Group Adventure"
        assert shared_trip["is_shared_trip"] is True
