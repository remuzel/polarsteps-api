"""Unit tests for Trip model and its to_summary methods."""

from polarsteps_api.models.trip import Location, MediaItem, Step, Trip, TripBuddy


class TestTripToSummary:
    """Test cases for Trip.to_summary() method."""

    def test_to_summary_basic_trip(self):
        """Test to_summary with basic trip data."""
        trip = Trip(
            id=123,
            uuid="test-uuid-123",
            name="Amazing European Adventure",
            summary="A wonderful journey through Europe",
            start_date=1640995200.0,  # 2022-01-01 00:00:00 UTC
            end_date=1641081600.0,  # 2022-01-02 00:00:00 UTC
            total_km=1500.5,
            step_count=10,
            country_count=3,
            views=250,
            like_count=15,
            cover_photo_path="/path/to/cover.jpg",
        )

        summary = trip.to_summary()

        assert summary["id"] == 123
        assert summary["name"] == "Amazing European Adventure"
        assert summary["summary"] == "A wonderful journey through Europe"
        assert summary["start_date"] == "2022/01/01"
        assert summary["end_date"] == "2022/01/02"
        assert summary["length_days"] == "2 days"
        assert summary["total_km"] == 1500.5
        assert summary["step_count"] == 10
        assert summary["country_count"] == 3
        assert summary["views"] == 250
        assert summary["like_count"] == 15
        assert summary["is_shared_trip"] is False  # No trip_buddies
        assert summary["cover_photo_path"] == "/path/to/cover.jpg"

    def test_to_summary_with_trip_buddies(self):
        """Test to_summary with trip buddies (shared trip)."""
        trip_buddies = [
            TripBuddy(buddy_user_id=1, uuid="buddy-1"),
            TripBuddy(buddy_user_id=2, uuid="buddy-2"),
        ]

        trip = Trip(
            id=456,
            uuid="shared-trip-uuid",
            name="Group Adventure",
            start_date=1640995200.0,
            trip_buddies=trip_buddies,
        )

        summary = trip.to_summary()

        assert summary["is_shared_trip"] is True
        assert summary["id"] == 456

    def test_to_summary_empty_trip_buddies(self):
        """Test to_summary with empty trip buddies list."""
        trip = Trip(
            id=789,
            uuid="solo-trip-uuid",
            name="Solo Journey",
            start_date=1640995200.0,
            trip_buddies=[],
        )

        summary = trip.to_summary()

        assert summary["is_shared_trip"] is False

    def test_to_summary_with_none_values(self):
        """Test to_summary handles None values gracefully."""
        trip = Trip(
            id=999,
            uuid="minimal-trip",
            name=None,
            summary=None,
            start_date=None,
            total_km=None,
            step_count=None,
            country_count=None,
            views=None,
            like_count=None,
            cover_photo_path=None,
        )

        summary = trip.to_summary()

        assert summary["id"] == 999
        assert summary["name"] is None
        assert summary["summary"] is None
        assert summary["total_km"] is None
        assert summary["step_count"] is None
        assert summary["country_count"] == 0
        assert summary["views"] is None
        assert summary["like_count"] is None
        assert summary["cover_photo_path"] is None

    def test_to_summary_multi_day_trip(self):
        """Test length_days calculation for multi-day trips."""
        trip = Trip(
            id=111,
            uuid="long-trip",
            start_date=1640995200.0,  # 2022-01-01
            end_date=1641686400.0,  # 2022-01-09 (9 days total)
        )

        summary = trip.to_summary()

        assert summary["length_days"] == "9 days"


class TestTripToDetailedSummary:
    """Test cases for Trip.to_detailed_summary() method."""

    def test_to_detailed_summary_basic(self):
        """Test to_detailed_summary with basic data."""
        # Create test steps with locations
        location1 = Location(name="Paris", country="France")
        location2 = Location(name="Rome", country="Italy")

        media_items = [
            MediaItem(id=1, uuid="media-1", type=1),
            MediaItem(id=2, uuid="media-2", type=2),
        ]

        steps = [
            Step(
                id=1,
                uuid="step-1",
                trip_id=123,
                location=location1,
                name="Paris Visit",
                description="Amazing visit to Paris",
                start_time=1640995200.0,
                media=media_items,
                is_deleted=False,
            ),
            Step(
                id=2,
                uuid="step-2",
                trip_id=123,
                location=location2,
                name="Rome Visit",
                description="Wonderful time in Rome",
                start_time=1641081600.0,
                media=[],
                is_deleted=False,
            ),
        ]

        trip_buddies = [TripBuddy(buddy_user_id=123, uuid="buddy-1")]

        trip = Trip(
            id=123,
            uuid="detailed-trip",
            name="European Tour",
            start_date=1640995200.0,
            all_steps=steps,
            trip_buddies=trip_buddies,
        )

        detailed_summary = trip.to_detailed_summary(n_steps=2)

        # Check that it includes basic summary fields
        assert detailed_summary["id"] == 123
        assert detailed_summary["name"] == "European Tour"

        # Check detailed fields
        assert len(detailed_summary["steps"]) == 2
        assert detailed_summary["steps"][0]["name"] == "Paris Visit"
        assert detailed_summary["steps"][0]["location"]["country"] == "France"
        assert detailed_summary["steps"][1]["name"] == "Rome Visit"
        assert detailed_summary["steps"][1]["location"]["country"] == "Italy"

        assert detailed_summary["trip_buddies_count"] == 1
        assert detailed_summary["media_count"] == 2  # 2 media items from first step

    def test_to_detailed_summary_with_deleted_steps(self):
        """Test that deleted steps are excluded from detailed summary."""
        steps = [
            Step(
                id=1,
                uuid="step-1",
                trip_id=123,
                name="Active Step",
                description="This step is active",
                is_deleted=False,
            ),
            Step(
                id=2,
                uuid="step-2",
                trip_id=123,
                name="Deleted Step",
                description="This step is deleted",
                is_deleted=True,
            ),
        ]

        trip = Trip(id=123, uuid="test-trip", all_steps=steps)

        detailed_summary = trip.to_detailed_summary()

        assert len(detailed_summary["steps"]) == 1
        assert detailed_summary["steps"][0]["name"] == "Active Step"

    def test_to_detailed_summary_steps_without_description(self):
        """Test that steps without description are excluded."""
        steps = [
            Step(
                id=1,
                uuid="step-1",
                trip_id=123,
                name="Step with description",
                description="Has description",
                is_deleted=False,
            ),
            Step(
                id=2,
                uuid="step-2",
                trip_id=123,
                name="Step without description",
                description="",
                is_deleted=False,
            ),
            Step(
                id=3,
                uuid="step-3",
                trip_id=123,
                name="Step with None description",
                description=None,
                is_deleted=False,
            ),
        ]

        trip = Trip(id=123, uuid="test-trip", all_steps=steps)

        detailed_summary = trip.to_detailed_summary()

        assert len(detailed_summary["steps"]) == 3
        assert detailed_summary["steps"][0]["name"] == "Step with description"

    def test_to_detailed_summary_limit_steps(self):
        """Test that num_steps parameter limits the number of steps returned."""
        steps = [
            Step(
                id=i,
                uuid=f"step-{i}",
                trip_id=123,
                name=f"Step {i}",
                description=f"Description {i}",
                is_deleted=False,
            )
            for i in range(1, 11)  # Create 10 steps
        ]

        trip = Trip(id=123, uuid="test-trip", all_steps=steps)

        detailed_summary = trip.to_detailed_summary(n_steps=3)

        assert len(detailed_summary["steps"]) == 3

    def test_to_detailed_summary_no_steps(self):
        """Test detailed summary with no steps."""
        trip = Trip(id=123, uuid="empty-trip", all_steps=[])

        detailed_summary = trip.to_detailed_summary()

        assert detailed_summary["steps"] == []
        assert detailed_summary["media_count"] == 0

    def test_to_detailed_summary_no_trip_buddies(self):
        """Test detailed summary with no trip buddies."""
        trip = Trip(id=123, uuid="solo-trip", trip_buddies=None)

        detailed_summary = trip.to_detailed_summary()

        assert detailed_summary["trip_buddies_count"] == 0

    def test_to_detailed_summary_step_location_fallback(self):
        """Test that step name is used when location is None."""
        steps = [
            Step(
                id=1,
                uuid="step-1",
                trip_id=123,
                name="Step Name Only",
                description="Has description",
                location=None,
                is_deleted=False,
            )
        ]

        trip = Trip(id=123, uuid="test-trip", all_steps=steps)

        detailed_summary = trip.to_detailed_summary()

        assert len(detailed_summary["steps"]) == 1
        assert detailed_summary["steps"][0]["name"] == "Step Name Only"
        assert detailed_summary["steps"][0]["location"] == {}


class TestTripProperties:
    """Test cases for Trip property methods used in summaries."""

    def test_datetime_properties(self):
        """Test datetime_start and datetime_end default properties."""
        trip = Trip(
            id=1,
            uuid="test",
            start_date=1640995200.0,  # 2022-01-01 00:00:00 UTC
        )

        assert trip.datetime_start.year == 2022
        assert trip.datetime_start.month == 1
        assert trip.datetime_start.day == 1

        assert trip.datetime_end.year == 1970
        assert trip.datetime_end.month == 1
        assert trip.datetime_end.day == 1

    def test_is_shared_trip_property(self):
        """Test is_shared_trip property with various scenarios."""
        # No trip buddies
        trip1 = Trip(id=1, uuid="test1", trip_buddies=None)
        assert trip1.is_shared_trip is False

        # Empty trip buddies list
        trip2 = Trip(id=2, uuid="test2", trip_buddies=[])
        assert trip2.is_shared_trip is False

        # With trip buddies
        buddies = [TripBuddy(buddy_user_id=1, uuid="buddy-1")]
        trip3 = Trip(id=3, uuid="test3", trip_buddies=buddies)
        assert trip3.is_shared_trip is True
