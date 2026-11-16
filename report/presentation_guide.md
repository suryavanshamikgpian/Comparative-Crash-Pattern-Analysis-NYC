# PRESENTATION PLANNING & RECORDING GUIDE
## Project 7: Comparative Crash Pattern Analysis at Signalized and Unsignalized Intersections 
**Institution:** Indian Institute of Technology Kharagpur  
**Observation Period:** 2023–2024 (Manhattan, New York City)  

---

## 1. VISUAL DESIGN SYSTEM: MONOCHROMATIC NAVY THEME

When designing your slides in Microsoft PowerPoint, Apple Keynote, or Google Slides, maintain the exact same professional monochromatic navy theme used in your research report:

| Element | Hex Code | Visual Application |
| :--- | :--- | :--- |
| **Dark Navy** | `#142D4E` | Slide titles, key metric callout numbers, major cards |
| **Deep Blue** | `#234B70` | Subheadings, category headers, section dividers |
| **Medium Blue** | `#4778A8` | Secondary bars, chart elements, accent lines |
| **Light Blue** | `#91B6D5` | Grid lines, table borders, inactive elements |
| **Very Light Blue**| `#EAF1F8` | Card backgrounds, alternating table rows, callout boxes |
| **Pure White** | `#FFFFFF` | Slide background (keeps slides clean, high contrast) |
| **Dark Text** | `#202833` | Body text, captions, data labels |

### Slide Typography Rules
- **Font Family:** Arial, Calibri, Helvetica, or Georgia (clean, readable sans-serif).
- **Hierarchy:** Slide Titles: 28–32 pt (Bold, Dark Navy); Subheadings: 18–20 pt; Body text / bullet points: 14–16 pt; Source notes: 9–10 pt.
- **Rule of Thumb:** No slide should contain walls of text. Use 3 to 4 concise bullet points per slide, paired with actual analysis figures.

---

## 2. RECOMMENDED 9-SLIDE STRUCTURE & CONTENT BLUEPRINT

### Slide 1: Title & Administrative Information
* **Slide Purpose:** Establish academic credibility, project scope, and institutional context.
* **Key Visual Elements:**
  * Clean white background with Dark Navy header bar or top accent.
  * Project Title: *Comparative Crash Pattern Analysis at Signalized and Unsignalized Intersections*.
  * Subtitle: *Empirical Evidence from Manhattan, New York City (2023–2024)*.
  * Student Name, Roll Number, Course Code, and Submission Date.
* **Suggested Image:** Schematic intersection icon or thumbnail of the Manhattan GIS crash map.
* **Key Technical Points:** State clearly that this is an empirical road safety investigation under Assignment 2.

---

### Slide 2: Research Problem, Context & Core Objectives
* **Slide Purpose:** Explain *why* intersection safety is critical and what this study aims to accomplish.
* **Key Visual Elements:** Two-column card layout (`#EAF1F8` background cards).
  * *Left Card (Problem Statement):* Urban intersections concentrate complex multidirectional traffic conflicts. Understanding crash typology across traffic control devices is vital for Vision Zero planning.
  * *Right Card (Research Objectives):*
    1. Compare crash frequency and collision typologies across signalized and unsignalized junctions.
    2. Identify recurring conflict patterns using schematic collision diagrams.
    3. Formulate data-supported geometric and operational safety countermeasures.
* **Critical Distinction to Emphasize:** Highlight the central methodological constraint: **Crash counts alone cannot determine relative safety without exposure (traffic volume) normalization.**

---

### Slide 3: Data Sources, Integration & Spatial Classification
* **Slide Purpose:** Detail the real-world datasets used and the spatial methodology developed to classify intersection control.
* **Key Visual Elements:** A 3-step pipeline flow diagram (Box 1 → Box 2 → Box 3).
  * *Step 1:* Primary Crash Data (NYC Open Data: 2,305,623 records, filtered to 23,191 Manhattan crashes for 2023–2024).
  * *Step 2:* Vehicle-level Supplementary Data (3,438,320 records merged via `COLLISION_ID` to capture vehicle type and maneuver).
  * *Step 3:* Spatial Matching with Official NYC DOT Traffic Signal Inventory & OpenStreetMap nodes using a 30-metre geodetic buffer in UTM Zone 18N (`EPSG:32618`).
* **Summary Table on Slide:**
  * Signalized Intersections: 1,455 crashes (1,149 unique locations)
  * Unsignalized Intersections: 7,911 crashes (6,411 unique locations)
  * Mid-block crashes (excluded from intersection analysis): 13,825 records

---

### Slide 4: Spatial GIS Distribution & Crash Heatmap
* **Slide Purpose:** Show the geographic spread of intersection collisions and temporal density peaks.
* **Visuals to Embed:**
  * *Left Graphic:* `outputs/maps/crash_locations_map.png` (Spatial GIS plot showing Signalized vs Unsignalized points across Manhattan).
  * *Right Graphic:* `outputs/graphs/heatmap_hour_day.png` (Hour-of-day vs Day-of-week collision density).
* **Key Findings to Highlight:**
  * Spatial clustering along high-density avenues (8th Ave, 1st Ave, Madison Ave, Delancey St corridors).
  * Temporal crash peaks concentrated between 15:00 and 19:00 (PM peak commute) across all weekdays.
  * Nighttime crashes (00:00–05:00) exhibit higher proportion of speeding and impairment.

---

### Slide 5: Crash Typology & Contributing Factor Comparison
* **Slide Purpose:** Present the empirical comparison of collision types.
* **Visual to Embed:** `outputs/graphs/collision_type_comparison.png` (Grouped bar chart).
* **Key Statistical Metrics (from Table 2):**
  * *Distracted Driving:* ~27.0% at signalized vs 26.4% at unsignalized.
  * *Improper Maneuvers (lane changes/turning):* 18.6% at signalized vs 18.5% at unsignalized.
  * *Failure to Yield:* 3.6% at signalized vs 2.4% at unsignalized (statistically significant difference, $\chi^2 = 27.22$, $p = 0.0024$).
  * *Traffic Control Violations (red-light/stop-sign running):* Observed at both intersection categories.
* **Interpretation:** Both control types are heavily impacted by human behavioral factors (distraction), but yield failures and turning conflicts dominate intersection-specific conflict points.

---

### Slide 6: Severity Profiles & Vulnerable Road User Vulnerability
* **Slide Purpose:** Contrast the outcome severity between signalized and unsignalized locations.
* **Visual to Embed:** `outputs/graphs/severity_distribution.png` (Stacked percentage bar chart).
* **Key Metrics (from Table 3 & Chi-Square test):**
  * *Injury Rate:* **35.12%** at signalized intersections vs **27.81%** at unsignalized intersections ($\chi^2 = 32.09$, $p < 0.0001$).
  * *Why does signalized show higher injury proportion?* Higher vehicular throughput, wider multi-lane cross-sections, higher pedestrian crossing density, and high-speed perpendicular red-light running impacts.
  * *Vehicle Composition (`outputs/graphs/vehicle_type_distribution.png`):* Sedans and SUVs represent >70% of involvements; taxis and commercial delivery vehicles account for significant urban friction.

---

### Slide 7: Schematic Collision Diagrams
* **Slide Purpose:** Demonstrate how collisions occur in physical intersection space.
* **Visuals to Embed:**
  * *Left:* `outputs/diagrams/collision_diagram_signalized.png` (Representative Signalized: South St corridor).
  * *Right:* `outputs/diagrams/collision_diagram_unsignalized.png` (Representative Unsignalized: E 125th St corridor).
* **Key Diagrammatic Observations:**
  * *Signalized Diagram:* Rear-end symbols (●) clustered on approaches; turning vs through conflicts (▲) inside the central box; pedestrian conflict points (◆) at crosswalk legs.
  * *Unsignalized Diagram:* Angle and failure-to-yield crashes (▲) concentrated at the cross-street entry points due to restricted sight distance and gap acceptance errors.
  * *Mandatory Technical Disclosure:* Acknowledge that because police reports do not log micro-trajectories, these diagrams are standardized schematic representations of recorded collision types and approach directions.

---

### Slide 8: Data-Driven Road Safety Improvements
* **Slide Purpose:** Translate analytical findings into actionable civil engineering solutions.
* **Visual Layout:** Two structured recommendation cards (`#EAF1F8`).
  * *For Signalized Intersections:*
    1. **Leading Pedestrian Intervals (LPI):** Provide 3–7 second dedicated pedestrian walk phase before turning green, mitigating yield conflicts.
    2. **Protected Left-Turn Phasing:** Eliminate permissive left-turn conflict points where angle crashes cluster.
    3. **Automated Enforcement:** Red-light cameras at high-frequency violation approaches.
  * *For Unsignalized Intersections:*
    1. **Daylighting (Sight Distance Enhancement):** Restrict curbside parking 6–9 m from corners to clear sight triangles for minor-street drivers.
    2. **Curb Extensions (Bulb-outs) & High-Visibility Crosswalks:** Reduce pedestrian crossing distances and calm approach speeds.
    3. **Signal Warrant Evaluation:** Conduct MUTCD Warrant 1–3 traffic volume and crash studies to evaluate whether high-crash unsignalized sites justify signalization or all-way stop control.

---

### Slide 9: Methodological Limitations & Conclusion
* **Slide Purpose:** Provide an honest, rigorous academic conclusion and outline future research directions.
* **Key Bullet Points:**
  * *Primary Limitation:* Lack of traffic volume (AADT/VMT) and pedestrian exposure data prevents calculating true crash *rates* ($CR = \frac{C \times 10^6}{V}$).
  * *Spatial Matching Constraint:* 30 m geocoding buffer relies on reported GPS accuracy and OSM node currency.
  * *Core Conclusion:* Signalized and unsignalized intersections display fundamentally distinct collision typologies. Signalized junctions experience a higher proportion of injury-producing events driven by multilane turning and pedestrian friction, while unsignalized junctions are dominated by sight-distance and gap-acceptance failures.
  * *Final Closing Statement:* Crash counts alone do not indicate safety; comprehensive safety management requires combining crash records with exposure data, geometric audits, and targeted countermeasures.

---

## 3. ORAL SCRIPT & PRESENTATION DELIVERY GUIDELINES

### Timing Plan (Target: 8–10 Minutes)
* **0:00 – 1:00:** Slide 1 & 2 (Introduction, Objectives, Problem Statement)
* **1:00 – 2:30:** Slide 3 (Data Sources, Cleaning, Spatial Classification Pipeline)
* **2:30 – 4:00:** Slide 4 & 5 (Spatial/Temporal Patterns & Collision Typologies)
* **4:00 – 5:30:** Slide 6 (Severity Comparison & Statistical Significance)
* **5:30 – 7:00:** Slide 7 (Collision Diagrams & Conflict Mechanisms)
* **7:00 – 8:30:** Slide 8 (Engineering Countermeasures & Recommendations)
* **8:30 – 9:30:** Slide 9 (Limitations, Synthesis & Conclusion)

### Suggested Phrasing for Difficult Concepts

#### 1. How to Explain the Lack of Exposure Data (Crucial):
> *"A central principle of highway safety engineering is that collision frequency is heavily governed by vehicular and pedestrian exposure. In this investigation, we analyzed 1,455 crashes at signalized intersections and 7,911 crashes at unsignalized intersections in Manhattan. However, I want to emphasize that we cannot conclude that unsignalized intersections are inherently less safe based on count alone. Signalized intersections are typically placed at major arterial crossroads with high traffic volumes, while unsignalized junctions in Manhattan often occur at lower-volume local street crossings. Without Average Annual Daily Traffic (AADT), our study provides a rigorous descriptive comparison of crash patterns, rather than a relative risk index."*

#### 2. How to Explain the Chi-Square Statistical Test:
> *"To verify whether the observed differences between signalized and unsignalized crash patterns are statistically meaningful or merely random variations, we conducted Pearson chi-square contingency tests. For severity distribution, our test yielded a chi-square statistic of 32.09 with a p-value less than 0.0001, demonstrating that the higher injury rate of 35.1% at signalized intersections compared to 27.8% at unsignalized intersections is statistically significant. Similarly, collision type distributions differed significantly with a p-value of 0.0024, confirming distinct conflict mechanisms across control types."*

#### 3. How to Explain the Collision Diagrams:
> *"On Slide 7, we present schematic collision diagrams for representative high-frequency junctions. It is critical to state a data limitation here: NYPD collision reports record crash coordinates, street names, and contributing factors, but do not record micro-level vehicle trajectories or approach lanes. Therefore, we used a standardized four-leg schematic layout to map the recorded collision types—distinguishing rear-end, angle, sideswipe, and pedestrian crashes with distinct symbols and monochromatic shades. This allows us to visualize how traffic friction concentrates at approach stops versus cross-street entry points."*

---

## 4. PRE-RECORDING CHECKLIST

Before recording your presentation video, verify each item:

- [ ] **Image Insertion:** High-resolution PNG figures from `outputs/graphs/` and `outputs/diagrams/` are clearly visible on the slides with legible axis labels.
- [ ] **Technical Numbers Verified:** Ensure the numbers spoken match the report tables (Total Manhattan crashes: 23,191; Signalized: 1,455; Unsignalized: 7,911; Signalized injury rate: 35.12%; Unsignalized injury rate: 27.81%).
- [ ] **Audio & Microphone:** Test audio levels. Speak at a measured, confident academic pace with clear enunciation.
- [ ] **Video Framing:** Ensure your webcam shows your face clearly in a quiet, well-lit environment.
- [ ] **Screen Sharing:** Set display resolution to 1080p (1920x1080) so that all slide text and chart annotations are razor-sharp.
- [ ] **Timing Check:** Rehearse once to ensure total presentation time remains between 8 and 10 minutes.

---

## 5. SUBMISSION DIRECTORY STRUCTURE

Assemble your Google Drive submission folder following this exact required hierarchy:

```
Assignment_2_Project_7/
│
├── 01_Final_Report/
│   ├── Final_Report.docx                 (2.4 MB - Complete report with embedded figures)
│   └── Final_Report.pdf                  (2.9 MB - Compiled publication PDF with page numbers)
│
├── 02_Presentation/
│   └── Student_Created_Presentation.pptx (Created independently by you using this guide)
│
├── 03_Code_and_Dataset/
│   ├── Source_Code/
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── data_collection.py
│   │   │   ├── preprocessing.py
│   │   │   ├── crash_analysis.py
│   │   │   ├── visualisation.py
│   │   │   ├── collision_diagrams.py
│   │   │   ├── report_generator.py
│   │   │   └── docx_to_pdf.py
│   │   ├── notebooks/
│   │   │   └── crash_pattern_analysis.ipynb
│   │   └── outputs/
│   │       ├── graphs/                   (8 PNG charts at 300 DPI)
│   │       ├── diagrams/                 (10 collision diagrams at 300 DPI)
│   │       ├── maps/                     (Static PNG map & interactive Folium HTML map)
│   │       └── tables/                   (11 analytical CSV summary tables)
│   ├── Dataset/
│   │   ├── raw/                          (Download links / instructions in DATA_SOURCES.md)
│   │   └── processed/
│   │       ├── manhattan_crashes_classified.csv  (7.9 MB)
│   │       ├── nyc_traffic_signals.gpkg          (913 KB)
│   │       ├── top_signalized.csv                (15.6 KB)
│   │       └── top_unsignalized.csv              (30.3 KB)
│   ├── README.md                         (Full reproducibility & execution instructions)
│   ├── DATA_SOURCES.md                   (Official citations & variable metadata)
│   ├── requirements.txt                  (Python environment dependencies)
│   └── GitHub_Link.txt                   (Link to your GitHub repository)
│
└── 04_Recorded_Presentation/
    └── Presentation_Recording.mp4        (Recorded video presentation delivered by you)
```
EOF

