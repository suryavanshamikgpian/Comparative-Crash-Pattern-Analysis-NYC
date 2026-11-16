"""
collision_diagrams.py
=====================
Schematic collision diagrams for representative signalized and unsignalized
intersections.

**Limitation**: The NYC crash dataset does not include exact vehicle
trajectories, approach lanes, or movement paths.  Therefore these diagrams
are *schematic representations*: crash counts and collision types are
plotted at approximate positions around a stylised four-leg intersection
layout.  They should be interpreted as summary visualisations rather than
precise collision plots.

Symbols
-------
- ● Circle     → Rear-end / Following Too Closely
- ▲ Triangle   → Angle / Failure to Yield
- ■ Square     → Sideswipe / Improper Manoeuvre
- ◆ Diamond    → Pedestrian / Cyclist related
- ★ Star       → Other / Unspecified
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from src.data_collection import PROJECT_ROOT

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DIAGRAMS_DIR = PROJECT_ROOT / "outputs" / "diagrams"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DIAGRAMS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Palette (matches project theme)
# ---------------------------------------------------------------------------
DARK_NAVY   = "#142D4E"
DEEP_BLUE   = "#234B70"
MEDIUM_BLUE = "#4778A8"
LIGHT_BLUE  = "#91B6D5"
VERY_LIGHT  = "#EAF1F8"
WHITE       = "#FFFFFF"
DARK_TEXT    = "#202833"

# ---------------------------------------------------------------------------
# Collision type → marker mapping
# ---------------------------------------------------------------------------
MARKER_MAP = {
    "Following Too Closely":       ("o", DARK_NAVY,   "Rear-end"),
    "Failure to Yield":            ("^", DEEP_BLUE,    "Angle / Yield"),
    "Improper Manoeuvre":           ("s", MEDIUM_BLUE,  "Sideswipe / Manoeuvre"),
    "Pedestrian/Cyclist Error":    ("D", LIGHT_BLUE,   "Pedestrian / Cyclist"),
    "Distracted Driving":          ("o", MEDIUM_BLUE,  "Distracted"),
    "Traffic Control Violation":   ("^", DARK_NAVY,    "Traffic Ctrl Violation"),
    "Speeding":                    ("s", DEEP_BLUE,    "Speeding"),
    "Aggressive Driving":          ("D", DARK_NAVY,    "Aggressive"),
    "Impaired Driving":            ("*", DEEP_BLUE,    "Impaired"),
}
DEFAULT_MARKER = ("*", LIGHT_BLUE, "Other")


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def _draw_intersection(ax: plt.Axes, label: str = "") -> None:
    """Draw a schematic four-leg intersection on *ax*."""
    # Road widths (normalised –1..1 space)
    road_w = 0.18

    # Horizontal road
    ax.fill_between([-1, 1], -road_w, road_w, color=VERY_LIGHT, zorder=0)
    # Vertical road
    ax.fill_betweenx([-1, 1], -road_w, road_w, color=VERY_LIGHT, zorder=0)

    # Centre-lines
    ax.axhline(0, color=LIGHT_BLUE, lw=0.8, ls="--", zorder=1)
    ax.axvline(0, color=LIGHT_BLUE, lw=0.8, ls="--", zorder=1)

    # Approach arrows
    arrow_kw = dict(head_width=0.04, head_length=0.03, fc=DARK_TEXT,
                    ec=DARK_TEXT, lw=0.8, zorder=2)
    ax.arrow(-0.9, -0.07, 0.45, 0, **arrow_kw)   # West → East (bottom lane)
    ax.arrow(0.9,  0.07, -0.45, 0, **arrow_kw)    # East → West (top lane)
    ax.arrow(-0.07, -0.9, 0, 0.45, **arrow_kw)    # South → North (left lane)
    ax.arrow(0.07,  0.9, 0, -0.45, **arrow_kw)    # North → South (right lane)

    # Labels
    for pos, txt in [((-0.85, 0.25), "W"), ((0.8, -0.25), "E"),
                     ((-0.25, -0.85), "S"), ((0.22, 0.85), "N")]:
        ax.text(*pos, txt, fontsize=9, ha="center", va="center",
                fontweight="bold", color=DARK_TEXT)

    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect("equal")
    ax.axis("off")


def _scatter_crashes(ax: plt.Axes, type_counts: pd.Series,
                     total: int, rng: np.random.Generator) -> None:
    """Scatter crash symbols around the intersection box.

    Positions are randomly jittered within the intersection zone.
    """
    for ctype, count in type_counts.items():
        marker, color, _ = MARKER_MAP.get(ctype, DEFAULT_MARKER)
        # Place points in a ring around the centre
        angles = rng.uniform(0, 2 * np.pi, size=count)
        radii = rng.uniform(0.20, 0.42, size=count)
        xs = radii * np.cos(angles)
        ys = radii * np.sin(angles)
        ax.scatter(xs, ys, marker=marker, c=color, s=40, alpha=0.7,
                   edgecolors=WHITE, linewidths=0.3, zorder=5)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_collision_diagram(
    intersection_name: str,
    intersection_df: pd.DataFrame,
    intersection_type: str,
    out_dir: Optional[Path] = None,
) -> Path:
    """Create a collision diagram for one intersection.

    Parameters
    ----------
    intersection_name : str
        Human-readable intersection name.
    intersection_df : pd.DataFrame
        Crash records at this intersection (must have ``collision_type``).
    intersection_type : str
        'Signalized' or 'Unsignalized'.
    out_dir : Path, optional

    Returns
    -------
    Path to saved PNG.
    """
    out_dir = out_dir or DIAGRAMS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    type_counts = intersection_df["collision_type"].value_counts()
    total = len(intersection_df)

    fig, ax = plt.subplots(figsize=(8, 8))
    _draw_intersection(ax, intersection_name)
    rng = np.random.default_rng(42)
    _scatter_crashes(ax, type_counts, total, rng)

    # Title
    short_name = intersection_name[:60]
    ax.set_title(
        f"Collision Diagram – {intersection_type}\n{short_name}\n"
        f"Total crashes: {total}",
        fontsize=12, fontweight="bold", color=DARK_TEXT, pad=15,
    )

    # Legend
    handles = []
    for ctype in type_counts.index:
        marker, color, label = MARKER_MAP.get(ctype, DEFAULT_MARKER)
        handles.append(
            Line2D([0], [0], marker=marker, color="w", markerfacecolor=color,
                   markersize=8, label=f"{label} ({type_counts[ctype]})")
        )
    ax.legend(handles=handles, loc="lower right", fontsize=8,
              frameon=True, facecolor=WHITE, edgecolor=LIGHT_BLUE)

    # Limitation note
    fig.text(0.5, 0.02,
             "Note: Crash positions are schematic; exact vehicle "
             "trajectories are not available in the source data.",
             ha="center", fontsize=7, color="grey")

    safe_name = intersection_name.replace("/", "-").replace(" ", "_")[:40]
    fname = f"collision_diagram_{intersection_type.lower()}_{safe_name}.png"
    out = out_dir / fname
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    logger.info("Saved collision diagram → %s", out)
    return out


def generate_all_diagrams(
    signalized_df: Optional[pd.DataFrame] = None,
    unsignalized_df: Optional[pd.DataFrame] = None,
) -> list[Path]:
    """Generate collision diagrams for all top intersections.

    Parameters
    ----------
    signalized_df, unsignalized_df : pd.DataFrame, optional
        If not provided, reads from processed CSVs.

    Returns
    -------
    list of Paths to saved diagrams.
    """
    if signalized_df is None:
        signalized_df = pd.read_csv(PROCESSED_DIR / "top_signalized.csv")
    if unsignalized_df is None:
        unsignalized_df = pd.read_csv(PROCESSED_DIR / "top_unsignalized.csv")

    paths: list[Path] = []

    for itype, sub_df in [("Signalized", signalized_df),
                          ("Unsignalized", unsignalized_df)]:
        if "intersection_key" not in sub_df.columns:
            logger.warning("No intersection_key column in %s data – skipping.", itype)
            continue
        for name, grp in sub_df.groupby("intersection_key"):
            path = create_collision_diagram(str(name), grp, itype)
            paths.append(path)

    logger.info("Generated %d collision diagrams.", len(paths))
    return paths


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    generate_all_diagrams()
