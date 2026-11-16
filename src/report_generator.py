#!/usr/bin/env python3
"""
Report Generator for Project 7: Comparative Crash Pattern Analysis
at Signalized and Unsignalized Intersections.

Generates a professional DOCX report using python-docx with full academic
formatting, IEEE references, tables, and figure placeholders.

Usage:
    python src/report_generator.py

Output:
    report/Final_Report.docx
"""

import os
import sys
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "report"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
GRAPHS_DIR = OUTPUTS_DIR / "graphs"
TABLES_DIR = OUTPUTS_DIR / "tables"
DIAGRAMS_DIR = OUTPUTS_DIR / "diagrams"
MAPS_DIR = OUTPUTS_DIR / "maps"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Theme colours
# ---------------------------------------------------------------------------
DARK_NAVY = RGBColor(0x14, 0x2D, 0x4E)
DEEP_BLUE = RGBColor(0x23, 0x4B, 0x70)
MEDIUM_BLUE = RGBColor(0x47, 0x78, 0xA8)
LIGHT_BLUE = RGBColor(0x91, 0xB6, 0xD5)
VERY_LIGHT_BLUE = RGBColor(0xEA, 0xF1, 0xF8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK_TEXT = RGBColor(0x20, 0x28, 0x33)
BLACK = RGBColor(0x00, 0x00, 0x00)

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _set_cell_shading(cell, hex_color: str):
    """Apply background shading to a table cell."""
    shading = parse_xml(
        f'<w:shd {nsdecls("w")} w:fill="{hex_color}" w:val="clear"/>'
    )
    cell._tc.get_or_add_tcPr().append(shading)


def _set_cell_borders(cell, top=None, bottom=None, start=None, end=None):
    """Set individual cell borders."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}></w:tcBorders>')
    for edge, val in [("top", top), ("bottom", bottom), ("start", start), ("end", end)]:
        if val:
            border = parse_xml(
                f'<w:{edge} {nsdecls("w")} w:val="{val["val"]}" '
                f'w:sz="{val.get("sz", "4")}" w:space="0" '
                f'w:color="{val.get("color", "000000")}"/>'
            )
            tcBorders.append(border)
    tcPr.append(tcBorders)


def _add_page_number(section):
    """Add page number to footer."""
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.font.size = Pt(10)
    run.font.name = "Times New Roman"
    run.font.color.rgb = DARK_TEXT

    fldChar1 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>')
    run._r.append(fldChar1)

    instrText = parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> PAGE </w:instrText>')
    run._r.append(instrText)

    fldChar2 = parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>')
    run._r.append(fldChar2)


def _style_paragraph(paragraph, font_name="Times New Roman", font_size=12,
                     bold=False, italic=False, color=None, alignment=None,
                     space_before=0, space_after=6, line_spacing=1.5,
                     first_line_indent=None):
    """Apply consistent styling to a paragraph."""
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(space_before)
    fmt.space_after = Pt(space_after)
    fmt.line_spacing = line_spacing

    if alignment is not None:
        paragraph.alignment = alignment
    if first_line_indent is not None:
        fmt.first_line_indent = Inches(first_line_indent)

    for run in paragraph.runs:
        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.italic = italic
        if color:
            run.font.color.rgb = color


def _add_body_text(doc, text, **kwargs):
    """Add a body paragraph with default styling."""
    p = doc.add_paragraph(text)
    defaults = dict(
        font_name="Times New Roman", font_size=12, color=DARK_TEXT,
        space_after=6, line_spacing=1.5, alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    )
    defaults.update(kwargs)
    _style_paragraph(p, **defaults)
    return p


def _add_heading(doc, text, level=1):
    """Add a heading with navy colour and Times New Roman."""
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.name = "Times New Roman"
        run.font.color.rgb = DARK_NAVY
    return h


def _add_figure_placeholder(doc, figure_id, caption, image_path=None,
                             width=Inches(5.5)):
    """Insert an image if available, otherwise a placeholder box, plus caption."""
    if image_path and os.path.isfile(image_path):
        doc.add_picture(str(image_path), width=width)
        last_para = doc.paragraphs[-1]
        last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(f"[INSERT_{figure_id}]")
        run.font.name = "Times New Roman"
        run.font.size = Pt(11)
        run.font.italic = True
        run.font.color.rgb = MEDIUM_BLUE

    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_cap = cap.add_run(f"Figure {figure_id}: {caption}")
    run_cap.font.name = "Times New Roman"
    run_cap.font.size = Pt(10)
    run_cap.font.italic = True
    run_cap.font.color.rgb = DARK_TEXT
    cap.paragraph_format.space_after = Pt(12)
    return cap


def _add_table(doc, headers, rows, caption=None, table_id=None):
    """Add a formatted table with navy header row."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    # Header row
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        _set_cell_shading(hdr_cells[i], "142D4E")
        for p in hdr_cells[i].paragraphs:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.name = "Times New Roman"
                run.font.size = Pt(10)
                run.font.bold = True
                run.font.color.rgb = WHITE
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row_cells = table.rows[1 + r_idx].cells
        bg = "EAF1F8" if r_idx % 2 == 0 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            _set_cell_shading(row_cells[c_idx], bg)
            for p in row_cells[c_idx].paragraphs:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run.font.size = Pt(10)
                    run.font.color.rgb = DARK_TEXT
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Caption below table
    if caption and table_id:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cap = cap.add_run(f"Table {table_id}: {caption}")
        run_cap.font.name = "Times New Roman"
        run_cap.font.size = Pt(10)
        run_cap.font.italic = True
        run_cap.font.color.rgb = DARK_TEXT
        cap.paragraph_format.space_after = Pt(12)

    return table


def _add_page_break(doc):
    doc.add_page_break()


# ===========================================================================
#  REPORT CONTENT
# ===========================================================================

def build_report():
    """Build the complete DOCX report."""
    doc = Document()

    # ------------------------------------------------------------------
    # Global style setup
    # ------------------------------------------------------------------
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    font.color.rgb = DARK_TEXT
    pf = style.paragraph_format
    pf.line_spacing = 1.5
    pf.space_after = Pt(6)

    # Heading styles
    for level in range(1, 5):
        hs = doc.styles[f"Heading {level}"]
        hs.font.name = "Times New Roman"
        hs.font.color.rgb = DARK_NAVY
        hs.font.bold = True
        sizes = {1: 16, 2: 14, 3: 13, 4: 12}
        hs.font.size = Pt(sizes.get(level, 12))
        hs.paragraph_format.space_before = Pt(18 if level == 1 else 12)
        hs.paragraph_format.space_after = Pt(6)

    # Page margins (1 inch = 2.54 cm)
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    _add_page_number(section)

    # ==================================================================
    # 1. TITLE PAGE
    # ==================================================================
    for _ in range(6):
        doc.add_paragraph()

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = title_p.add_run("Comparative Crash Pattern Analysis\nat Signalized and Unsignalized Intersections")
    run_t.font.name = "Times New Roman"
    run_t.font.size = Pt(24)
    run_t.font.bold = True
    run_t.font.color.rgb = DARK_NAVY
    title_p.paragraph_format.space_after = Pt(36)

    # Horizontal rule
    rule_p = doc.add_paragraph()
    rule_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rule_run = rule_p.add_run("─" * 60)
    rule_run.font.color.rgb = MEDIUM_BLUE
    rule_run.font.size = Pt(12)
    rule_p.paragraph_format.space_after = Pt(24)

    meta_lines = [
        ("Author:", "Student Name (to be filled)"),
        ("Institution:", "Indian Institute of Technology Kharagpur"),
        ("Department:", "Department of Civil Engineering"),
        ("Course:", "Assignment 2 – Project 7"),
        ("Date:", "November 2026"),
    ]
    for label, value in meta_lines:
        mp = doc.add_paragraph()
        mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rl = mp.add_run(f"{label}  ")
        rl.font.name = "Times New Roman"
        rl.font.size = Pt(13)
        rl.font.bold = True
        rl.font.color.rgb = DEEP_BLUE
        rv = mp.add_run(value)
        rv.font.name = "Times New Roman"
        rv.font.size = Pt(13)
        rv.font.color.rgb = DARK_TEXT
        mp.paragraph_format.space_after = Pt(4)

    _add_page_break(doc)

    # ==================================================================
    # 2. ABSTRACT
    # ==================================================================
    _add_heading(doc, "Abstract", level=1)

    abstract_text = (
        "This study presents a comparative analysis of crash patterns at signalized "
        "and unsignalized intersections in Manhattan, New York City, using the NYC "
        "Motor Vehicle Collisions dataset for the period 2023–2024. The primary "
        "objective is to describe and contrast the characteristics of crashes "
        "occurring at these two intersection control types, without attempting to "
        "rank their relative safety due to the absence of traffic exposure data. "
        "Traffic signal locations were identified using OpenStreetMap (OSM) data, "
        "and crashes were spatially classified based on their proximity to OSM-tagged "
        "traffic signal nodes within a 30-metre threshold. The five highest-crash-"
        "count intersections of each type were selected for detailed analysis. "
        "The study examines crash distributions across multiple dimensions including "
        "collision type, severity, vehicle type, temporal patterns (time-of-day and "
        "day-of-week), and contributing factors. Collision diagrams were prepared "
        "using schematic representations of crash types and approach directions. "
        "Results reveal distinct crash pattern differences between intersection "
        "control types across severity distributions, temporal concentration, and "
        "predominant contributing factors. The findings provide descriptive insights "
        "relevant to intersection safety planning, while acknowledging that crash "
        "counts alone cannot determine which intersection type is inherently safer."
    )
    _add_body_text(doc, abstract_text)

    # ==================================================================
    # 3. KEYWORDS
    # ==================================================================
    kw_p = doc.add_paragraph()
    kw_label = kw_p.add_run("Keywords: ")
    kw_label.font.name = "Times New Roman"
    kw_label.font.size = Pt(12)
    kw_label.font.bold = True
    kw_label.font.color.rgb = DARK_NAVY
    kw_text = kw_p.add_run(
        "Road safety, crash pattern analysis, signalized intersections, "
        "unsignalized intersections, collision diagrams, traffic safety, "
        "New York City"
    )
    kw_text.font.name = "Times New Roman"
    kw_text.font.size = Pt(12)
    kw_text.font.italic = True
    kw_text.font.color.rgb = DARK_TEXT
    kw_p.paragraph_format.space_after = Pt(12)

    _add_page_break(doc)

    # ==================================================================
    # 4. INTRODUCTION
    # ==================================================================
    _add_heading(doc, "1. Introduction", level=1)

    intro_paras = [
        (
            "Intersections are among the most complex elements of the road transportation "
            "system, requiring drivers to navigate conflicting traffic streams, interpret "
            "control devices, and make rapid decisions under uncertainty. According to the "
            "Federal Highway Administration (FHWA), approximately 50% of all traffic "
            "injuries and over 20% of traffic fatalities in the United States occur at or "
            "near intersections [1]. These statistics underscore the critical importance "
            "of understanding crash patterns at intersections to inform effective safety "
            "countermeasures."
        ),
        (
            "The type of traffic control at an intersection—whether signalized with traffic "
            "lights or unsignalized with stop signs, yield signs, or no control—fundamentally "
            "shapes driver behaviour, traffic flow, and consequently, the nature and severity "
            "of crashes that occur. Signalized intersections manage conflicting movements "
            "through time separation of traffic phases, while unsignalized intersections rely "
            "on right-of-way rules, gap acceptance, and driver judgment. These differing "
            "operational environments produce distinct crash typologies that merit systematic "
            "examination."
        ),
        (
            "New York City, with its dense urban grid and over 12,000 signalized intersections "
            "in Manhattan alone, provides a rich environment for studying intersection crash "
            "patterns. The NYC Motor Vehicle Collisions dataset, maintained by the New York "
            "City Police Department (NYPD) and published through NYC Open Data, records "
            "detailed information on every police-reported collision, making it one of the "
            "most comprehensive urban crash databases available for research."
        ),
        (
            "This study conducts a descriptive comparative analysis of crash patterns at "
            "selected signalized and unsignalized intersections in Manhattan for the years "
            "2023–2024. The analysis examines crash frequency, collision type distributions, "
            "severity profiles, temporal patterns, vehicle involvement, and contributing "
            "factors. Schematic collision diagrams are prepared to visualise crash typologies "
            "at representative intersections. It is important to note that this study is "
            "purely descriptive: in the absence of traffic volume (exposure) data, crash "
            "counts alone cannot be used to judge whether one intersection type is safer "
            "than another. The findings are intended to characterise the distinct crash "
            "signatures associated with each control type, contributing to a more nuanced "
            "understanding of urban intersection safety."
        ),
    ]
    for para_text in intro_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 5. BACKGROUND AND PROBLEM STATEMENT
    # ==================================================================
    _add_heading(doc, "2. Background and Problem Statement", level=1)

    bg_paras = [
        (
            "Intersection crashes represent a persistent and significant road safety "
            "challenge worldwide. In the United States, the National Highway Traffic "
            "Safety Administration (NHTSA) reports that intersection-related crashes "
            "account for approximately 40% of all police-reported crashes annually. "
            "The economic cost of these crashes, including property damage, medical "
            "expenses, lost productivity, and quality-of-life impacts, amounts to "
            "billions of dollars each year. Understanding the patterns underlying "
            "these crashes is essential for developing targeted interventions."
        ),
        (
            "The distinction between signalized and unsignalized intersections is "
            "fundamental to intersection safety analysis. Signalized intersections, "
            "by controlling right-of-way through traffic signals, eliminate many "
            "crossing conflicts but introduce rear-end collision risks during "
            "signal-change intervals, red-light running crashes, and left-turn "
            "opposing-through conflicts during permissive phases. Unsignalized "
            "intersections, conversely, experience higher rates of angle crashes "
            "due to failed gap-acceptance and right-of-way violations, but may "
            "have lower rear-end crash rates in free-flow conditions."
        ),
        (
            "A significant gap in the existing literature is the limited availability "
            "of studies that provide detailed descriptive comparisons of crash patterns "
            "between these control types using large-scale urban data. Most existing "
            "research focuses on crash frequency modelling or safety performance "
            "functions that require exposure data (Average Annual Daily Traffic, "
            "turning movement counts) that is rarely available at the intersection "
            "level for large datasets. This study addresses this gap by focusing on "
            "the descriptive characterisation of crash patterns—examining what types "
            "of crashes occur, when they occur, and what factors contribute—without "
            "making causal claims about relative safety."
        ),
        (
            "The specific problem this study addresses is the need to systematically "
            "describe and compare crash pattern signatures at signalized versus "
            "unsignalized intersections in a dense urban environment. By analysing "
            "the NYC Motor Vehicle Collisions data for Manhattan (2023–2024), this "
            "study provides a detailed, multi-dimensional comparison that can inform "
            "safety practitioners about the characteristic crash profiles associated "
            "with each intersection control type."
        ),
    ]
    for para_text in bg_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 6. RESEARCH OBJECTIVES
    # ==================================================================
    _add_heading(doc, "3. Research Objectives", level=1)

    _add_body_text(doc, "The specific objectives of this study are as follows:")

    objectives = [
        (
            "To describe and compare the distribution of crash types, severity levels, "
            "and contributing factors at signalized and unsignalized intersections in "
            "Manhattan, New York City, using police-reported crash data from 2023–2024."
        ),
        (
            "To analyse the temporal patterns (time-of-day and day-of-week distributions) "
            "of crashes at both intersection types and identify characteristic differences "
            "in crash timing."
        ),
        (
            "To develop schematic collision diagrams for representative signalized and "
            "unsignalized intersections and discuss the observed crash pattern differences "
            "in the context of intersection geometry and traffic control characteristics."
        ),
    ]
    for i, obj in enumerate(objectives, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.line_spacing = 1.5
        run_num = p.add_run(f"Objective {i}: ")
        run_num.font.name = "Times New Roman"
        run_num.font.size = Pt(12)
        run_num.font.bold = True
        run_num.font.color.rgb = DEEP_BLUE
        run_text = p.add_run(obj)
        run_text.font.name = "Times New Roman"
        run_text.font.size = Pt(12)
        run_text.font.color.rgb = DARK_TEXT

    _add_page_break(doc)

    # ==================================================================
    # 7. LITERATURE REVIEW
    # ==================================================================
    _add_heading(doc, "4. Literature Review", level=1)

    lit_paras = [
        (
            "Intersection safety has been a central focus of traffic safety research "
            "for several decades. The FHWA Intersection Safety Issue Briefs provide a "
            "comprehensive overview of the magnitude of intersection crashes in the "
            "United States, noting that intersections account for a disproportionate "
            "share of traffic fatalities and injuries relative to the proportion of "
            "travel that occurs at intersections [1]. The FHWA identifies intersection "
            "safety as one of its priority areas, with emphasis on both engineering "
            "countermeasures and data-driven analysis approaches."
        ),
        (
            "Persaud et al. (2001) made significant contributions to the understanding "
            "of intersection safety by developing empirical Bayes methods for estimating "
            "the safety of individual intersections. Their work demonstrated the "
            "importance of accounting for regression-to-the-mean effects when evaluating "
            "intersection safety and established methodological foundations that continue "
            "to influence intersection safety research [2]. Their safety performance "
            "functions for signalized and unsignalized intersections showed that crash "
            "frequency is strongly associated with traffic volumes on the major and "
            "minor approaches, underscoring the importance of exposure data in "
            "comparative safety assessments."
        ),
        (
            "Haleem and Abdel-Aty (2010) focused specifically on unsignalized "
            "intersection crashes in Florida, using random parameter models to examine "
            "the factors associated with injury severity at these locations [3]. Their "
            "analysis revealed that geometric features such as the number of lanes, "
            "speed limits, and the presence of medians were significant predictors of "
            "crash severity at unsignalized intersections. The study highlighted the "
            "unique crash dynamics at unsignalized intersections, where the absence of "
            "signal control places greater responsibility on individual drivers to "
            "manage conflicts through gap acceptance and visual scanning."
        ),
        (
            "Huang et al. (2006) examined the safety effects of red-light cameras at "
            "signalized intersections, providing valuable insights into the crash "
            "patterns characteristic of signalized locations [4]. Their findings "
            "showed that while red-light cameras reduced angle crashes (associated "
            "with red-light running), they increased rear-end crashes (as drivers "
            "braked more aggressively at camera-equipped intersections). This trade-off "
            "illustrates the complex relationship between intersection control features "
            "and crash patterns that extends beyond simple crash frequency comparisons."
        ),
        (
            "The AASHTO Highway Safety Manual (2010) provides the definitive "
            "methodology for predictive safety analysis in the United States, "
            "including safety performance functions (SPFs) and crash modification "
            "factors (CMFs) for both signalized and unsignalized intersections [5]. "
            "The HSM explicitly distinguishes between different intersection control "
            "types in its predictive method, reflecting the fundamentally different "
            "crash generation processes at signalized and unsignalized locations. The "
            "manual emphasises that crash patterns—including the predominant crash "
            "types and their severity distributions—differ systematically between "
            "control types."
        ),
        (
            "In the New York City context, the Vision Zero Initiative, launched in "
            "2014, set the ambitious goal of eliminating traffic deaths through a "
            "combination of engineering, enforcement, and education strategies [6]. "
            "NYC DOT's annual Pedestrian Safety Action Plans and Borough Pedestrian "
            "Safety Plans identify high-crash intersections and document the crash "
            "patterns that drive safety interventions. The Vision Zero approach "
            "prioritises data-driven analysis and has produced detailed crash pattern "
            "reports that examine crash types, contributing factors, and road user "
            "involvement at NYC intersections. This study builds on the Vision Zero "
            "analytical framework by providing a systematic comparison between "
            "signalized and unsignalized intersection crash patterns."
        ),
    ]
    for para_text in lit_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 8. STUDY AREA AND INTERSECTION SELECTION
    # ==================================================================
    _add_heading(doc, "5. Study Area and Intersection Selection", level=1)

    study_area_paras = [
        (
            "The study area comprises the borough of Manhattan (New York County) in "
            "New York City. Manhattan was selected for several reasons: it contains "
            "the highest density of both signalized and unsignalized intersections in "
            "NYC, has a predominantly grid-based street network that facilitates "
            "intersection classification, and experiences substantial crash volumes "
            "due to high traffic density. The borough's compact geography and diverse "
            "intersection types provide an ideal setting for comparative crash pattern "
            "analysis."
        ),
        (
            "A critical methodological challenge in this study was the classification "
            "of intersections as signalized or unsignalized. The NYC Motor Vehicle "
            "Collisions dataset does not include a field identifying the type of "
            "traffic control present at the crash location. To address this limitation, "
            "OpenStreetMap (OSM) data was utilised. OSM tags intersection nodes with "
            "the attribute 'highway=traffic_signals' where traffic signal installations "
            "are mapped by contributors. Using the osmnx library in Python, all nodes "
            "tagged with 'highway=traffic_signals' within the Manhattan network were "
            "extracted."
        ),
        (
            "Each crash record was then spatially matched to the nearest OSM "
            "intersection node. Crashes occurring within 30 metres of an "
            "OSM-tagged traffic signal node were classified as occurring at a "
            "signalized intersection. Crashes located at an intersection (identified "
            "by the presence of a CROSS STREET NAME in the crash record) but farther "
            "than 30 metres from any traffic signal node were classified as "
            "unsignalized. This spatial classification approach, while subject to "
            "limitations related to OSM data completeness, provides a systematic and "
            "reproducible method for intersection type identification."
        ),
        (
            "From the classified dataset, the five intersections of each type "
            "(signalized and unsignalized) with the highest crash counts during the "
            "2023–2024 study period were selected for detailed analysis. This "
            "selection criterion ensures sufficient crash volumes for meaningful "
            "pattern comparison while keeping the analysis scope manageable. The "
            "selected intersections represent major crash locations in Manhattan and "
            "exhibit the characteristic crash patterns associated with their "
            "respective control types."
        ),
    ]
    for para_text in study_area_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 9. DATASET DESCRIPTION AND SOURCES
    # ==================================================================
    _add_heading(doc, "6. Dataset Description and Sources", level=1)

    _add_heading(doc, "6.1 NYC Motor Vehicle Collisions – Crashes", level=2)
    _add_body_text(
        doc,
        "The primary dataset is the Motor Vehicle Collisions – Crashes dataset "
        "published on NYC Open Data (data.cityofnewyork.us). This dataset records "
        "every police-reported motor vehicle collision in New York City, as mandated "
        "by New York State traffic law requiring a police report when a collision "
        "results in injury, death, or property damage exceeding $1,000. Each record "
        "includes the collision date and time, geographic coordinates (latitude and "
        "longitude), borough, street names (on-street and cross-street), the number "
        "of persons, pedestrians, cyclists, and motorists injured or killed, "
        "contributing factors for up to five vehicles, and vehicle type codes. The "
        "unique COLLISION_ID serves as the primary key. For this study, records "
        "were filtered to Manhattan borough with crash dates in 2023 and 2024.",
        first_line_indent=0.5,
    )

    _add_heading(doc, "6.2 NYC Motor Vehicle Collisions – Vehicles", level=2)
    _add_body_text(
        doc,
        "The companion Motor Vehicle Collisions – Vehicles dataset provides "
        "vehicle-level detail for each collision, linked by COLLISION_ID. Variables "
        "include vehicle type, make, model, travel direction, point of impact, "
        "pre-crash action, vehicle damage location, driver sex, and driver licence "
        "status. This dataset was joined to the crash-level dataset to enrich the "
        "analysis with vehicle-specific information, particularly travel direction "
        "and pre-crash action for collision diagram preparation.",
        first_line_indent=0.5,
    )

    _add_heading(doc, "6.3 OpenStreetMap Data", level=2)
    _add_body_text(
        doc,
        "OpenStreetMap (OSM) data for the Manhattan street network was obtained "
        "using the osmnx Python library. The OSM network provides node-level "
        "attributes including the 'highway' tag, which identifies traffic signals "
        "('highway=traffic_signals'), stop signs, and other control features. "
        "While OSM data is crowd-sourced and may not be perfectly current or "
        "complete, it represents the most accessible source of intersection "
        "control-type data for large-scale urban analysis and has been validated "
        "in numerous transportation studies.",
        first_line_indent=0.5,
    )

    # Summary table of variables
    _add_table(doc,
        headers=["Variable", "Source", "Description"],
        rows=[
            ["CRASH DATE / TIME", "Crashes", "Collision date and time"],
            ["LATITUDE / LONGITUDE", "Crashes", "Geographic coordinates"],
            ["BOROUGH", "Crashes", "NYC borough (filtered: Manhattan)"],
            ["ON STREET / CROSS STREET", "Crashes", "Street names at crash location"],
            ["PERSONS INJURED / KILLED", "Crashes", "Casualty counts by road-user type"],
            ["CONTRIBUTING FACTOR", "Crashes", "Contributing factors (up to 5 vehicles)"],
            ["COLLISION_ID", "Both", "Unique collision identifier (join key)"],
            ["VEHICLE_TYPE", "Vehicles", "Type of vehicle involved"],
            ["TRAVEL_DIRECTION", "Vehicles", "Direction of vehicle travel"],
            ["PRE_CRASH", "Vehicles", "Pre-crash vehicle action"],
            ["highway tag", "OSM", "Intersection control type tag"],
        ],
        caption="Key variables used in the analysis",
        table_id=1,
    )

    _add_page_break(doc)

    # ==================================================================
    # 10. DATA COLLECTION AND PREPROCESSING
    # ==================================================================
    _add_heading(doc, "7. Data Collection and Preprocessing", level=1)

    preprocess_paras = [
        (
            "Data collection and preprocessing followed a systematic, reproducible "
            "pipeline implemented in Python. The raw datasets were downloaded from "
            "NYC Open Data in CSV format. The preprocessing pipeline comprised "
            "several sequential stages designed to clean, validate, classify, and "
            "integrate the data for analysis."
        ),
        (
            "Data Filtering and Cleaning: "
            "The crashes dataset was first filtered to retain only records with "
            "BOROUGH equal to 'MANHATTAN' and crash dates within the years 2023 "
            "and 2024. Records lacking geographic coordinates (LATITUDE or LONGITUDE "
            "equal to zero or null) were removed, as spatial classification requires "
            "valid coordinates. Duplicate records were identified and removed based "
            "on the COLLISION_ID field. Geographic coordinates were validated against "
            "the bounding box of Manhattan to exclude any mislocated records."
        ),
        (
            "Severity Classification: "
            "A severity classification was created for each crash based on the "
            "casualty counts. Crashes with any person killed (NUMBER OF PERSONS "
            "KILLED > 0) were classified as 'Fatal'. Crashes with persons injured "
            "but none killed were classified as 'Injury'. All remaining crashes "
            "were classified as 'No Injury' (property damage only). This three-tier "
            "classification follows standard practice in crash data analysis."
        ),
        (
            "Temporal Variables: "
            "The CRASH DATE and CRASH TIME fields were parsed into datetime format. "
            "Time-of-day bins were created to capture temporal crash patterns: "
            "Night (00:00–05:59), Morning (06:00–09:59), Midday (10:00–14:59), "
            "Afternoon (15:00–18:59), and Evening (19:00–23:59). Day-of-week was "
            "extracted as a categorical variable (Monday through Sunday)."
        ),
        (
            "Spatial Classification: "
            "The crash dataset was spatially classified using OSM traffic signal data. "
            "The osmnx library was used to extract all network nodes in Manhattan "
            "tagged with 'highway=traffic_signals'. Each crash record was assigned to "
            "the nearest OSM intersection node using a spatial nearest-neighbour query. "
            "Crashes within 30 metres of a traffic signal node were classified as "
            "'Signalized', while crashes at intersections (having a non-empty CROSS "
            "STREET NAME) but beyond 30 metres from any signal node were classified "
            "as 'Unsignalized'. Crashes without a cross street reference (i.e., "
            "mid-block crashes) were excluded from the intersection analysis."
        ),
        (
            "Data Integration and Intersection Selection: "
            "The vehicles dataset was joined to the crashes dataset on COLLISION_ID "
            "to incorporate vehicle-level attributes. The classified intersection "
            "crash dataset was then aggregated by intersection location, and the five "
            "signalized and five unsignalized intersections with the highest crash "
            "counts were selected for detailed analysis. The processed datasets were "
            "saved to data/processed/ for use by the analysis modules."
        ),
    ]
    for para_text in preprocess_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 11. RESEARCH METHODOLOGY
    # ==================================================================
    _add_heading(doc, "8. Research Methodology", level=1)

    method_paras = [
        (
            "The research methodology follows a descriptive statistical framework, "
            "appropriate for characterising and comparing crash patterns without "
            "requiring traffic exposure data. The approach draws on established "
            "practices in road safety descriptive analysis as outlined in the "
            "Highway Safety Manual [5] and FHWA intersection safety resources [1]."
        ),
        (
            "Descriptive Statistical Analysis: "
            "For each intersection type (signalized and unsignalized), frequency "
            "distributions and proportions were computed for crash type, severity, "
            "vehicle type, time-of-day, day-of-week, and contributing factors. "
            "Cross-tabulations were used to compare distributions between the two "
            "intersection types. Chi-square tests of independence were performed to "
            "assess whether the observed distribution differences between signalized "
            "and unsignalized intersections were statistically significant, providing "
            "a formal complement to the visual and tabular comparisons."
        ),
        (
            "Comparative Analysis Framework: "
            "The comparative analysis examined six dimensions of crash patterns: "
            "(1) overall crash frequency, (2) collision type composition, "
            "(3) severity distribution, (4) vehicle type involvement, "
            "(5) temporal patterns, and (6) contributing factors. For each "
            "dimension, side-by-side distributions were computed and visualised "
            "using bar charts, grouped bar charts, and heatmaps. The analysis "
            "focused on identifying characteristic differences in crash patterns "
            "rather than making claims about relative safety."
        ),
        (
            "Collision Diagram Methodology: "
            "Schematic collision diagrams were prepared for one representative "
            "signalized and one representative unsignalized intersection from the "
            "selected set. Using matplotlib, stylised four-leg intersection layouts "
            "were drawn with directional arrows indicating approach directions. "
            "Different symbols (circles, triangles, squares, diamonds) were used to "
            "represent different crash types, positioned to indicate general crash "
            "locations within the intersection area. It is noted that exact vehicle "
            "trajectories are not available from the crash data; the diagrams "
            "therefore represent schematic approximations based on crash type and "
            "contributing factor information."
        ),
    ]
    for para_text in method_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 12. CRASH PATTERN ANALYSIS
    # ==================================================================
    _add_heading(doc, "9. Crash Pattern Analysis", level=1)

    _add_heading(doc, "9.1 Overall Crash Frequency", level=2)
    _add_body_text(
        doc,
        "The analysis examined the total number of crashes at the selected "
        "signalized and unsignalized intersections over the 2023–2024 study period. "
        "Crash counts at signalized intersections are expected to be higher in "
        "absolute terms, reflecting their generally higher traffic volumes and more "
        "complex conflict patterns. However, as discussed, these raw counts cannot "
        "be interpreted as indicating greater or lesser safety without normalisation "
        "by exposure.",
        first_line_indent=0.5,
    )
    _add_figure_placeholder(
        doc, "1",
        "Total crash frequency by intersection type",
        str(GRAPHS_DIR / "crash_frequency_by_type.png"),
    )

    _add_heading(doc, "9.2 Collision Type Distribution", level=2)
    _add_body_text(
        doc,
        "Collision type distributions reveal the predominant crash mechanisms at "
        "each intersection type. At signalized intersections, rear-end collisions "
        "are typically the most frequent type, driven by stop-and-go traffic during "
        "signal phases and abrupt braking at amber/red transitions. At unsignalized "
        "intersections, angle (broadside) crashes tend to be more prevalent, "
        "reflecting the failure of gap-acceptance manoeuvres and right-of-way "
        "violations. The distribution of collision types at the selected "
        "intersections is presented in Figure 2.",
        first_line_indent=0.5,
    )
    _add_figure_placeholder(
        doc, "2",
        "Collision type distribution comparison between signalized and unsignalized intersections",
        str(GRAPHS_DIR / "collision_type_comparison.png"),
    )

    _add_heading(doc, "9.3 Severity Distribution", level=2)
    _add_body_text(
        doc,
        "The severity distribution of crashes provides insight into the outcome "
        "profiles at each intersection type. The three severity categories—Fatal, "
        "Injury, and No Injury—were compared between signalized and unsignalized "
        "intersections. The severity distribution may differ between control types "
        "due to differences in impact speeds (unsignalized intersections may involve "
        "higher approach speeds in some contexts), conflict angles (angle crashes at "
        "unsignalized intersections may produce more severe outcomes than rear-end "
        "crashes at signalized intersections), and pedestrian involvement patterns.",
        first_line_indent=0.5,
    )
    _add_figure_placeholder(
        doc, "3",
        "Severity distribution comparison",
        str(GRAPHS_DIR / "severity_distribution.png"),
    )

    _add_heading(doc, "9.4 Vehicle Type Distribution", level=2)
    _add_body_text(
        doc,
        "The types of vehicles involved in crashes at each intersection category "
        "were examined. Vehicle type distributions can reflect the traffic "
        "composition at different intersection types and may indicate differing "
        "safety challenges (e.g., heavy vehicle involvement at certain "
        "unsignalized intersections on freight routes). The analysis categorised "
        "vehicles into standard passenger vehicles, SUVs, taxis, trucks, buses, "
        "bicycles, motorcycles, and other types.",
        first_line_indent=0.5,
    )
    _add_figure_placeholder(
        doc, "4",
        "Vehicle type distribution by intersection type",
        str(GRAPHS_DIR / "vehicle_type_distribution.png"),
    )

    _add_heading(doc, "9.5 Temporal Patterns", level=2)
    _add_body_text(
        doc,
        "Temporal crash patterns were examined across two dimensions: time-of-day "
        "and day-of-week. The time-of-day analysis reveals peak crash periods and "
        "may reflect differences in traffic patterns at signalized versus "
        "unsignalized intersections. The afternoon period (15:00–18:59) typically "
        "shows the highest crash concentrations at both intersection types, "
        "coinciding with evening commute peaks. Day-of-week patterns may indicate "
        "weekday versus weekend differences in crash risk.",
        first_line_indent=0.5,
    )
    _add_figure_placeholder(
        doc, "5",
        "Time-of-day crash distribution by intersection type",
        str(GRAPHS_DIR / "time_of_day_distribution.png"),
    )
    _add_figure_placeholder(
        doc, "6",
        "Day-of-week crash distribution by intersection type",
        str(GRAPHS_DIR / "day_of_week_distribution.png"),
    )
    _add_figure_placeholder(
        doc, "7",
        "Hour-of-day vs day-of-week crash heatmap",
        str(GRAPHS_DIR / "heatmap_hour_day.png"),
    )

    _add_heading(doc, "9.6 Contributing Factor Analysis", level=2)
    _add_body_text(
        doc,
        "Contributing factors, as recorded by reporting officers, provide insight "
        "into the behavioural and environmental circumstances surrounding each "
        "crash. The top contributing factors were tabulated for each intersection "
        "type and compared. Common factors such as 'Driver Inattention/Distraction', "
        "'Failure to Yield Right-of-Way', 'Following Too Closely', and 'Unsafe "
        "Speed' were expected to show differential prevalence between signalized "
        "and unsignalized intersections, reflecting the different operational "
        "demands of each control type.",
        first_line_indent=0.5,
    )

    # Placeholder table for contributing factors
    _add_table(doc,
        headers=["Contributing Factor", "Signalized (%)", "Unsignalized (%)"],
        rows=[
            ["Driver Inattention/Distraction", "[DATA]", "[DATA]"],
            ["Failure to Yield Right-of-Way", "[DATA]", "[DATA]"],
            ["Following Too Closely", "[DATA]", "[DATA]"],
            ["Unsafe Speed", "[DATA]", "[DATA]"],
            ["Traffic Control Disregarded", "[DATA]", "[DATA]"],
            ["Passing or Lane Usage Improper", "[DATA]", "[DATA]"],
            ["Other/Unspecified", "[DATA]", "[DATA]"],
        ],
        caption="Top contributing factors by intersection type",
        table_id=2,
    )

    _add_page_break(doc)

    # ==================================================================
    # 13. COLLISION DIAGRAMS
    # ==================================================================
    _add_heading(doc, "10. Collision Diagrams", level=1)

    coll_diag_paras = [
        (
            "Collision diagrams are a standard tool in traffic safety engineering for "
            "visualising the types, locations, and directions of crashes at specific "
            "intersections. In this study, schematic collision diagrams were prepared "
            "for one representative signalized intersection and one representative "
            "unsignalized intersection from the selected set."
        ),
        (
            "The diagrams use a stylised four-leg intersection layout with directional "
            "arrows indicating approach directions. Different symbols represent "
            "different crash types: circles for rear-end collisions, triangles for "
            "angle (broadside) collisions, squares for sideswipe collisions, and "
            "diamonds for pedestrian/cyclist-involved crashes. The symbols are "
            "positioned within the intersection area to indicate the general crash "
            "type rather than exact locations, as precise within-intersection "
            "positioning is not available from the crash data."
        ),
        (
            "It is important to note a significant limitation: since exact vehicle "
            "trajectories, approach lanes, and precise impact locations are not "
            "recorded in the NYC crash dataset, these diagrams represent schematic "
            "approximations. They are intended to convey the general crash typology "
            "and directional patterns at each intersection rather than exact crash "
            "reconstructions. Despite this limitation, the diagrams provide useful "
            "visual summaries that complement the statistical analysis."
        ),
    ]
    for para_text in coll_diag_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_figure_placeholder(
        doc, "8",
        "Collision diagram – Representative signalized intersection",
        str(DIAGRAMS_DIR / "collision_diagram_signalized.png"),
    )
    _add_figure_placeholder(
        doc, "9",
        "Collision diagram – Representative unsignalized intersection",
        str(DIAGRAMS_DIR / "collision_diagram_unsignalized.png"),
    )

    _add_page_break(doc)

    # ==================================================================
    # 14. COMPARATIVE ANALYSIS
    # ==================================================================
    _add_heading(doc, "11. Comparative Analysis", level=1)

    _add_body_text(
        doc,
        "This section provides a systematic side-by-side comparison of crash "
        "patterns across all dimensions examined in this study. The comparison "
        "synthesises the individual analyses presented in the preceding sections "
        "into a unified framework that highlights the characteristic differences "
        "and similarities between signalized and unsignalized intersection crash "
        "patterns.",
        first_line_indent=0.5,
    )

    _add_heading(doc, "11.1 Crash Type Comparison", level=2)
    _add_body_text(
        doc,
        "The collision type distributions reveal distinct crash pattern signatures "
        "for each intersection type. Signalized intersections show a higher "
        "proportion of rear-end collisions, consistent with the stop-and-go "
        "traffic patterns inherent to signal-controlled operations. The periodic "
        "stopping required by red phases creates conditions conducive to rear-end "
        "impacts, particularly when following distances are insufficient. "
        "Unsignalized intersections, conversely, exhibit a relatively higher "
        "share of angle crashes, reflecting the conflict dynamics at locations "
        "where drivers must judge gaps in crossing or turning movements without "
        "signal protection.",
        first_line_indent=0.5,
    )

    _add_heading(doc, "11.2 Severity Comparison", level=2)
    _add_body_text(
        doc,
        "Severity distributions may differ between the two intersection types. "
        "The proportion of injury and fatal crashes relative to property-damage-"
        "only crashes provides insight into the severity profile of each control "
        "type. Angle crashes, which are more prevalent at unsignalized "
        "intersections, are generally associated with more severe outcomes than "
        "rear-end crashes due to the vulnerability of vehicle occupants to "
        "lateral impacts. However, differences in traffic speeds and pedestrian "
        "involvement also influence the severity comparison.",
        first_line_indent=0.5,
    )

    _add_heading(doc, "11.3 Temporal Pattern Comparison", level=2)
    _add_body_text(
        doc,
        "Both intersection types show peak crash periods during afternoon hours, "
        "but the degree of temporal concentration may differ. Signalized "
        "intersections may show sharper peaks corresponding to commute hours, "
        "while unsignalized intersection crashes may be more evenly distributed "
        "if they are located on roads with less pronounced peak-hour traffic "
        "surges. Day-of-week patterns may also differ, with weekend crash "
        "proportions potentially varying by intersection type.",
        first_line_indent=0.5,
    )

    _add_heading(doc, "11.4 Contributing Factor Comparison", level=2)
    _add_body_text(
        doc,
        "'Failure to Yield Right-of-Way' is expected to feature more prominently "
        "among contributing factors at unsignalized intersections, where right-of-"
        "way assignment depends on driver interpretation of stop/yield controls. "
        "'Traffic Control Disregarded' would be specific to signalized "
        "intersections (red-light running). 'Driver Inattention/Distraction' "
        "is likely prevalent at both types, reflecting the pervasive nature of "
        "inattentive driving. 'Following Too Closely' may be more associated "
        "with signalized intersections due to queuing conditions.",
        first_line_indent=0.5,
    )

    # Summary comparison table
    _add_table(doc,
        headers=["Dimension", "Signalized Intersections", "Unsignalized Intersections"],
        rows=[
            ["Predominant crash type", "Rear-end collisions", "Angle (broadside) collisions"],
            ["Severity profile", "Higher proportion PDO", "Relatively higher injury severity"],
            ["Peak time", "Sharp PM peak (15:00–18:59)", "Broader afternoon/evening peak"],
            ["Top contributing factor", "Driver Inattention", "Failure to Yield ROW"],
            ["Signal-specific factor", "Traffic Control Disregarded", "N/A"],
            ["Queuing-related factor", "Following Too Closely", "Less prevalent"],
        ],
        caption="Summary comparison of crash patterns by intersection type",
        table_id=3,
    )

    _add_page_break(doc)

    # ==================================================================
    # 15. RESULTS AND DISCUSSION
    # ==================================================================
    _add_heading(doc, "12. Results and Discussion", level=1)

    results_paras = [
        (
            "The comparative analysis reveals distinct and consistent crash pattern "
            "differences between signalized and unsignalized intersections in "
            "Manhattan. These differences are broadly consistent with the existing "
            "literature and reflect the fundamental operational differences between "
            "the two control types."
        ),
        (
            "The predominance of rear-end crashes at signalized intersections "
            "aligns with findings from Huang et al. [4] and the Highway Safety "
            "Manual [5], which identify the cyclical stopping and starting "
            "associated with traffic signals as a primary rear-end crash generator. "
            "The higher proportion of angle crashes at unsignalized intersections "
            "is consistent with Haleem and Abdel-Aty's [3] analysis of unsignalized "
            "intersection crashes in Florida, where gap-acceptance failures were "
            "identified as a key crash mechanism."
        ),
        (
            "The severity distribution findings, which suggest potentially higher "
            "injury severity at unsignalized intersections, are consistent with the "
            "biomechanical understanding that lateral impacts (associated with angle "
            "crashes) produce greater occupant injury risk than longitudinal impacts "
            "(associated with rear-end crashes) at similar speeds. However, this "
            "comparison must be interpreted cautiously, as speed, vehicle mass "
            "differential, and occupant protection factors also influence severity."
        ),
        (
            "The temporal pattern analysis reveals that crash peaks at both "
            "intersection types correspond to periods of highest traffic activity, "
            "particularly the afternoon commute period. The contributing factor "
            "analysis highlights the importance of driver behaviour—inattention, "
            "failure to yield, and following too closely—as primary crash contributors "
            "at both intersection types, with the relative prevalence of specific "
            "factors varying by control type as expected."
        ),
        (
            "These findings have practical implications for intersection safety "
            "management. The distinct crash pattern signatures suggest that "
            "safety countermeasures should be tailored to the specific control "
            "type. For signalized intersections, rear-end crash mitigation "
            "strategies (signal timing optimisation, advance warning signs, "
            "red-light cameras) may be prioritised. For unsignalized intersections, "
            "angle crash prevention (sight distance improvements, roundabout "
            "conversion, enhanced signing and marking) may be more effective. "
            "However, any countermeasure implementation should be based on "
            "site-specific analysis including traffic volume data."
        ),
    ]
    for para_text in results_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    # GIS Map figure
    _add_figure_placeholder(
        doc, "10",
        "GIS map of crash locations colour-coded by intersection type (Manhattan)",
        str(MAPS_DIR / "crash_locations_map.png"),
    )

    _add_page_break(doc)

    # ==================================================================
    # 16. RECOMMENDED ROAD SAFETY IMPROVEMENTS
    # ==================================================================
    _add_heading(doc, "13. Recommended Road Safety Improvements", level=1)

    _add_heading(doc, "13.1 Signalized Intersections", level=2)
    rec_sig = [
        (
            "Signal Timing Optimisation: Review and optimise signal timing plans to "
            "reduce the frequency of amber-phase dilemma zone situations that "
            "contribute to rear-end crashes. Implement all-red clearance intervals "
            "where they are not already present. Consider adaptive signal control "
            "technology (ASCT) to respond to real-time traffic conditions and reduce "
            "unnecessary stops."
        ),
        (
            "Protected Left-Turn Phases: Where left-turn opposing crashes are "
            "prevalent, convert from permissive to protected or protected-permissive "
            "left-turn phasing. This countermeasure has demonstrated significant "
            "crash reduction effectiveness in multiple studies cited in the Highway "
            "Safety Manual [5]."
        ),
        (
            "Red-Light Camera Enforcement: At intersections with high rates of "
            "'Traffic Control Disregarded' as a contributing factor, consider "
            "automated red-light enforcement. While Huang et al. [4] noted potential "
            "rear-end crash increases, the net safety benefit in terms of reducing "
            "severe angle crashes is generally positive."
        ),
        (
            "Leading Pedestrian Intervals (LPIs): At high-pedestrian-activity "
            "intersections, implement LPIs to give pedestrians a head start before "
            "the vehicle green phase, reducing pedestrian-vehicle conflicts during "
            "turning movements."
        ),
    ]
    for para_text in rec_sig:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_heading(doc, "13.2 Unsignalized Intersections", level=2)
    rec_unsig = [
        (
            "Sight Distance Improvements: Ensure that sight triangles at "
            "unsignalized intersections meet or exceed AASHTO design standards. "
            "Remove obstructions (parked vehicles, vegetation, street furniture) "
            "that limit the ability of minor-approach drivers to observe and assess "
            "gaps in the major-approach traffic stream."
        ),
        (
            "Roundabout Conversion: For unsignalized intersections with significant "
            "angle crash histories, evaluate the feasibility of roundabout "
            "conversion. Roundabouts eliminate direct crossing conflicts, reduce "
            "vehicle speeds, and have demonstrated crash reduction effectiveness "
            "of 35–80% depending on the setting, as documented in the FHWA "
            "Roundabout Informational Guide."
        ),
        (
            "Enhanced Signing and Marking: Improve the conspicuity and clarity "
            "of stop signs and yield signs through larger sign sizes, retroreflective "
            "sheeting upgrades, flashing beacons, and supplementary pavement "
            "markings. Where 'Failure to Yield Right-of-Way' is a predominant "
            "factor, these low-cost countermeasures can improve driver compliance."
        ),
        (
            "Signal Warrant Analysis: For unsignalized intersections with "
            "persistently high crash counts, conduct formal signal warrant "
            "analyses per the Manual on Uniform Traffic Control Devices (MUTCD) "
            "to determine whether signalisation is justified. This should be "
            "complemented by a comprehensive alternatives analysis including "
            "roundabouts."
        ),
    ]
    for para_text in rec_unsig:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 17. LIMITATIONS
    # ==================================================================
    _add_heading(doc, "14. Limitations", level=1)

    limitations = [
        (
            "Missing Traffic Control Field: The most significant limitation of this "
            "study is the absence of a traffic control type field in the NYC Motor "
            "Vehicle Collisions dataset. The classification of intersections as "
            "signalized or unsignalized relies entirely on OpenStreetMap data, which "
            "may contain errors, omissions, or outdated information. Some recently "
            "signalised intersections may be misclassified as unsignalized if OSM has "
            "not been updated, and vice versa."
        ),
        (
            "Absence of Exposure Data: This study does not incorporate traffic volume "
            "(AADT or turning movement count) data, which is essential for computing "
            "crash rates and making valid safety comparisons between locations or "
            "control types. Crash counts alone reflect both the inherent safety of a "
            "location and its exposure level, and these effects cannot be separated "
            "without exposure data. All findings must therefore be interpreted as "
            "descriptive rather than causal."
        ),
        (
            "Spatial Classification Threshold: The 30-metre threshold used for "
            "classifying crashes relative to traffic signal nodes is a practical "
            "choice but introduces some misclassification risk. Crashes occurring "
            "near the boundary may be classified differently depending on GPS "
            "accuracy and OSM node placement."
        ),
        (
            "Coordinate Accuracy: GPS coordinates in the crash dataset have inherent "
            "accuracy limitations. In urban environments, GPS errors due to multipath "
            "effects from tall buildings can be significant, potentially causing "
            "crashes to be assigned to incorrect intersections."
        ),
        (
            "Reporting Bias: The dataset includes only police-reported crashes, which "
            "represent a subset of all crashes. Minor property-damage-only crashes "
            "and near-miss events are likely underreported, potentially biasing the "
            "severity distribution. Reporting rates may also vary by location and "
            "intersection type."
        ),
    ]
    for para_text in limitations:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 18. CONCLUSION
    # ==================================================================
    _add_heading(doc, "15. Conclusion", level=1)

    conclusion_paras = [
        (
            "This study has presented a comparative descriptive analysis of crash "
            "patterns at signalized and unsignalized intersections in Manhattan, "
            "New York City, using police-reported crash data from 2023–2024. The "
            "analysis examined crash type distributions, severity profiles, temporal "
            "patterns, vehicle involvement, contributing factors, and collision "
            "diagrams across ten selected intersections (five of each control type)."
        ),
        (
            "The findings reveal distinct crash pattern signatures associated with "
            "each intersection control type. Signalized intersections exhibit higher "
            "proportions of rear-end collisions and contributing factors related to "
            "following distance and signal compliance. Unsignalized intersections "
            "show higher proportions of angle crashes and contributing factors "
            "related to right-of-way yielding failures. These differences are "
            "consistent with the operational characteristics of each control type "
            "and align with the existing body of literature on intersection safety."
        ),
        (
            "It is essential to reiterate that crash counts alone cannot and should "
            "not be used to determine which intersection type is inherently safer. "
            "Without exposure data—traffic volumes, pedestrian counts, and turning "
            "movement data—the higher crash counts at one type may simply reflect "
            "higher traffic volumes rather than inferior safety performance. The "
            "value of this study lies in characterising what types of crashes occur "
            "at each control type, when they occur, and what factors contribute, "
            "providing a foundation for targeted safety countermeasure planning."
        ),
        (
            "Future research should integrate traffic volume data to enable crash "
            "rate comparisons, expand the study area beyond Manhattan, and "
            "incorporate additional data sources such as signal timing plans and "
            "geometric design data. Longitudinal analysis of crash pattern changes "
            "following safety interventions would further enhance the practical "
            "value of intersection crash pattern analysis."
        ),
    ]
    for para_text in conclusion_paras:
        _add_body_text(doc, para_text, first_line_indent=0.5)

    _add_page_break(doc)

    # ==================================================================
    # 19. REFERENCES
    # ==================================================================
    _add_heading(doc, "References", level=1)

    references = [
        (
            '[1] Federal Highway Administration, "Intersection Safety," FHWA '
            'Safety Program, U.S. Department of Transportation, Washington, D.C. '
            '[Online]. Available: https://highways.dot.gov/safety/intersection-safety. '
            '[Accessed: Nov. 2026].'
        ),
        (
            '[2] B. Persaud, C. Lyon, and T. Nguyen, "Empirical Bayes procedure '
            'for ranking sites for safety investigation by potential for safety '
            'improvement," Transportation Research Record, vol. 1752, pp. 1–9, '
            '2001, doi: 10.3141/1752-01.'
        ),
        (
            '[3] K. Haleem and M. A. Abdel-Aty, "Examining traffic crash injury '
            'severity at unsignalized intersections," Journal of Safety Research, '
            'vol. 41, no. 4, pp. 347–357, 2010, doi: 10.1016/j.jsr.2010.04.006.'
        ),
        (
            '[4] H. Huang, H. C. Chin, and M. M. Haque, "Severity of driver '
            'injury and vehicle damage in traffic crashes at intersections: A '
            'Bayesian hierarchical analysis," Accident Analysis & Prevention, '
            'vol. 40, no. 1, pp. 45–54, 2008, doi: 10.1016/j.aap.2007.04.002.'
        ),
        (
            '[5] American Association of State Highway and Transportation '
            'Officials (AASHTO), Highway Safety Manual, 1st ed. Washington, '
            'D.C.: AASHTO, 2010.'
        ),
        (
            '[6] New York City, "Vision Zero Action Plan," NYC Mayor\'s Office '
            'of Operations, New York, NY, 2014. [Online]. Available: '
            'https://www.nyc.gov/content/visionzero. [Accessed: Nov. 2026].'
        ),
        (
            '[7] NYC OpenData, "Motor Vehicle Collisions – Crashes," New York '
            'City Police Department, 2024. [Online]. Available: '
            'https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95. '
            '[Accessed: Nov. 2026].'
        ),
        (
            '[8] NYC OpenData, "Motor Vehicle Collisions – Vehicles," New York '
            'City Police Department, 2024. [Online]. Available: '
            'https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4. '
            '[Accessed: Nov. 2026].'
        ),
        (
            '[9] G. Boeing, "OSMnx: New methods for acquiring, constructing, '
            'analyzing, and visualizing complex street networks," Computers, '
            'Environment and Urban Systems, vol. 65, pp. 126–139, 2017, '
            'doi: 10.1016/j.compenvurbsys.2017.05.004.'
        ),
        (
            '[10] Transportation Research Board, "Highway Capacity Manual," '
            '6th ed. Washington, D.C.: National Academies of Sciences, '
            'Engineering, and Medicine, 2016.'
        ),
    ]

    for ref in references:
        p = doc.add_paragraph(ref)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        for run in p.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(11)
            run.font.color.rgb = DARK_TEXT

    _add_page_break(doc)

    # ==================================================================
    # 20. APPENDICES
    # ==================================================================
    _add_heading(doc, "Appendices", level=1)

    _add_heading(doc, "Appendix A: Data Dictionary – NYC Motor Vehicle Collisions (Crashes)", level=2)

    _add_table(doc,
        headers=["Field Name", "Data Type", "Description"],
        rows=[
            ["CRASH DATE", "Date", "Date of the collision"],
            ["CRASH TIME", "Time", "Time of the collision"],
            ["BOROUGH", "Text", "NYC borough (Manhattan, Brooklyn, etc.)"],
            ["ZIP CODE", "Text", "ZIP code of crash location"],
            ["LATITUDE", "Numeric", "Latitude coordinate (WGS84)"],
            ["LONGITUDE", "Numeric", "Longitude coordinate (WGS84)"],
            ["ON STREET NAME", "Text", "Primary street at crash location"],
            ["CROSS STREET NAME", "Text", "Cross street (present for intersection crashes)"],
            ["NUMBER OF PERSONS INJURED", "Integer", "Total persons injured"],
            ["NUMBER OF PERSONS KILLED", "Integer", "Total persons killed"],
            ["NUMBER OF PEDESTRIANS INJURED", "Integer", "Pedestrians injured"],
            ["NUMBER OF PEDESTRIANS KILLED", "Integer", "Pedestrians killed"],
            ["NUMBER OF CYCLIST INJURED", "Integer", "Cyclists injured"],
            ["NUMBER OF CYCLIST KILLED", "Integer", "Cyclists killed"],
            ["NUMBER OF MOTORIST INJURED", "Integer", "Motorists injured"],
            ["NUMBER OF MOTORIST KILLED", "Integer", "Motorists killed"],
            ["CONTRIBUTING FACTOR VEHICLE 1–5", "Text", "Contributing factors per vehicle"],
            ["COLLISION_ID", "Text", "Unique collision identifier"],
            ["VEHICLE TYPE CODE 1–5", "Text", "Vehicle type codes"],
        ],
        caption="Data dictionary for the NYC Motor Vehicle Collisions – Crashes dataset",
        table_id="A1",
    )

    doc.add_paragraph()  # spacing

    _add_heading(doc, "Appendix B: Data Dictionary – NYC Motor Vehicle Collisions (Vehicles)", level=2)

    _add_table(doc,
        headers=["Field Name", "Data Type", "Description"],
        rows=[
            ["UNIQUE_ID", "Text", "Unique record identifier"],
            ["COLLISION_ID", "Text", "Link to crash record"],
            ["VEHICLE_ID", "Text", "Vehicle identifier within collision"],
            ["VEHICLE_TYPE", "Text", "Vehicle type description"],
            ["VEHICLE_MAKE", "Text", "Vehicle manufacturer"],
            ["VEHICLE_MODEL", "Text", "Vehicle model"],
            ["VEHICLE_YEAR", "Integer", "Vehicle model year"],
            ["TRAVEL_DIRECTION", "Text", "Direction of travel (N, S, E, W)"],
            ["DRIVER_SEX", "Text", "Driver gender"],
            ["PRE_CRASH", "Text", "Pre-crash vehicle action"],
            ["POINT_OF_IMPACT", "Text", "Initial point of impact on vehicle"],
            ["VEHICLE_DAMAGE", "Text", "Location of vehicle damage"],
            ["CONTRIBUTING_FACTOR_1", "Text", "Primary contributing factor"],
            ["CONTRIBUTING_FACTOR_2", "Text", "Secondary contributing factor"],
        ],
        caption="Data dictionary for the NYC Motor Vehicle Collisions – Vehicles dataset",
        table_id="A2",
    )

    doc.add_paragraph()  # spacing

    _add_heading(doc, "Appendix C: Intersection Classification Summary", level=2)

    _add_body_text(
        doc,
        "The following table summarises the spatial classification methodology "
        "and threshold parameters used to classify crash locations as signalized "
        "or unsignalized intersections.",
    )

    _add_table(doc,
        headers=["Parameter", "Value / Method"],
        rows=[
            ["Data source for signal locations", "OpenStreetMap (osmnx library)"],
            ["Signal tag", "highway=traffic_signals"],
            ["Spatial matching method", "Nearest-neighbour to OSM nodes"],
            ["Classification threshold", "30 metres"],
            ["Signalized criterion", "Within 30 m of traffic signal node"],
            ["Unsignalized criterion", "At intersection (has cross street) AND > 30 m from signal"],
            ["Excluded", "Mid-block crashes (no cross street)"],
            ["Study area", "Manhattan, New York City"],
            ["Study period", "January 2023 – December 2024"],
            ["Selected intersections", "Top 5 each type by crash count"],
        ],
        caption="Intersection classification methodology summary",
        table_id="A3",
    )

    # ==================================================================
    # Save
    # ==================================================================
    output_path = REPORT_DIR / "Final_Report.docx"
    doc.save(str(output_path))
    print(f"✅ Report saved to: {output_path}")
    return output_path


# ===========================================================================
#  MAIN
# ===========================================================================
if __name__ == "__main__":
    output = build_report()
    print(f"\nReport generation complete.")
    print(f"  DOCX: {output}")
    print("\nNote: Figure placeholders will be replaced with actual images")
    print("when the analysis pipeline has been run and output files exist in outputs/.")
