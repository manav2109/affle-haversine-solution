import pandas as pd
import numpy as np
from sklearn.neighbors import BallTree
from datetime import datetime
from joblib import Parallel, delayed, cpu_count
from tqdm import tqdm

EARTH_RADIUS_KM = 6371.0


class RestaurantProcessor:
    def __init__(self, static_time="12:00:00"):
        """
        Initializes the RestaurantProcessor with a static time used for restaurant availability checks.

        :param static_time: Time string in HH:MM:SS format used to filter open restaurants.
        """
        self.static_time = static_time

    def is_open(self, row, current_time):
        """
        Determines whether a restaurant is open at the specified time.

        Handles overnight hours by checking if closing time is before opening time.

        :param row: A DataFrame row with 'open_hour' and 'close_hour' fields.
        :param current_time: A datetime.time object representing the current time to compare.
        :return: True if the restaurant is open, False otherwise.
        """
        try:
            open_time = datetime.strptime(row['open_hour'], "%H:%M:%S").time()
            close_time = datetime.strptime(row['close_hour'], "%H:%M:%S").time()
            if open_time < close_time:
                return open_time <= current_time <= close_time
            else:
                return current_time >= open_time or current_time <= close_time
        except:
            return False

    def process_user_batch(self, user_coords_batch, lat_batch, lon_batch, open_coords, open_ids, open_radii):
        """
            Processes a batch of user coordinates to find matching restaurants within availability radius.

            Uses BallTree with haversine distance metric to efficiently find nearby restaurants.

            :param user_coords_batch: Array of user coordinates (in radians).
            :param lat_batch: Original user latitudes (degrees) for output.
            :param lon_batch: Original user longitudes (degrees) for output.
            :param open_coords: Array of open restaurant coordinates (in radians).
            :param open_ids: Array of restaurant IDs.
            :param open_radii: Array of restaurant radii (in radians).
            :return: List of results per user containing lat, lon, match count, and matched restaurant IDs.
            """
        results = []
        tree = BallTree(open_coords, metric='haversine')
        indices_list = tree.query_radius(user_coords_batch, r=open_radii.max())

        for i, indices in enumerate(indices_list):
            user_coord = user_coords_batch[i]
            candidates = open_coords[indices].astype(np.float32)
            candidate_radii = open_radii[indices].astype(np.float32)
            candidate_ids = open_ids[indices]

            dlat = candidates[:, 0] - user_coord[0]
            dlon = candidates[:, 1] - user_coord[1]
            a = np.sin(dlat / 2) ** 2 + np.cos(user_coord[0]) * np.cos(candidates[:, 0]) * np.sin(dlon / 2) ** 2
            c = 2 * np.arcsin(np.clip(np.sqrt(a), 0, 1))

            matched_ids = candidate_ids[c <= candidate_radii].astype(str)
            results.append([
                lat_batch[i],
                lon_batch[i],
                len(matched_ids),
                ";".join(np.sort(matched_ids)) if len(matched_ids) else ""
            ])

        return results

    def find_available_restaurants(self, users_df, restaurants_df):
        """
        Filters restaurants based on current time and finds available ones for each user.

        Splits users into batches and uses parallel processing to find restaurants within reach.

        :param users_df: DataFrame containing user locations with 'USER_LATITUDE' and 'USER_LONGITUDE'.
        :param restaurants_df: DataFrame containing restaurant info including location, hours, and radius.
        :return: A DataFrame with user location, count of available restaurants, and matched restaurant IDs.
        """
        users_df = users_df[['USER_LATITUDE', 'USER_LONGITUDE']].copy()
        restaurants_df = restaurants_df[
            ['id', 'latitude', 'longitude', 'availability_radius', 'open_hour', 'close_hour']].copy()

        user_coords = np.radians(users_df.to_numpy(dtype=np.float32))
        lat_array, lon_array = users_df['USER_LATITUDE'].to_numpy(), users_df['USER_LONGITUDE'].to_numpy()

        restaurants_df.dropna(subset=['latitude', 'longitude'], inplace=True)
        restaurants_df['lat_rad'] = np.radians(restaurants_df['latitude'].astype(np.float32))
        restaurants_df['lon_rad'] = np.radians(restaurants_df['longitude'].astype(np.float32))

        time_check = datetime.strptime(self.static_time, "%H:%M:%S").time()
        restaurants_df = restaurants_df[restaurants_df.apply(lambda row: self.is_open(row, time_check), axis=1)]

        if restaurants_df.empty:
            print("No open restaurants at given time.")
            return pd.DataFrame()

        open_coords = restaurants_df[['lat_rad', 'lon_rad']].to_numpy(dtype=np.float32)
        open_ids = restaurants_df['id'].to_numpy()
        open_radii = restaurants_df['availability_radius'].to_numpy(dtype=np.float32) / EARTH_RADIUS_KM

        batch_size = 5000
        batches = [(user_coords[i:i + batch_size], lat_array[i:i + batch_size], lon_array[i:i + batch_size],
                    open_coords, open_ids, open_radii)
                   for i in range(0, len(user_coords), batch_size)]

        all_results = Parallel(n_jobs=cpu_count())(
            delayed(self.process_user_batch)(*args) for args in tqdm(batches, desc="Processing Users")
        )

        flat_results = [item for sublist in all_results for item in sublist]
        return pd.DataFrame(flat_results, columns=["User_latitude", "User_Longitude", "Available_restaurant_count",
                                                   "Restaurant_Id's"])
