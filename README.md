# Project 7 – Comparative Crash Pattern Analysis at Signalized and Unsignalized Intersections

## Description

This project analyses motor vehicle crash patterns at **signalized** (traffic-signal-controlled) and **unsignalized** intersections in Manhattan, New York City, using 2023-2024 crash data from NYC Open Data and traffic signal locations from OpenStreetMap.

Key analyses include:

- **Crash frequency comparison** between signalized and unsignalized intersections
- **Collision type distribution** (rear-end, angle, sideswipe, pedestrian, etc.)
- **Severity analysis** (fatal, injury, no-injury)
- **Temporal patterns** by time-of-day, day-of-week, and hour
- **Vehicle type involvement**
- **Contributing factor analysis** with chi-square statistical tests
- **Collision diagrams** for representative intersections
- **Interactive GIS map** of crash locations

### How Signalized vs Unsignalized Is Determined

The NYC crash dataset does not include a traffic-control field.  We use OpenStreetMap data (via the `osmnx` library) to extract all nodes tagged `highway=traffic_signals` in NYC, then classify each intersection crash:

| Classification  | Rule |
|-----------------|------|
| **Signalized**  | Crash within 30 m of an OSM traffic-signal node **and** has a cross street |
| **Unsignalized**| Crash with a cross street but **not** within 30 m of a signal node |
| Mid-block       | No cross street — excluded from intersection analysis |

---

## Project Structure

```
project_7/
├── data/
│   ├── raw/                # Original CSVs (not in version control)
│   │   ├── nyc_crashes.csv
│   │   └── nyc_vehicles.csv
│   ├── processed/          # Cleaned & classified datasets
│   └── README.md
├── notebooks/
│   └── crash_pattern_analysis.ipynb
├── outputs/
│   ├── diagrams/           # Collision diagrams (PNG)
│   ├── graphs/             # Charts & plots (PNG, 300 DPI)
│   ├── maps/               # Interactive Folium maps (HTML)
│   └── tables/             # Summary CSV tables
├── report/                 # Final report documents
├── src/
│   ├── __init__.py
│   ├── data_collection.py  # Data loading & OSM signal retrieval
│   ├── preprocessing.py    # Cleaning, feature engineering, spatial join
│   ├── crash_analysis.py   # Statistical analysis & summary tables
│   ├── visualisation.py    # All matplotlib & folium visualisations
│   └── collision_diagrams.py  # Schematic collision diagrams
├── requirements.txt
├── README.md
└── DATA_SOURCES.md
```

---

## Setup

### Prerequisites

- Python 3.10+
- An internet connection is required on the **first run** to download OSM traffic-signal data (cached after that).

### Installation

```bash
cd project_7
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## How to Reproduce

### Option A – Run the Jupyter Notebook

```bash
jupyter notebook notebooks/crash_pattern_analysis.ipynb
```

Execute the cells in order. The notebook imports modules from `src/` and runs the full pipeline.

### Option B – Run Modules Individually

```bash
# 1. Preprocessing (creates data/processed/*.csv)
python -m src.preprocessing

# 2. Analysis (creates outputs/tables/*.csv)
python -m src.crash_analysis

# 3. Visualisations (creates outputs/graphs/*.png + maps/*.html)
python -m src.visualisation

# 4. Collision diagrams (creates outputs/diagrams/*.png)
python -m src.collision_diagrams
```

---

## Data Sources

| Dataset | Source | License |
|---------|--------|---------|
| NYC Motor Vehicle Collisions – Crashes | [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95) | NYC Open Data ToU |
| NYC Motor Vehicle Collisions – Vehicles | [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4) | NYC Open Data ToU |
| Traffic signal locations | [OpenStreetMap](https://www.openstreetmap.org/) via `osmnx` | ODbL |

See [DATA_SOURCES.md](DATA_SOURCES.md) for full details.

---

## Limitations

1. **Signal classification is approximate.** OSM coverage may be incomplete, and the 30 m buffer is a heuristic. Some crashes may be misclassified.
2. **No vehicle trajectory data.** Collision diagrams are schematic — crash symbols are placed at approximate positions, not along actual travel paths.
3. **Reporting bias.** Not all crashes are reported, especially minor property-damage-only incidents.
4. **Observation period.** Analysis is limited to 2023-2024 Manhattan data and may not generalise to other boroughs or time periods.
5. **OSM data currency.** Signal installations or removals after the OSM data snapshot are not reflected.

---

## License

This project is for academic and research purposes.  The underlying datasets are governed by their respective licences (see above).
