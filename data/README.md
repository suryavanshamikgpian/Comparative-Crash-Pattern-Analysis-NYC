# Data Directory

## `raw/`

Original source data files (not modified by the pipeline):

- **nyc_crashes.csv** – NYC Motor Vehicle Collisions – Crashes dataset from NYC Open Data.
- **nyc_vehicles.csv** – NYC Motor Vehicle Collisions – Vehicles dataset from NYC Open Data.

These files are large and are not tracked in version control.

## `processed/`

Output of the preprocessing pipeline (`src/preprocessing.py`):

- **manhattan_crashes_classified.csv** – Cleaned Manhattan 2023-2024 crashes with severity, collision type, temporal features, and signalized/unsignalized classification.
- **top_signalized.csv** – Crash records at the top 5 signalized intersections.
- **top_unsignalized.csv** – Crash records at the top 5 unsignalized intersections.
- **nyc_traffic_signals.gpkg** – Cached OpenStreetMap traffic signal node locations (GeoPackage).
