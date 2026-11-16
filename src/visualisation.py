"""
visualisation.py
=================
Publication-quality crash-pattern visualisations using a monochromatic
navy-blue colour palette.

All figures are saved to ``outputs/graphs/`` at 300 DPI.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import folium

from src.data_collection import PROJECT_ROOT
from src.crash_analysis import (
    TIME_ORDER,
    DAY_ORDER,
    run_analysis,
    hourly_dow_heatmap_data,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
GRAPHS_DIR = PROJECT_ROOT / "outputs" / "graphs"
MAPS_DIR = PROJECT_ROOT / "outputs" / "maps"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
MAPS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Navy-blue colour palette
# ---------------------------------------------------------------------------
DARK_NAVY   = "#142D4E"
DEEP_BLUE   = "#234B70"
MEDIUM_BLUE = "#4778A8"
LIGHT_BLUE  = "#91B6D5"
VERY_LIGHT  = "#EAF1F8"
WHITE       = "#FFFFFF"
DARK_TEXT    = "#202833"

PALETTE = [DARK_NAVY, DEEP_BLUE, MEDIUM_BLUE, LIGHT_BLUE, VERY_LIGHT]
TWO_COLORS = [DARK_NAVY, MEDIUM_BLUE]   # Signalized, Unsignalized
THREE_COLORS = [DARK_NAVY, MEDIUM_BLUE, LIGHT_BLUE]

SOURCE_CAPTION = (
    "Source: NYC Open Data – Motor Vehicle Collisions (2023-2024); "
    "OpenStreetMap traffic signals"
)

# ---------------------------------------------------------------------------
# Matplotlib style setup
# ---------------------------------------------------------------------------

def setup_style() -> None:
    """Apply the project-wide matplotlib style."""
    plt.rcParams.update({
        "figure.facecolor": WHITE,
        "axes.facecolor": WHITE,
        "axes.edgecolor": DARK_TEXT,
        "axes.labelcolor": DARK_TEXT,
        "text.color": DARK_TEXT,
        "xtick.color": DARK_TEXT,
        "ytick.color": DARK_TEXT,
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.color": LIGHT_BLUE,
    })


def _add_source(ax: plt.Axes, caption: str = SOURCE_CAPTION) -> None:
    """Add a source annotation below the axes."""
    ax.annotate(
        caption,
        xy=(0, -0.15), xycoords="axes fraction",
        fontsize=7, color="grey", ha="left", va="top",
    )


def _save(fig: plt.Figure, name: str) -> Path:
    """Save figure and close."""
    out = GRAPHS_DIR / f"{name}.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    logger.info("Saved figure → %s", out)
    return out


# ---------------------------------------------------------------------------
# Individual chart functions
# ---------------------------------------------------------------------------

def plot_crash_frequency(results: Dict[str, pd.DataFrame]) -> Path:
    """Bar chart: total crash frequency by intersection type."""
    setup_style()
    data = results["crash_counts"]
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(data.index, data["count"], color=TWO_COLORS, edgecolor=WHITE, width=0.5)
    for bar, val in zip(bars, data["count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"{int(val):,}", ha="center", va="bottom", fontsize=11,
                fontweight="bold", color=DARK_TEXT)
    ax.set_title("Total Crash Frequency by Intersection Type", fontweight="bold")
    ax.set_ylabel("Number of Crashes")
    ax.set_xlabel("Intersection Type")
    _add_source(ax)
    return _save(fig, "crash_frequency_by_type")


def plot_collision_type(results: Dict[str, pd.DataFrame]) -> Path:
    """Grouped bar chart: collision type comparison."""
    setup_style()
    data = results["collision_type"]
    # Get count columns
    sig_col = [c for c in data.columns if c.endswith("_count") and "Signalized" in c][0]
    unsig_col = [c for c in data.columns if c.endswith("_count") and "Unsignalized" in c][0]

    top = data.head(8)
    labels = top.index
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(x + width / 2, top[sig_col], width, label="Signalized",
            color=DARK_NAVY, edgecolor=WHITE)
    ax.barh(x - width / 2, top[unsig_col], width, label="Unsignalized",
            color=MEDIUM_BLUE, edgecolor=WHITE)
    ax.set_yticks(x)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Number of Crashes")
    ax.set_title("Collision Type Distribution: Signalized vs Unsignalized",
                 fontweight="bold")
    ax.legend(frameon=False)
    ax.invert_yaxis()
    _add_source(ax)
    return _save(fig, "collision_type_comparison")


def plot_severity(results: Dict[str, pd.DataFrame]) -> Path:
    """Stacked bar chart: severity distribution."""
    setup_style()
    data = results["severity"]
    sig_counts = [data.loc[s, [c for c in data.columns if "Signalized_count" in c][0]]
                  if s in data.index else 0
                  for s in ["No Injury", "Injury", "Fatal"]]
    unsig_counts = [data.loc[s, [c for c in data.columns if "Unsignalized_count" in c][0]]
                    if s in data.index else 0
                    for s in ["No Injury", "Injury", "Fatal"]]
    categories = ["No Injury", "Injury", "Fatal"]
    sig_total = sum(sig_counts)
    unsig_total = sum(unsig_counts)
    sig_pct = [v / sig_total * 100 if sig_total else 0 for v in sig_counts]
    unsig_pct = [v / unsig_total * 100 if unsig_total else 0 for v in unsig_counts]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(2)
    bottom_sig = 0
    bottom_unsig = 0
    colors = [LIGHT_BLUE, MEDIUM_BLUE, DARK_NAVY]
    for i, cat in enumerate(categories):
        ax.bar(x[0], sig_pct[i], bottom=bottom_sig, color=colors[i],
               edgecolor=WHITE, width=0.4, label=cat)
        ax.bar(x[1], unsig_pct[i], bottom=bottom_unsig, color=colors[i],
               edgecolor=WHITE, width=0.4)
        bottom_sig += sig_pct[i]
        bottom_unsig += unsig_pct[i]
    ax.set_xticks(x)
    ax.set_xticklabels(["Signalized", "Unsignalized"])
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Severity Distribution by Intersection Type", fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    _add_source(ax)
    return _save(fig, "severity_distribution")


def plot_vehicle_type(results: Dict[str, pd.DataFrame]) -> Path:
    """Grouped bar chart: vehicle type distribution."""
    setup_style()
    data = results["vehicle_type"].head(8)
    count_cols = [c for c in data.columns if c.endswith("_count")]
    labels = data.index
    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(10, 6))
    for i, col in enumerate(count_cols):
        lbl = col.replace("_count", "")
        ax.barh(x + (i - 0.5) * width, data[col], width,
                label=lbl, color=TWO_COLORS[i % 2], edgecolor=WHITE)
    ax.set_yticks(x)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Number of Crashes")
    ax.set_title("Vehicle Type Distribution: Signalized vs Unsignalized",
                 fontweight="bold")
    ax.legend(frameon=False)
    ax.invert_yaxis()
    _add_source(ax)
    return _save(fig, "vehicle_type_distribution")


def plot_time_of_day(results: Dict[str, pd.DataFrame]) -> Path:
    """Grouped bar chart: time-of-day distribution."""
    setup_style()
    data = results["time_of_day"]
    count_cols = [c for c in data.columns if c.endswith("_count")]
    labels = data.index
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5))
    for i, col in enumerate(count_cols):
        lbl = col.replace("_count", "")
        ax.bar(x + (i - 0.5) * width, data[col], width,
               label=lbl, color=TWO_COLORS[i % 2], edgecolor=WHITE)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Number of Crashes")
    ax.set_xlabel("Time of Day")
    ax.set_title("Crash Distribution by Time of Day", fontweight="bold")
    ax.legend(frameon=False)
    _add_source(ax)
    return _save(fig, "time_of_day_distribution")


def plot_day_of_week(results: Dict[str, pd.DataFrame]) -> Path:
    """Grouped bar chart: day-of-week distribution."""
    setup_style()
    data = results["day_of_week"]
    count_cols = [c for c in data.columns if c.endswith("_count")]
    labels = data.index
    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, col in enumerate(count_cols):
        lbl = col.replace("_count", "")
        ax.bar(x + (i - 0.5) * width, data[col], width,
               label=lbl, color=TWO_COLORS[i % 2], edgecolor=WHITE)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Number of Crashes")
    ax.set_xlabel("Day of Week")
    ax.set_title("Crash Distribution by Day of Week", fontweight="bold")
    ax.legend(frameon=False)
    _add_source(ax)
    return _save(fig, "day_of_week_distribution")


def plot_heatmap(df: pd.DataFrame, title_suffix: str = "Signalized") -> Path:
    """Heatmap: hour × day-of-week crash frequency."""
    setup_style()
    data = hourly_dow_heatmap_data(df, title_suffix)

    fig, ax = plt.subplots(figsize=(10, 8))
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("navy", [VERY_LIGHT, DARK_NAVY])
    im = ax.imshow(data.values, aspect="auto", cmap=cmap, interpolation="nearest")
    ax.set_xticks(np.arange(len(data.columns)))
    ax.set_xticklabels(data.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(np.arange(len(data.index)))
    ax.set_yticklabels([f"{h:02d}:00" for h in data.index], fontsize=9)
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Hour of Day")
    ax.set_title(f"Crash Frequency Heatmap – {title_suffix} Intersections",
                 fontweight="bold")
    cbar = fig.colorbar(im, ax=ax, shrink=0.7, label="Crash Count")
    # Annotate cells
    for i in range(len(data.index)):
        for j in range(len(data.columns)):
            val = data.values[i, j]
            colour = WHITE if val > data.values.max() * 0.5 else DARK_TEXT
            ax.text(j, i, int(val), ha="center", va="center",
                    fontsize=7, color=colour)
    _add_source(ax)
    name = f"heatmap_{title_suffix.lower()}"
    return _save(fig, name)


def plot_folium_map(df: pd.DataFrame) -> Path:
    """Interactive Folium map of crash locations colour-coded by type."""
    # Centre on Manhattan
    centre = [40.783, -73.967]
    m = folium.Map(location=centre, zoom_start=13, tiles="cartodbpositron")

    color_map = {"Signalized": DARK_NAVY, "Unsignalized": MEDIUM_BLUE}

    # Sample if too many points for performance
    plot_df = df[df["intersection_type"].isin(["Signalized", "Unsignalized"])]
    if len(plot_df) > 5000:
        plot_df = plot_df.sample(5000, random_state=42)

    for _, row in plot_df.iterrows():
        lat, lon = row.get("LATITUDE"), row.get("LONGITUDE")
        if pd.isna(lat) or pd.isna(lon):
            continue
        itype = row["intersection_type"]
        popup_text = (
            f"<b>{itype}</b><br>"
            f"Date: {row.get('CRASH DATE', 'N/A')}<br>"
            f"Severity: {row.get('severity', 'N/A')}<br>"
            f"Intersection: {row.get('intersection_key', 'N/A')}"
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color=color_map.get(itype, "grey"),
            fill=True,
            fill_opacity=0.6,
            popup=folium.Popup(popup_text, max_width=250),
        ).add_to(m)

    # Legend
    legend_html = f"""
    <div style="position:fixed; bottom:30px; left:30px; z-index:9999;
                background:white; padding:10px; border-radius:5px;
                border:1px solid grey; font-size:12px;">
    <b>Intersection Type</b><br>
    <i style="background:{DARK_NAVY};width:12px;height:12px;
       display:inline-block;border-radius:50%;"></i> Signalized<br>
    <i style="background:{MEDIUM_BLUE};width:12px;height:12px;
       display:inline-block;border-radius:50%;"></i> Unsignalized
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    out = MAPS_DIR / "crash_locations_map.html"
    m.save(str(out))
    logger.info("Saved Folium map → %s", out)
    return out


# ---------------------------------------------------------------------------
# Master runner
# ---------------------------------------------------------------------------

def generate_all_visualisations(
    df: Optional[pd.DataFrame] = None,
    results: Optional[Dict[str, pd.DataFrame]] = None,
) -> list[Path]:
    """Produce every visualisation and return list of saved paths.

    Parameters
    ----------
    df : pd.DataFrame, optional
        Classified crash data.  Loaded from processed CSV if not given.
    results : dict, optional
        Pre-computed analysis tables.  Computed if not given.
    """
    setup_style()

    if df is None:
        df = pd.read_csv(PROCESSED_DIR / "manhattan_crashes_classified.csv")

    if results is None:
        results = run_analysis(df)

    paths: list[Path] = []
    paths.append(plot_crash_frequency(results))
    paths.append(plot_collision_type(results))
    paths.append(plot_severity(results))
    paths.append(plot_vehicle_type(results))
    paths.append(plot_time_of_day(results))
    paths.append(plot_day_of_week(results))
    paths.append(plot_heatmap(df, "Signalized"))
    paths.append(plot_heatmap(df, "Unsignalized"))
    paths.append(plot_folium_map(df))

    logger.info("All visualisations generated (%d files).", len(paths))
    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    generate_all_visualisations()
