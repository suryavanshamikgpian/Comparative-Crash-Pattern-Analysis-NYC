"""
preprocessing.py
=================
Data cleaning, feature engineering, spatial classification of crashes as
signalized / unsignalized, and selection of top intersections.

Pipeline
--------
1. Load raw crash + vehicle CSVs.
2. Filter to Manhattan, 2023-2024.
3. Drop rows missing coordinates; deduplicate on COLLISION_ID.
4. Parse date / time; create severity, time-of-day, day-of-week features.
5. Classify contributing factors into broad collision-type categories.
6. Merge vehicle data.
7. Spatially classify crashes using OSM traffic-signal nodes.
8. Select top-5 signalized and top-5 unsignalized intersections.
9. Export processed datasets.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Tuple, Optional

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from src.data_collection import (
    load_crash_data,
    load_vehicle_data,
    fetch_traffic_signals,
    PROJECT_ROOT,
    PROCESSED_DATA_DIR,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# NYC bounding box (generous)
NYC_LAT_MIN, NYC_LAT_MAX = 40.49, 40.92
NYC_LON_MIN, NYC_LON_MAX = -74.27, -73.68

# Manhattan approximate bounding box
MANHATTAN_LAT_MIN, MANHATTAN_LAT_MAX = 40.700, 40.882
MANHATTAN_LON_MIN, MANHATTAN_LON_MAX = -74.020, -73.907

# Buffer distance (metres) for signalized classification
SIGNAL_BUFFER_M = 30

# Years to keep
STUDY_YEARS = [2023, 2024]

# Number of top intersections per type
TOP_N = 5

# Time-of-day bins  (label, start_hour, end_hour_exclusive)
TIME_BINS: list[Tuple[str, int, int]] = [
    ("Night",     0,  6),
    ("Morning",   6,  10),
    ("Midday",    10, 15),
    ("Afternoon", 15, 19),
    ("Evening",   19, 24),
]

# Broad collision-type mapping from contributing factors
COLLISION_TYPE_MAP: dict[str, str] = {
    "Driver Inattention/Distraction": "Distracted Driving",
    "Failure to Yield Right-of-Way": "Failure to Yield",
    "Following Too Closely": "Following Too Closely",
    "Backing Unsafely": "Improper Manoeuvre",
    "Passing or Lane Usage Improper": "Improper Manoeuvre",
    "Turning Improperly": "Improper Manoeuvre",
    "Unsafe Lane Changing": "Improper Manoeuvre",
    "Passing Too Closely": "Improper Manoeuvre",
    "Traffic Control Disregarded": "Traffic Control Violation",
    "Traffic Control Device Improper/Non-Working": "Traffic Control Violation",
    "Unsafe Speed": "Speeding",
    "Alcohol Involvement": "Impaired Driving",
    "Drugs (illegal)": "Impaired Driving",
    "Prescription Medication": "Impaired Driving",
    "Fell Asleep": "Impaired Driving",
    "Fatigued/Drowsy": "Impaired Driving",
    "Pedestrian/Bicyclist/Other Pedestrian Error/Confusion": "Pedestrian/Cyclist Error",
    "Aggressive Driving/Road Rage": "Aggressive Driving",
    "Unspecified": "Unspecified",
}

SEVERITY_COLS_KILLED = [
    "NUMBER OF PERSONS KILLED",
    "NUMBER OF PEDESTRIANS KILLED",
    "NUMBER OF CYCLIST KILLED",
    "NUMBER OF MOTORIST KILLED",
]
SEVERITY_COLS_INJURED = [
    "NUMBER OF PERSONS INJURED",
    "NUMBER OF PEDESTRIANS INJURED",
    "NUMBER OF CYCLIST INJURED",
    "NUMBER OF MOTORIST INJURED",
]


# ---------------------------------------------------------------------------
# Inspection helper
# ---------------------------------------------------------------------------

def inspect_raw(df: pd.DataFrame, label: str = "DataFrame") -> None:
    """Log basic shape, dtypes, and missing-value summary."""
    logger.info("--- %s ---", label)
    logger.info("Shape: %s", df.shape)
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    summary = pd.DataFrame({"missing": missing, "pct": missing_pct})
    logger.info("Missing values:\n%s", summary[summary["missing"] > 0].to_string())


# ---------------------------------------------------------------------------
# Core preprocessing
# ---------------------------------------------------------------------------

def filter_manhattan(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only Manhattan crashes in study years."""
    df = df.copy()

    # Parse year from CRASH DATE
    df["CRASH DATE"] = pd.to_datetime(df["CRASH DATE"], format="mixed", dayfirst=False)
    df["crash_year"] = df["CRASH DATE"].dt.year

    # Borough filter
    mask_borough = df["BOROUGH"].str.upper().eq("MANHATTAN")
    mask_year = df["crash_year"].isin(STUDY_YEARS)
    df = df[mask_borough & mask_year].copy()
    logger.info("After Manhattan + year filter: %d records.", len(df))
    return df


def clean_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows without valid lat/lon within NYC bounding box."""
    df = df.dropna(subset=["LATITUDE", "LONGITUDE"]).copy()
    mask = (
        df["LATITUDE"].between(NYC_LAT_MIN, NYC_LAT_MAX)
        & df["LONGITUDE"].between(NYC_LON_MIN, NYC_LON_MAX)
    )
    df = df[mask].copy()
    logger.info("After coordinate cleaning: %d records.", len(df))
    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate COLLISION_IDs, keeping the first occurrence."""
    before = len(df)
    df = df.drop_duplicates(subset=["COLLISION_ID"], keep="first").copy()
    logger.info("Removed %d duplicate COLLISION_IDs.", before - len(df))
    return df


def add_severity(df: pd.DataFrame) -> pd.DataFrame:
    """Add a ``severity`` column: Fatal > Injury > No Injury."""
    df = df.copy()
    total_killed = df[SEVERITY_COLS_KILLED].fillna(0).sum(axis=1)
    total_injured = df[SEVERITY_COLS_INJURED].fillna(0).sum(axis=1)
    df["severity"] = np.where(
        total_killed > 0, "Fatal",
        np.where(total_injured > 0, "Injury", "No Injury"),
    )
    logger.info("Severity distribution:\n%s", df["severity"].value_counts().to_string())
    return df


def add_collision_type(df: pd.DataFrame) -> pd.DataFrame:
    """Map CONTRIBUTING FACTOR VEHICLE 1 to broad collision types."""
    df = df.copy()
    df["collision_type"] = (
        df["CONTRIBUTING FACTOR VEHICLE 1"]
        .map(COLLISION_TYPE_MAP)
        .fillna("Other")
    )
    logger.info("Collision type distribution:\n%s",
                df["collision_type"].value_counts().head(10).to_string())
    return df


def add_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Parse time fields and add time_of_day, day_of_week, hour columns."""
    df = df.copy()

    # Ensure CRASH DATE is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["CRASH DATE"]):
        df["CRASH DATE"] = pd.to_datetime(df["CRASH DATE"], format="mixed", dayfirst=False)

    # Parse hour from CRASH TIME (HH:MM or H:MM)
    df["hour"] = pd.to_datetime(df["CRASH TIME"], format="mixed").dt.hour

    # Time-of-day bins
    conditions = [
        df["hour"].between(s, e - 1) for _, s, e in TIME_BINS
    ]
    choices = [label for label, _, _ in TIME_BINS]
    df["time_of_day"] = np.select(conditions, choices, default="Unknown")

    # Day of week
    df["day_of_week"] = df["CRASH DATE"].dt.day_name()

    logger.info("Temporal features added.")
    return df


# ---------------------------------------------------------------------------
# Intersection name helper
# ---------------------------------------------------------------------------

def create_intersection_key(df: pd.DataFrame) -> pd.DataFrame:
    """Create a normalised intersection key from ON/CROSS STREET NAME."""
    df = df.copy()
    on_st = df["ON STREET NAME"].fillna("").str.strip().str.upper()
    cross_st = df["CROSS STREET NAME"].fillna("").str.strip().str.upper()
    # Sort the two street names alphabetically so the pair is order-invariant
    df["intersection_key"] = [
        " & ".join(sorted([a, b])) if b else a
        for a, b in zip(on_st, cross_st)
    ]
    return df


# ---------------------------------------------------------------------------
# Spatial signal classification
# ---------------------------------------------------------------------------

def classify_signalised(
    df: pd.DataFrame,
    signals_gdf: Optional[gpd.GeoDataFrame] = None,
    buffer_m: int = SIGNAL_BUFFER_M,
) -> pd.DataFrame:
    """Add ``intersection_type`` column (Signalized / Unsignalized).

    A crash is *signalized* if it falls within ``buffer_m`` metres of an
    OSM node tagged ``highway=traffic_signals``.  Crashes that have a
    cross-street name but are *not* within the buffer are classified
    *unsignalized*.  Crashes without a cross-street (mid-block) are
    labelled *Mid-block* and excluded from the intersection analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain LATITUDE, LONGITUDE, CROSS STREET NAME.
    signals_gdf : gpd.GeoDataFrame, optional
        Traffic-signal nodes.  Fetched from OSM / cache if not provided.
    buffer_m : int
        Buffer radius in metres.

    Returns
    -------
    pd.DataFrame
        With ``intersection_type`` column added.
    """
    if signals_gdf is None:
        signals_gdf = fetch_traffic_signals()

    df = df.copy()

    # Build a GeoDataFrame of crash points
    crash_geom = gpd.points_from_xy(df["LONGITUDE"], df["LATITUDE"], crs="EPSG:4326")
    crash_gdf = gpd.GeoDataFrame(df, geometry=crash_geom, crs="EPSG:4326")

    # Project to a metre-based CRS for buffering (UTM zone 18N covers NYC)
    crash_gdf_proj = crash_gdf.to_crs(epsg=32618)
    signals_proj = signals_gdf.to_crs(epsg=32618)

    # Buffer signals and build a unary union
    signal_buffer = signals_proj.geometry.buffer(buffer_m).union_all()

    # Test containment
    within_signal = crash_gdf_proj.geometry.within(signal_buffer)

    # Has a cross street → intersection
    has_cross = df["CROSS STREET NAME"].fillna("").str.strip().ne("")

    df["intersection_type"] = np.where(
        within_signal & has_cross, "Signalized",
        np.where(has_cross & ~within_signal, "Unsignalized", "Mid-block"),
    )
    logger.info("Intersection type distribution:\n%s",
                df["intersection_type"].value_counts().to_string())
    return df


# ---------------------------------------------------------------------------
# Top intersection selection
# ---------------------------------------------------------------------------

def select_top_intersections(
    df: pd.DataFrame,
    n: int = TOP_N,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return the top-*n* signalized and unsignalized intersections by count.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain ``intersection_type`` and ``intersection_key``.
    n : int
        Number of intersections to keep per type.

    Returns
    -------
    (signalized_df, unsignalized_df)
        Filtered DataFrames containing only crashes at the selected
        intersections.
    """
    results = {}
    for itype in ("Signalized", "Unsignalized"):
        sub = df[df["intersection_type"] == itype]
        top_keys = (
            sub["intersection_key"]
            .value_counts()
            .head(n)
            .index.tolist()
        )
        results[itype] = sub[sub["intersection_key"].isin(top_keys)].copy()
        logger.info("Top %d %s intersections: %s", n, itype, top_keys)
    return results["Signalized"], results["Unsignalized"]


# ---------------------------------------------------------------------------
# Vehicle merge
# ---------------------------------------------------------------------------

def merge_vehicles(crashes: pd.DataFrame,
                   vehicles: pd.DataFrame) -> pd.DataFrame:
    """Left-join vehicle records onto crash records via COLLISION_ID.

    Only a *summary* of vehicle info is attached (dominant vehicle type
    and contributing factor per crash) to avoid row explosion.
    """
    # Filter vehicles to only crashes in the study dataset for massive speedup
    vehicles = vehicles[vehicles["COLLISION_ID"].isin(crashes["COLLISION_ID"])].copy()

    # Dominant vehicle type per crash
    vtype = (
        vehicles.groupby("COLLISION_ID")["VEHICLE_TYPE"]
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "Unknown")
        .rename("primary_vehicle_type")
    )

    # Dominant contributing factor from vehicles
    cfactor = (
        vehicles.groupby("COLLISION_ID")["CONTRIBUTING_FACTOR_1"]
        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else "Unspecified")
        .rename("vehicle_contributing_factor")
    )

    summary = pd.concat([vtype, cfactor], axis=1)
    merged = crashes.merge(summary, how="left", left_on="COLLISION_ID",
                           right_index=True)
    logger.info("Merged vehicle summary; shape = %s", merged.shape)
    return merged


# ---------------------------------------------------------------------------
# Master pipeline
# ---------------------------------------------------------------------------

def run_preprocessing(
    crash_path: Optional[Path] = None,
    vehicle_path: Optional[Path] = None,
    signal_gdf: Optional[gpd.GeoDataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Execute the full preprocessing pipeline.

    Returns
    -------
    (all_crashes, signalized, unsignalized)
        ``all_crashes`` is the cleaned Manhattan dataset with intersection
        classification.  ``signalized`` / ``unsignalized`` are subsets for
        the top intersections.
    """
    # 1. Load
    crashes = load_crash_data(crash_path)
    vehicles = load_vehicle_data(vehicle_path)
    inspect_raw(crashes, "Raw crashes")
    inspect_raw(vehicles, "Raw vehicles")

    # 2. Filter & clean
    crashes = filter_manhattan(crashes)
    crashes = clean_coordinates(crashes)
    crashes = deduplicate(crashes)

    # 3. Feature engineering
    crashes = add_severity(crashes)
    crashes = add_collision_type(crashes)
    crashes = add_temporal_features(crashes)
    crashes = create_intersection_key(crashes)

    # 4. Merge vehicle summary
    crashes = merge_vehicles(crashes, vehicles)

    # 5. Spatial classification
    crashes = classify_signalised(crashes, signals_gdf=signal_gdf)

    # 6. Top intersections
    signalized, unsignalized = select_top_intersections(crashes)

    # 7. Persist
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    crashes.to_csv(PROCESSED_DATA_DIR / "manhattan_crashes_classified.csv", index=False)
    signalized.to_csv(PROCESSED_DATA_DIR / "top_signalized.csv", index=False)
    unsignalized.to_csv(PROCESSED_DATA_DIR / "top_unsignalized.csv", index=False)
    logger.info("Processed data saved to %s", PROCESSED_DATA_DIR)

    return crashes, signalized, unsignalized


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    run_preprocessing()
