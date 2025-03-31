import pandas as pd
import numpy as np
import os

RESTAURANT_PATH = "../data/input/restaurants.csv"
"""
Path to the restaurants CSV file. This file contains restaurant location and metadata.
"""

OUTPUT_DIR = "../data/input"
"""
Directory to save generated user files. These files will serve as input for restaurant lookup.
"""

np.random.seed(42)

STAGES = [
    (1, 10),
    (11, 100),
    (101, 1000),
    (1001, 100000),
    (100001, 1000000)
]
"""
Defines ranges of user counts to simulate. Each tuple specifies a (start, end) range.
"""


def generate_users_near_restaurants(restaurants_df, count, noise=0.01):
    """
    Generates synthetic user data near a randomly selected restaurant.

    :param restaurants_df: DataFrame containing restaurant latitude and longitude.
    :param count: Number of user records to generate.
    :param noise: Standard deviation of the noise applied to latitude and longitude for random spread.
    :return: DataFrame with columns ['USER_LATITUDE', 'USER_LONGITUDE']
    """
    sample = restaurants_df[['latitude', 'longitude']].dropna().sample(1)
    lat, lon = sample.iloc[0]
    user_lats = lat + np.random.normal(scale=noise, size=count)
    user_lons = lon + np.random.normal(scale=noise, size=count)
    return pd.DataFrame({
        "USER_LATITUDE": user_lats,
        "USER_LONGITUDE": user_lons
    })


def main():
    """
    Main entry point to generate synthetic user data files.

    - Creates output directory if not exists.
    - Loads restaurant data.
    - Generates and saves user files for each defined stage in STAGES.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    restaurants_df = pd.read_csv(RESTAURANT_PATH)

    for start, end in STAGES:
        count = end - start + 1
        users_df = generate_users_near_restaurants(restaurants_df, count)
        filename = f"{OUTPUT_DIR}/users_{start}_{end}.csv"
        users_df.to_csv(filename, index=False)
        print(f"Generated: {filename}")


if __name__ == "__main__":
    main()
