### Problem Overview

**Problem**: Get the restaurant IDs that are eligible to deliver to a particular user's location, based on:
- User's coordinates (latitude & longitude)
- Whether the restaurant is currently open (within open and close time)
- Whether the restaurant is within delivery radius (Haversine distance)

---

### Solution Architecture

**Dependencies:**
- `pandas`, `numpy`, `scikit-learn`, `joblib`, `tqdm`, `psutil`, `pytest`, `pytest-cov`

**Code Structure:**
```
/                          # Project root
|-- readme.md              # Project documentation
|-- solution.txt           # Summary or problem/solution outline
|-- requirements.txt       # Dependency list
|-- .gitignore             # Git exclusions
|-- run.py                 # Main execution script
|-- run.sh                 # Shell wrapper
|--- data/
|   |-- input/             # Input data (users and restaurants CSVs)
|   |-- output/            # Output directory for results
|-- src/
|   |-- processor.py       # Core logic: matching, Haversine distance
|   |-- runner.py          # Batch supervisor to orchestrate execution
|-- utils/
|   |-- sample_data_generator.py   # Synthetic data generation for testing
|-- tests/
    |-- test_processor.py  # Unit tests for core logic
```

---

### Workflow Summary

#### Executor File: `run.py`
- Entrypoint that initializes `BatchRunner`
- Accepts:
  - `restaurant_file`: CSV path with restaurant info
  - `output_dir`: Path where results will be saved
  - `static_time`: Time at which restaurant availability is evaluated (default: `12:00:00`)
- Calls `.run()` with a list of user CSV files

**Why a list of user files?**
- The design supports benchmarking performance over varied data sizes by iterating through multiple datasets

#### Batch Supervisor: `BatchRunner.run()`
- Ensures output directory exists
- Loads restaurant data
- Iterates over user files with `tqdm` progress bar
- For each file:
  - Reads user locations
  - Finds eligible restaurants using `RestaurantProcessor`
  - Saves matched results (if any) as a CSV
- At the end, prints total execution time and memory usage

#### Restaurant Availability Logic: `RestaurantProcessor`
- Accepts a `static_time` parameter for filtering based on restaurant hours
- Uses `.find_available_restaurants(users_df, restaurants_df)` to:
  1. Preprocess restaurant and user location data
  2. Filter out closed restaurants (via `is_open()`)
  3. Convert coordinates to radians
  4. Build a `BallTree` (Haversine metric) for spatial queries
  5. Match users to restaurants within radius
  6. Return results with restaurant IDs and count

### Why Haversine Formula?

**Haversine Formula** is used because:
- It provides a good approximation for distances between points on the Earth's surface, assuming a spherical Earth
- Defined as:

```python
    a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
    c = 2 * arcsin(√a)
    d = R * c
```
- Where `R = 6371 km` (Earth's radius)

**Why Not Great Circle or Vincenty?**
- **Vincenty** is more accurate for ellipsoidal models but computationally heavier
- **Great Circle** is a simplified model similar to Haversine, but it can lead to errors for small distances or polar regions

**When to use Vincenty?**
- Required in geodetic, surveying, or aviation applications where **high precision** is mandatory