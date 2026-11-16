"""
data_collection.py
===================
Functions to load raw NYC crash and vehicle CSVs and to retrieve
OpenStreetMap traffic-signal node locations for New York City.

Data Sources
------------
1. NYC Motor Vehicle Collisions – Crashes
   https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95
   Columns used: CRASH DATE, CRASH TIME, BOROUGH, LATITUDE, LONGITUDE,
                  COLLISION_ID, ON STREET NAME, CROSS STREET NAME,
                  NUMBER OF PERSONS KILLED/INJURED, CONTRIBUTING FACTOR …,
                  VEHICLE TYPE CODE …
   License: NYC Open Data Terms of Use

2. NYC Motor Vehicle Collisions – Vehicles
   https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4
   Columns used: COLLISION_ID, VEHICLE_TYPE, TRAVEL_DIRECTION,
                  CONTRIBUTING_FACTOR_1/2, PRE_CRASH, POINT_OF_IMPACT
   License: NYC Open Data Terms of Use

3. OpenStreetMap (via osmnx)
   Traffic-signal nodes tagged highway=traffic_signals within NYC boundary.
   License: ODbL (Open Database License)
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import geopandas as gpd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Project paths (relative to repository root)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
CACHE_DIR = PROJECT_ROOT / "data" / "processed"

# Default file names
CRASH_FILE = "nyc_crashes.csv"
VEHICLE_FILE = "nyc_vehicles.csv"
SIGNAL_CACHE_FILE = "nyc_traffic_signals.gpkg"


# ---------------------------------------------------------------------------
# Loading helpers
# ---------------------------------------------------------------------------

def load_crash_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    """Load the raw NYC Motor Vehicle Collisions – Crashes CSV.

    Parameters
    ----------
    filepath : Path, optional
        Full path to the CSV.  Defaults to ``data/raw/nyc_crashes.csv``.

    Returns
    -------
    pd.DataFrame
        Raw crash records.
    """
    filepath = filepath or RAW_DATA_DIR / CRASH_FILE
    logger.info("Loading crash data from %s …", filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Crash CSV not found: {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    logger.info("Loaded %d crash records with %d columns.", len(df), len(df.columns))
    return df


def load_vehicle_data(filepath: Optional[Path] = None) -> pd.DataFrame:
    """Load the raw NYC Motor Vehicle Collisions – Vehicles CSV.

    Parameters
    ----------
    filepath : Path, optional
        Full path to the CSV.  Defaults to ``data/raw/nyc_vehicles.csv``.

    Returns
    -------
    pd.DataFrame
        Raw vehicle-level records.
    """
    filepath = filepath or RAW_DATA_DIR / VEHICLE_FILE
    logger.info("Loading vehicle data from %s …", filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Vehicle CSV not found: {filepath}")
    df = pd.read_csv(filepath, low_memory=False)
    logger.info("Loaded %d vehicle records.", len(df))
    return df


# ---------------------------------------------------------------------------
# OSM traffic-signal retrieval
# ---------------------------------------------------------------------------

def fetch_traffic_signals(place: str = "New York City, New York, USA",
                          cache_path: Optional[Path] = None) -> gpd.GeoDataFrame:
    """Query OpenStreetMap for nodes tagged ``highway=traffic_signals``.

    Results are cached locally as a GeoPackage so the OSM query runs only
    once.

    Parameters
    ----------
    place : str
        Geocodable place name understood by Nominatim.
    cache_path : Path, optional
        Where to cache the result.  Defaults to
        ``data/processed/nyc_traffic_signals.gpkg``.

    Returns
    -------
    gpd.GeoDataFrame
        Point geometries of traffic-signal nodes (EPSG:4326).
    """
    import osmnx as ox  # imported here so the rest of the module works without it

    cache_path = cache_path or CACHE_DIR / SIGNAL_CACHE_FILE

    if cache_path.exists():
        logger.info("Loading cached traffic signals from %s", cache_path)
        return gpd.read_file(cache_path)

    logger.info("Querying OSM for traffic signals in '%s' …", place)
    tags = {"highway": "traffic_signals"}
    gdf = ox.features_from_place(place, tags=tags)

    # Keep only point geometries (nodes)
    gdf = gdf[gdf.geometry.geom_type == "Point"].copy()
    gdf = gdf[["geometry"]].reset_index(drop=True)
    gdf = gdf.set_crs(epsg=4326, allow_override=True)

    logger.info("Retrieved %d traffic-signal nodes.", len(gdf))
    save_traffic_signals(gdf, cache_path)
    return gdf


def save_traffic_signals(gdf: gpd.GeoDataFrame,
                         cache_path: Optional[Path] = None) -> Path:
    """Persist the traffic-signal GeoDataFrame to disk.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Traffic-signal point data.
    cache_path : Path, optional
        Destination file.

    Returns
    -------
    Path
        The path where the file was saved.
    """
    cache_path = cache_path or CACHE_DIR / SIGNAL_CACHE_FILE
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(cache_path, driver="GPKG")
    logger.info("Saved traffic signals to %s", cache_path)
    return cache_path
