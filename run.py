from src.runner import BatchRunner

if __name__ == "__main__":
    user_files = [
        "data/input/users_1_10.csv",
        "data/input/users_11_100.csv",
        "data/input/users_101_1000.csv",
        "data/input/users_1001_100000.csv",
        "data/input/users_100001_1000000.csv"
    ]
    runner = BatchRunner("data/input/restaurants.csv", output_dir="data/output")
    runner.run(user_files)
