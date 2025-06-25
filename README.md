# Polarsteps API Client

## Installation

### For development
```bash
uv sync --dev
uv run main.py
```
### Release [TBC]
```bash
pip install polarsteps-api
```

## Quick Start
```python
from polarsteps_api.client import PolarstepsClient
from polarsteps_api.models.response import TripResponse, UserResponse
from polarsteps_api.models.trip import Trip
from polarsteps_api.models.user import User

# Initialize the client
client = PolarstepsClient(remember_token = YOUR_TOKEN)

# Example User data
get_user_response: UserResponse = client.get_user_by_username(args.username)
user_data: User | None = get_user_response.user
if get_user_response.is_error or user_data is None:
    exit()
print(
    f"@{args.username} - {user_data.first_name} {user_data.last_name} [{user_data.country_count} countries / {int(user_data.stats.km_count):,}km]"
)

# Example Trip data
trip_id = (
    # Choose a random trip to get information about
    str(random.choice(user_data.alltrips).id)
    if len(user_data.alltrips or []) > 0 and user_data.alltrips is not None
    else args.trip_id
)
get_trip_response: TripResponse = client.get_trip(trip_id)
trip: Trip | None = get_trip_response.trip
if get_trip_response.is_error or trip is None:
    exit()
print(f"Random Trip - {(trip.name or 'Unknown').strip()} {int(trip.total_km):,}km")  # type: ignore
```

## Remember Tokens
The API client relies on an authenticated token, for which you must be an active Polarsteps customer. To obtain this:
1. Log in to [Polarsteps](https://www.polarsteps.com/) in your browser
2. Open browser developer tools (F12)
3. Go to Application/Storage tab → Cookies
4. Find the `POLARSTEPS_REMEMBER_TOKEN` cookie value
5. Copy this value to use with the client

## Supported APIs
1. `get_user_by_username` - Fetch complete user profile including trips, statistics, followers, and followees
2. `get_trip` - Get detailed information for individual trips by ID
3. _more tbd!_
