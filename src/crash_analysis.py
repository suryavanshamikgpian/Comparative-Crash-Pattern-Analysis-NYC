"""
crash_analysis.py
==================
Statistical analysis of crash patterns at signalized vs unsignalized
intersections.

Analyses
--------
* Total crash counts per intersection type
* Collision-type frequency distribution
* Severity distribution comparison
* Vehicle-type distribution
* Time-of-day distribution
* Day-of-week distribution
* Contributing-factor analysis
* Chi-square tests for categorical distributions
* Summary tables exported to ``outputs/tables/``
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from src.data_collection import PROJECT_ROOT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"

# Ensure output directory exists
TABLES_DIR.mkdir(parents=True, exist_ok=True)

# Ordered categories
TIME_ORDER = ["Night", "Morning", "Midday", "Afternoon", "Evening"]
DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
             "Saturday", "Sunday"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _pct(series: pd.Series) -> pd.Series:
    """Return percentage shares (summing to 100)."""
    return (series / series.sum() * 100).round(1)


def _crosstab_pct(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Build a frequency + pct crosstab of *col* by intersection_type."""
    ct = pd.crosstab(df[col], df["intersection_type"])
    pct = ct.div(ct.sum()).mul(100).round(1)
    combined = ct.astype(str) + " (" + pct.astype(str) + "%)"
    return combined


# ---------------------------------------------------------------------------
# Core analysis functions
# ---------------------------------------------------------------------------

def crash_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Total crash counts by intersection type.

    Parameters
    ----------
    df : pd.DataFrame
        Classified crash dataset with ``intersection_type``.

    Returns
    -------
    pd.DataFrame
        Counts and percentages.
    """
    counts = df["intersection_type"].value_counts().rename("count")
    pct = _pct(counts).rename("pct")
    result = pd.concat([counts, pct], axis=1)
    result.index.name = "intersection_type"
    return result


def collision_type_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Collision type frequency table with percentages per intersection type.

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Rows = collision type, columns = intersection type (count + %).
    """
    ct = pd.crosstab(df["collision_type"], df["intersection_type"])
    pct = ct.div(ct.sum()).mul(100).round(1)
    # Stack nicely
    result = pd.DataFrame()
    for col in ct.columns:
        result[f"{col}_count"] = ct[col]
        result[f"{col}_pct"] = pct[col]
    result = result.sort_values(result.columns[0], ascending=False)
    return result


def severity_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Severity distribution by intersection type."""
    ct = pd.crosstab(df["severity"], df["intersection_type"])
    pct = ct.div(ct.sum()).mul(100).round(1)
    result = pd.DataFrame()
    for col in ct.columns:
        result[f"{col}_count"] = ct[col]
        result[f"{col}_pct"] = pct[col]
    return result


def vehicle_type_distribution(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top vehicle type distribution by intersection type."""
    # Use primary_vehicle_type from merge
    col = "primary_vehicle_type" if "primary_vehicle_type" in df.columns else "VEHICLE TYPE CODE 1"
    top_types = df[col].value_counts().head(top_n).index
    sub = df[df[col].isin(top_types)]
    ct = pd.crosstab(sub[col], sub["intersection_type"])
    pct = ct.div(ct.sum()).mul(100).round(1)
    result = pd.DataFrame()
    for c in ct.columns:
        result[f"{c}_count"] = ct[c]
        result[f"{c}_pct"] = pct[c]
    result = result.sort_values(result.columns[0], ascending=False)
    return result


def time_of_day_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Crash count by time-of-day bin and intersection type."""
    ct = pd.crosstab(df["time_of_day"], df["intersection_type"])
    ct = ct.reindex(TIME_ORDER)
    pct = ct.div(ct.sum()).mul(100).round(1)
    result = pd.DataFrame()
    for c in ct.columns:
        result[f"{c}_count"] = ct[c]
        result[f"{c}_pct"] = pct[c]
    return result


def day_of_week_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Crash count by day of week and intersection type."""
    ct = pd.crosstab(df["day_of_week"], df["intersection_type"])
    ct = ct.reindex(DAY_ORDER)
    pct = ct.div(ct.sum()).mul(100).round(1)
    result = pd.DataFrame()
    for c in ct.columns:
        result[f"{c}_count"] = ct[c]
        result[f"{c}_pct"] = pct[c]
    return result


def contributing_factor_analysis(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Top contributing factors by intersection type."""
    col = "CONTRIBUTING FACTOR VEHICLE 1"
    top_factors = df[col].value_counts().head(top_n).index
    sub = df[df[col].isin(top_factors)]
    ct = pd.crosstab(sub[col], sub["intersection_type"])
    pct = ct.div(ct.sum()).mul(100).round(1)
    result = pd.DataFrame()
    for c in ct.columns:
        result[f"{c}_count"] = ct[c]
        result[f"{c}_pct"] = pct[c]
    result = result.sort_values(result.columns[0], ascending=False)
    return result


def hourly_dow_heatmap_data(df: pd.DataFrame,
                            itype: str = "Signalized") -> pd.DataFrame:
    """Pivot table of crash counts: hour × day-of-week for one type."""
    sub = df[df["intersection_type"] == itype]
    pt = pd.crosstab(sub["hour"], sub["day_of_week"])
    pt = pt.reindex(columns=DAY_ORDER)
    return pt


# ---------------------------------------------------------------------------
# Statistical tests
# ---------------------------------------------------------------------------

def chi_square_test(df: pd.DataFrame, col: str) -> Dict[str, float]:
    """Run chi-square test on *col* vs intersection_type.

    Parameters
    ----------
    df : pd.DataFrame
    col : str
        Categorical column to test.

    Returns
    -------
    dict with keys chi2, p_value, dof, significant (at α = 0.05).
    """
    ct = pd.crosstab(df[col], df["intersection_type"])
    chi2, p, dof, _ = chi2_contingency(ct)
    return {
        "column": col,
        "chi2": round(chi2, 4),
        "p_value": round(p, 6),
        "dof": int(dof),
        "significant_005": p < 0.05,
    }


def run_all_chi_square(df: pd.DataFrame) -> pd.DataFrame:
    """Run chi-square tests on all key categorical columns."""
    cols = ["severity", "collision_type", "time_of_day", "day_of_week"]
    if "primary_vehicle_type" in df.columns:
        cols.append("primary_vehicle_type")
    results = [chi_square_test(df, c) for c in cols]
    return pd.DataFrame(results)


# ---------------------------------------------------------------------------
# Summary statistics
# ---------------------------------------------------------------------------

def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """High-level summary statistics per intersection type."""
    records = []
    for itype in ["Signalized", "Unsignalized"]:
        sub = df[df["intersection_type"] == itype]
        total = len(sub)
        fatal = (sub["severity"] == "Fatal").sum()
        injury = (sub["severity"] == "Injury").sum()
        no_injury = (sub["severity"] == "No Injury").sum()
        n_intersections = sub["intersection_key"].nunique()
        records.append({
            "intersection_type": itype,
            "total_crashes": total,
            "unique_intersections": n_intersections,
            "fatal": fatal,
            "injury": injury,
            "no_injury": no_injury,
            "fatal_rate_pct": round(fatal / total * 100, 2) if total else 0,
            "injury_rate_pct": round(injury / total * 100, 2) if total else 0,
        })
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def run_analysis(
    df: pd.DataFrame | None = None,
) -> Dict[str, pd.DataFrame]:
    """Run all analyses and export tables.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Classified crash data.  If not provided, reads from processed CSV.

    Returns
    -------
    dict
        Name → DataFrame of every analysis result.
    """
    if df is None:
        path = PROCESSED_DIR / "manhattan_crashes_classified.csv"
        logger.info("Loading classified data from %s", path)
        df = pd.read_csv(path)

    # Filter to intersection crashes only
    df = df[df["intersection_type"].isin(["Signalized", "Unsignalized"])].copy()

    results: Dict[str, pd.DataFrame] = {}

    results["crash_counts"] = crash_counts(df)
    results["collision_type"] = collision_type_distribution(df)
    results["severity"] = severity_distribution(df)
    results["vehicle_type"] = vehicle_type_distribution(df)
    results["time_of_day"] = time_of_day_distribution(df)
    results["day_of_week"] = day_of_week_distribution(df)
    results["contributing_factors"] = contributing_factor_analysis(df)
    results["heatmap_signalized"] = hourly_dow_heatmap_data(df, "Signalized")
    results["heatmap_unsignalized"] = hourly_dow_heatmap_data(df, "Unsignalized")
    results["chi_square"] = run_all_chi_square(df)
    results["summary"] = summary_statistics(df)

    # Export
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    for name, table in results.items():
        out = TABLES_DIR / f"{name}.csv"
        table.to_csv(out)
        logger.info("Saved %s → %s", name, out)

    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    run_analysis()
