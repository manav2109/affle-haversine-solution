import pandas as pd
import os
import tempfile
from datetime import datetime
from src.processor import RestaurantProcessor
from src.runner import BatchRunner

"""
Unit tests for the RestaurantProcessor and BatchRunner classes.

Tests include:
- Restaurant open/close logic (basic, overnight, invalid formats)
- Radius filtering and user-to-restaurant matching
- Output file creation and empty result cases
"""


def test_is_open_basic():
    """Test if restaurant is correctly marked as open within standard hours."""
    processor = RestaurantProcessor(static_time="12:00:00")
    test_row = {
        'open_hour': '10:00:00',
        'close_hour': '18:00:00'
    }
    assert processor.is_open(test_row, datetime.strptime("12:00:00", "%H:%M:%S").time())


def test_is_open_overnight():
    """Test restaurant open logic across midnight (e.g., 22:00 to 06:00)."""
    processor = RestaurantProcessor(static_time="03:00:00")
    test_row = {
        'open_hour': '22:00:00',
        'close_hour': '06:00:00'
    }
    assert processor.is_open(test_row, datetime.strptime("03:00:00", "%H:%M:%S").time())


def test_is_open_invalid_time_format():
    """Ensure invalid time formats do not crash the method and return False."""
    processor = RestaurantProcessor()
    test_row = {
        'open_hour': 'invalid_time',
        'close_hour': 'invalid_time'
    }
    assert processor.is_open(test_row, datetime.now().time()) is False


def test_find_available_restaurants_single_match():
    """Test that one restaurant within radius is matched to a user."""
    users = pd.DataFrame({
        "USER_LATITUDE": [-34.60],
        "USER_LONGITUDE": [-58.40]
    })

    restaurants = pd.DataFrame({
        "id": [1],
        "latitude": [-34.60],
        "longitude": [-58.40],
        "availability_radius": [2.0],
        "open_hour": ["00:00:00"],
        "close_hour": ["23:59:59"]
    })

    processor = RestaurantProcessor(static_time="12:00:00")
    result = processor.find_available_restaurants(users, restaurants)

    assert result.shape[0] == 1
    assert result["Available_restaurant_count"].iloc[0] == 1
    assert "1" in result["Restaurant_Id's"].iloc[0]


def test_find_available_restaurants_no_match_due_to_time():
    """Test filtering out restaurant due to time constraint (not open at query time)."""
    users = pd.DataFrame({
        "USER_LATITUDE": [-34.60],
        "USER_LONGITUDE": [-58.40]
    })

    restaurants = pd.DataFrame({
        "id": [2],
        "latitude": [-34.60],
        "longitude": [-58.40],
        "availability_radius": [2.0],
        "open_hour": ["20:00:00"],
        "close_hour": ["23:00:00"]
    })

    processor = RestaurantProcessor(static_time="12:00:00")
    result = processor.find_available_restaurants(users, restaurants)

    assert result.shape[0] == 0 or result["Available_restaurant_count"].iloc[0] == 0


def test_find_available_restaurants_all_out_of_radius():
    """Ensure no restaurants are matched if all are outside radius."""
    users = pd.DataFrame({
        "USER_LATITUDE": [-34.60],
        "USER_LONGITUDE": [-58.40]
    })

    restaurants = pd.DataFrame({
        "id": [3],
        "latitude": [-35.00],
        "longitude": [-58.90],
        "availability_radius": [1.0],
        "open_hour": ["00:00:00"],
        "close_hour": ["23:59:59"]
    })

    processor = RestaurantProcessor(static_time="12:00:00")
    result = processor.find_available_restaurants(users, restaurants)

    assert result.shape[0] == 1
    assert result["Available_restaurant_count"].iloc[0] == 0
    assert result["Restaurant_Id's"].iloc[0] == ""


def test_no_restaurants_open():
    """Verify behavior when no restaurants are open at the static time."""
    users = pd.DataFrame({
        "USER_LATITUDE": [-34.60],
        "USER_LONGITUDE": [-58.40]
    })

    restaurants = pd.DataFrame({
        "id": [4],
        "latitude": [-34.60],
        "longitude": [-58.40],
        "availability_radius": [2.0],
        "open_hour": ["00:00:00"],
        "close_hour": ["01:00:00"]
    })

    processor = RestaurantProcessor(static_time="12:00:00")
    result = processor.find_available_restaurants(users, restaurants)

    assert result.empty


def test_runner_creates_output_file():
    """Test that BatchRunner correctly creates a results file with valid data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        input_user_path = os.path.join(temp_dir, "users.csv")
        input_rest_path = os.path.join(temp_dir, "restaurants.csv")
        output_dir = os.path.join(temp_dir, "output")

        users = pd.DataFrame({
            "USER_LATITUDE": [-34.60],
            "USER_LONGITUDE": [-58.40]
        })
        users.to_csv(input_user_path, index=False)

        restaurants = pd.DataFrame({
            "id": [1],
            "latitude": [-34.60],
            "longitude": [-58.40],
            "availability_radius": [2.0],
            "open_hour": ["00:00:00"],
            "close_hour": ["23:59:59"]
        })
        restaurants.to_csv(input_rest_path, index=False)

        runner = BatchRunner(restaurant_file=input_rest_path, output_dir=output_dir)
        runner.run([input_user_path])

        output_file = os.path.join(output_dir, "users_results.csv")
        assert os.path.exists(output_file)
        result_df = pd.read_csv(output_file)
        assert result_df.shape[0] == 1
        assert result_df["Available_restaurant_count"].iloc[0] == 1


def test_no_restaurant_matches_any_user():
    """Test case where user is too far from any restaurant (no matches)."""
    users = pd.DataFrame({
        "USER_LATITUDE": [10.0],
        "USER_LONGITUDE": [10.0]
    })

    restaurants = pd.DataFrame({
        "id": [99],
        "latitude": [80.0],
        "longitude": [80.0],
        "availability_radius": [1.0],
        "open_hour": ["00:00:00"],
        "close_hour": ["23:59:59"]
    })

    processor = RestaurantProcessor(static_time="12:00:00")
    result = processor.find_available_restaurants(users, restaurants)

    assert result.shape[0] == 1
    assert result["Available_restaurant_count"].iloc[0] == 0
    assert result["Restaurant_Id's"].iloc[0] == ""
