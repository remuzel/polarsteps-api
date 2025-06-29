import argparse
import random

from dotenv import load_dotenv

from polarsteps_api.client import PolarstepsClient
from polarsteps_api.models.response import TripResponse, UserResponse
from polarsteps_api.models.trip import Trip
from polarsteps_api.models.user import User

load_dotenv()


def main():
    parser = argparse.ArgumentParser(description="Polarsteps API Client Demo")
    parser.add_argument("--username", help="Polarsteps username", required=True)
    parser.add_argument("--trip-id", help="Specific trip ID to fetch")

    args = parser.parse_args()

    print("Hello from polarsteps-api!")
    client = PolarstepsClient()
    get_user_response: UserResponse = client.get_user_by_username(args.username)
    user_data: User | None = get_user_response.user
    if get_user_response.is_error or user_data is None:
        exit()
    print(
        f"@{args.username} - {user_data.first_name} {user_data.last_name} [{user_data.country_count} countries / {int(user_data.stats.km_count):,}km]"  # type: ignore
    )
    print(f"\t{user_data.to_summary()}")
    with open(f"data/{args.username}.json", "w") as f:
        f.write(user_data.model_dump_json(indent=4))

    trip_id = (
        str(random.choice(user_data.alltrips).id)
        if len(user_data.alltrips or []) > 0 and user_data.alltrips is not None
        else args.trip_id
    )
    get_trip_response: TripResponse = client.get_trip(trip_id)
    trip: Trip | None = get_trip_response.trip
    if get_trip_response.is_error or trip is None:
        exit()
    print(f"Random Trip - {(trip.name or 'Unknown').strip()} {int(trip.total_km):,}km")  # type: ignore
    print(f"\t{trip.to_detailed_summary()}")
    with open(f"data/{args.username}-{trip.slug}.json", "w") as f:
        f.write(trip.model_dump_json(indent=4))


if __name__ == "__main__":
    main()
