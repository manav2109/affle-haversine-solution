# 🍽️ Restaurant Lookup Service

A scalable and efficient system to find open and nearby restaurants for large sets of user locations using Haversine distance and time-aware logic.

---

## 📁 Project Structure

```
restaurant-lookup/
├── data/
│   ├── input/        # Input files like users_*.csv, restaurants.csv
│   └── output/       # Output result files after processing
│
├── src/
│   ├── processor.py  # Core logic: time filters, BallTree distance
│   ├── runner.py     # Batch runner to coordinate input/output
│   └── __init__.py
├── utils/
│   ├── sample_data_generator.py # Script to generate users.csv at various scales
│   └── __init__.py
├── tests/            # Unit tests using pytest
├── run.py            # Optional entry point
├── run.sh            # Shell script to auto-setup, test, and run
└── requirements.txt  # Dependency list
```

---

## 🚀 Features

- ✅ Uses **Haversine distance** + **BallTree** for fast spatial filtering
- ✅ Time filtering (handles overnight hours)
- ✅ Vectorized and Parallelized (via `joblib.Parallel`)
- ✅ Handles 10 to 1 million+ users in under 15 seconds
- ✅ Fully tested (81%+ coverage)

---

## ⚙️ Setup & Usage

### ✨ One Command Setup

```bash
chmod +x ./run.sh
./run.sh
```

This will:
- Recreate virtualenv
- Install dependencies
- Run tests + coverage
- Execute `run.py` if present

### 🔧 Manual Setup (Alternate)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

---

## 🔄 Usage Instructions

1. Place your input files in the `data/input/` folder:
   - `restaurants.csv`
   - `users_*.csv` (e.g., `users_1_10.csv`, `users_1001_100000.csv`)

2. Run the script:
```bash
python run.py
```

3. Results will be saved automatically in:
```
data/output/<input_file>_results.csv
```

Each output row contains:
- User's location
- Count of available restaurants
- Restaurant IDs separated by `;`

---

## 📊 Input Format

### 📄 restaurants.csv
```csv
id,latitude,longitude,availability_radius,open_hour,close_hour
1,28.61,77.20,5.0,10:00:00,22:00:00
```

### 📄 users_*.csv
```csv
USER_LATITUDE,USER_LONGITUDE
28.61,77.20
```

---

## 📄 Output Format

```csv
User_latitude,User_Longitude,Available_restaurant_count,Restaurant_Id's
28.61,77.20,2,1;3
```

Results are saved in `data/output/`.

---

## 📊 Benchmark Results

| User File                 | User Count | Time Taken (s) | Memory Before (MB) | Memory After (MB) | Matched Rows | Total Matches | Output File                    |
|---------------------------|-------------|----------------|---------------------|--------------------|---------------|----------------|---------------------------------|
| users_1_10.csv           | 10          | 1.203          | 158.55              | 167.7              | 10            | 890            | users_1_10_results.csv         |
| users_11_100.csv         | 90          | 0.77           | 167.7               | 171.45             | 90            | 1273           | users_11_100_results.csv       |
| users_101_1000.csv       | 900         | 0.801          | 171.45              | 174.26             | 900           | 44837          | users_101_1000_results.csv     |
| users_1001_100000.csv    | 99,000      | 1.544          | 174.26              | 267.74             | 99,000        | 12,501,551     | users_1001_100000_results.csv  |
| users_100001_1000000.csv | 900,000     | 5.226          | 268.24              | 799.76             | 900,000       | 47,131,749     | users_100001_1000000_results.csv |

---

## 📊 Testing

Run tests and view coverage:
```bash
PYTHONPATH=./src pytest --cov=src --cov-report=term-missing
```

