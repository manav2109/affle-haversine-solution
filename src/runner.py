import os
import time
import psutil
import pandas as pd
from tqdm import tqdm
from .processor import RestaurantProcessor


class BatchRunner:
    def __init__(self, restaurant_file, output_dir="results", static_time="12:00:00",
                 benchmark_log="benchmark_results.csv"):
        """
        Initializes the BatchRunner with file paths, time parameters, and optional benchmarking log.

        :param restaurant_file: Path to the restaurant data CSV.
        :param output_dir: Directory to store result CSVs.
        :param static_time: Static time string used to check restaurant availability.
        :param benchmark_log: Optional filename to save benchmarking results.
        """
        self.restaurant_file = restaurant_file
        self.output_dir = output_dir
        self.processor = RestaurantProcessor(static_time)
        self.benchmark_log = os.path.join(output_dir, benchmark_log)
        self.benchmark_records = []

    def run(self, user_file_paths):
        """
        Runs the restaurant matching process on a list of user files and logs performance.

        :param user_file_paths: List of user CSV file paths.
        :return: None. Saves results and optionally benchmark log.
        """
        total_start = time.time()
        os.makedirs(self.output_dir, exist_ok=True)
        restaurants_df = pd.read_csv(self.restaurant_file)

        for user_file in tqdm(user_file_paths, desc="Processing Files"):
            file_start = time.time()
            memory_before = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2

            users_df = pd.read_csv(user_file)
            user_count = len(users_df)

            result_df = self.processor.find_available_restaurants(users_df, restaurants_df)

            memory_after = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            file_end = time.time()

            match_count = result_df["Available_restaurant_count"].sum() if not result_df.empty else 0
            result_rows = len(result_df)

            output_file = os.path.splitext(os.path.basename(user_file))[0] + "_results.csv"
            if not result_df.empty:
                result_df.to_csv(os.path.join(self.output_dir, output_file), index=False)

            self.benchmark_records.append({
                "User_File": os.path.basename(user_file),
                "User_Count": user_count,
                "Time_Taken_Seconds": round(file_end - file_start, 3),
                "Memory_MB_Before": round(memory_before, 2),
                "Memory_MB_After": round(memory_after, 2),
                "Matched_Rows": result_rows,
                "Total_Matches": int(match_count),
                "Output_File": output_file if not result_df.empty else "None"
            })

        total_end = time.time()
        print(f"\nTotal time: {round(total_end - total_start, 2)}s")

        pd.DataFrame(self.benchmark_records).to_csv(self.benchmark_log, index=False)
        print(f"Benchmark log saved to: {self.benchmark_log}")
