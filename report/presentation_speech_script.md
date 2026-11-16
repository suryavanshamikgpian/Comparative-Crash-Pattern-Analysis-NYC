# 10-Minute Slide-by-Slide Oral Presentation Script
## Comparative Crash Pattern Analysis at Signalized and Unsignalized Intersections
**Empirical Evidence from Manhattan, New York City (2023–2024)**  
*Author:* Suryavansham | Roll No. 23BT30032  
*Course:* CE60012 Transportation Safety / Road Safety Engineering  
*Context:* Assignment 2 — Project 7 | IIT Kharagpur  
*Target Duration:* Exactly 9 minutes 45 seconds to 10 minutes (Average speaking pace: ~130 words/min with deliberate pauses)

---

### Delivery Guidelines:
- **`[pause]`**: Brief 1- to 2-second pause to let a point sink in or take a breath.
- **`*word*`**: Vocal emphasis / stress.
- **`[gesture/glance]`**: Physical stage cue (looking at the screen, engaging the jury).
- **`[advance slide]`**: Exact moment to click to the next slide.

---

### Timing Overview
| Slide # | Title / Topic | Target Time | Cumulative Elapsed |
| :---: | :--- | :---: | :---: |
| **Slide 1** | Title Slide & Research Context | 45 sec | 0:45 |
| **Slide 2** | The Problem, Objectives & Methodological Constraint | 60 sec | 1:45 |
| **Slide 3** | Data Pipeline & Spatial Classification Methodology | 65 sec | 2:50 |
| **Slide 4** | Spatial Crash Distribution & Corridor Concentrations | 55 sec | 3:45 |
| **Slide 5** | Temporal Patterns: Diurnal & Weekly Crash Cycles | 60 sec | 4:45 |
| **Slide 6** | Contributing Factors & Behavioral Contrasts ($\chi^2 = 27.22$) | 65 sec | 5:50 |
| **Slide 7** | Crash Severity & The Signalized Injury Rate Paradox ($\chi^2 = 32.09$) | 75 sec | 7:05 |
| **Slide 8** | Micro-Level Collision Diagrams & Conflict Mechanics | 65 sec | 8:10 |
| **Slide 9** | Data-Driven Countermeasures & Engineering Improvements | 60 sec | 9:10 |
| **Slide 10** | Conclusions, Academic Limitations & Takeaway | 50 sec | 10:00 |

---

## Slide 1: Title Slide
**Visual:** Project Title, Author Details (Suryavansham, 23BT30032), IIT Kharagpur, $N = 9,366$ intersection crashes.  
**Target Duration:** 45 seconds `[Elapsed: 0:00 – 0:45]`

> "Good morning, respected professors and evaluation committee members.
> 
> My name is Suryavansham, Roll Number 23BT30032, and today I will be presenting my work on **Project 7: Comparative Crash Pattern Analysis at Signalized and Unsignalized Intersections**. `[pause]`
> 
> In transportation engineering, intersections are inherently the most hazardous nodes of any road network because that is where traffic streams diverge, merge, and cross paths. 
> 
> In this study, we evaluate empirical crash records from Manhattan, New York City, spanning 2023 and 2024. Analyzing a filtered sample of over nine thousand three hundred intersection collisions, our objective is to uncover how traffic control mechanisms fundamentally alter collision signatures, injury outcomes, and failure modes. `[pause]`
> 
> Let us begin by looking at why this distinction matters." `[advance slide]`

---

## Slide 2: Why Intersection Crashes Matter
**Visual:** The problem, three objectives, and the key methodological constraint (exposure data).  
**Target Duration:** 60 seconds `[Elapsed: 0:45 – 1:45]`

> "Every day in an urban road network, intersections force motor vehicles, cyclists, and pedestrians to share limited spatial geometry. `[pause]` 
> 
> When traffic signals are introduced, they separate conflicting movements in *time*. Unsignalized intersections, on the other hand, rely on right-of-way priority rules and driver gap acceptance. 
> 
> To design targeted interventions under Vision Zero frameworks, we framed three specific research objectives: `[glance at slide]`
> 1. *First*, compare collision types, severity levels, and reported contributing factors between both control types.
> 2. *Second*, examine their temporal stability across hours of the day and days of the week.
> 3. And *third*, reconstruct localized collision diagrams to recommend concrete civil engineering countermeasures. `[pause]`
> 
> Now, before presenting the data, I must emphasize a foundational methodological constraint: `[pause]` 
> Our dataset does not contain exposure data, such as entering traffic volumes or pedestrian counts. Therefore, as mandated by rigorous road safety methodology, **this study is strictly a descriptive pattern comparison**. We cannot, and do not, rank overall intersection safety based on raw crash counts alone." `[advance slide]`

---

## Slide 3: Data and Intersection Classification
**Visual:** Pipeline from 2.3M records down to 23,191 Manhattan crashes, 3.4M vehicle records, and UTM 18N 30m buffer classification.  
**Target Duration:** 65 seconds `[Elapsed: 1:45 – 2:50]`

> "Let us look at how the data pipeline was engineered. `[glance at diagram]`
> 
> We extracted the raw NYC Motor Vehicle Collisions database containing over 2.3 million records, alongside a secondary dataset of 3.4 million registered vehicle records.
> 
> We filtered these records to the dense urban environment of Manhattan for the calendar years 2023 and 2024, yielding twenty-three thousand one hundred and ninety-one geocoded crashes. `[pause]`
> 
> However, the raw NYPD crash dataset has an important limitation: it does *not* record whether an intersection is signalized. 
> 
> To resolve this objectively, we integrated OpenStreetMap intersection nodes and NYC Department of Transportation official signal inventories. We projected all coordinates into UTM Zone 18N to preserve metric distances, and executed a 30-meter geodetic buffer analysis. `[pause]`
> 
> The results were clear:
> - Thirteen thousand eight hundred crashes were identified as mid-block segments and excluded from our intersection scope.
> - That left **nine thousand three hundred and sixty-six** validated intersection crashes: 
>   One thousand four hundred and fifty-five at signalized locations across 1,149 junctions, and seven thousand nine hundred and eleven at unsignalized locations across 6,411 junctions. 
> 
> Every record was joined with its corresponding vehicle-level factors." `[advance slide]`

---

## Slide 4: Where Crashes Occur (Spatial Distribution)
**Visual:** GIS spatial map of Manhattan showing signalized corridors vs. unsignalized local spread.  
**Target Duration:** 55 seconds `[Elapsed: 2:50 – 3:45]`

> "This brings us to the spatial geography of these incidents. `[gesture to the map]`
> 
> As you can observe on the GIS density map, crash occurrences form distinct spatial typologies. 
> 
> Signalized crashes — shown here in dark navy markers — strictly trace the primary multi-lane arterial corridors: avenues like Madison, 8th Avenue, and major perimeter routes such as South Street and 12th Avenue. These are high-capacity facilities carrying major commercial traffic and transit. `[pause]`
> 
> In contrast, unsignalized intersection crashes are dispersed widely across the secondary grid and local residential cross-streets, with pronounced clusters around commercial loading zones in Midtown and northern interchange ramps in Harlem. `[pause]`
> 
> Again, the visual dominance of unsignalized points simply reflects the fact that unsignalized junctions far outnumber signalized junctions in the city grid. It reinforces why crash densities must be interpreted alongside facility function." `[advance slide]`

---

## Slide 5: When Crashes Occur (Temporal Trends)
**Visual:** Diurnal crash curve (hour of day) and weekly crash breakdown for both control types.  
**Target Duration:** 60 seconds `[Elapsed: 3:45 – 4:45]`

> "Next, we investigated *when* these collisions take place. 
> 
> Looking at the diurnal distribution on the left, both signalized and unsignalized intersections display remarkably synchronized profiles. `[pause]`
> 
> Collisions remain relatively low in the early morning hours, begin rising sharply during the morning commuter rush between 8 and 10 AM, and plateau at their peak levels through the afternoon from 1 PM to 6 PM. This coincides directly with peak business activity, delivery logistics, and pedestrian foot traffic. `[pause]`
> 
> When we tested day-of-week distributions, unsignalized counts showed a slight dip on Sundays, while signalized corridors maintained steady volumes. 
> 
> Statistically, a chi-square test of independence yielded a p-value of 0.169 across time-of-day and 0.619 across days of the week. This confirms that temporal variations are driven by city-wide ambient activity patterns rather than the presence or absence of traffic signals." `[advance slide]`

---

## Slide 6: Contributing Factors
**Visual:** Comparison bar chart of NYPD contributing factors; highlighted chi-square statistic ($\chi^2 = 27.22, p = 0.0024$).  
**Target Duration:** 65 seconds `[Elapsed: 4:45 – 5:50]`

> "Where the two intersection types diverge sharply is in their *behavioral contributing factors*. `[pause]`
> 
> Our chi-square test across contributing factors produced a statistic of 27.22 with a p-value of 0.0024, confirming a statistically significant difference at the 99% confidence level. `[pause]`
> 
> Distracted driving is the single leading specified factor at both types, accounting for roughly 27% of all attributed crashes. 
> 
> However, look closely at **failure to yield right-of-way**: `[point to slide]`
> Signalized intersections recorded a 3.6% failure-to-yield rate, compared to 2.4% at unsignalized junctions — a relative increase of fifty percent. 
> 
> Why does this happen? At signalized junctions, drivers turning left on a permissive green or turning right on red frequently misjudge clearance intervals against oncoming traffic or crossing pedestrians. 
> 
> Meanwhile, unsignalized intersections suffer heavily from sight-distance limitations and aggressive gap acceptance during lane-changing maneuvers." `[advance slide]`

---

## Slide 7: Severity: Signalized Crashes Are More Often Injurious
**Visual:** Severity breakdown (Injury vs. Property Damage Only), $\chi^2 = 32.09, p < 0.0001$, 35.12% vs. 27.81%.  
**Target Duration:** 75 seconds `[Elapsed: 5:50 – 7:05]`

> "Now, turning to what is perhaps the most critical finding of this research: **crash severity outcomes**. `[pause]`
> 
> Fatal crashes represent under 0.6% of the data at both categories — a proportion too small to display clearly on the chart, but reflecting strict urban speed enforcement. 
> 
> However, when we look at **injuries**:
> - At unsignalized intersections, the injury rate was **27.81%**.
> - At signalized intersections, the injury rate reached **35.12%**. `[pause]`
> 
> That is a 7.3 percentage-point increase in the probability of an injury when a crash occurs at a signalized intersection. A chi-square test of independence confirms this difference is overwhelmingly significant, with a chi-square value of 32.09 and a p-value less than 0.0001. `[pause]`
> 
> Now, as engineers, we must ask: *Why would signalized intersections exhibit a higher injury proportion?* `[pause]`
> 
> The evidence points to three physical and operational drivers:
> 1. *Operating Speeds:* Drivers approaching a green signal often maintain or accelerate their travel speed to clear the intersection, whereas drivers approaching an unsignalized junction are forced to decelerate to scan for traffic.
> 2. *Crossing Geometries:* Signalized intersections span wider, multi-lane arterials, significantly extending pedestrian clearance distances.
> 3. *Pedestrian Density:* High-volume corridors attract greater pedestrian exposure, converting vehicle-pedestrian impacts directly into recorded bodily injuries." `[advance slide]`

---

## Slide 8: Micro-Level Collision Diagrams
**Visual:** 4-leg schematic collision diagrams for 299 South St (Signalized, 11 crashes) and 600 E 125th St (Unsignalized, 36 crashes).  
**Target Duration:** 65 seconds `[Elapsed: 7:05 – 8:10]`

> "To understand the localized conflict mechanics, we mapped collision diagrams for the top crash locations in our database. `[glance at slide]`
> 
> On the left is the signalized intersection at **299 South Street**, which recorded 11 crashes. 
> The schematic reveals that conflict points are heavily concentrated on straight-through and left-turning maneuvers, dominated by driver distraction and failing to clear queue spillbacks.
> 
> On the right is the unsignalized intersection at **600 East 125th Street**, which recorded 36 crashes. 
> Here, the conflict pattern is fundamentally different: sideswipes, sudden merges, and rear-end collisions predominate. Because this intersection sits adjacent to major commercial loading bays and transit ramps, frequent curb friction and double-parked vehicles force drivers into blind lane changes. `[pause]`
> 
> It is important to note that these diagrams represent schematic movement classifications based on police report fields, as continuous micro-trajectory vehicle tracking is not captured in standard crash records." `[advance slide]`

---

## Slide 9: Data-Driven Safety Improvements
**Visual:** Engineering recommendations split into Signalized (LPI, Protected Lefts, Red-Light Cameras) and Unsignalized (Daylighting, Curb Extensions, Warrant Studies).  
**Target Duration:** 60 seconds `[Elapsed: 8:10 – 9:10]`

> "Based on these empirical findings, we propose a targeted suite of civil engineering improvements. `[pause]`
> 
> For **Signalized Intersections**, where injury rates and turning conflicts are elevated:
> - *Leading Pedestrian Intervals (LPIs):* Providing a 3 to 7 second head start for pedestrians before vehicle green phases eliminates turning-vehicle conflicts.
> - *Protected Left-Turn Phasing:* Replacing permissive green ball left turns with dedicated green arrows along multi-lane arterials to eliminate gap-misjudgment crashes.
> - *Automated Enforcement:* Deploying red-light cameras at high-speed approaches to suppress aggressive amber-running. `[pause]`
> 
> For **Unsignalized Intersections**, where sideswipes, visual obstruction, and pedestrian crossing vulnerability dominate:
> - *Intersection Daylighting:* Enforcing mandatory 6 to 9 meter parking bans from corners using physical curb extensions or flex-posts, restoring critical sight triangles.
> - *Curb Extensions and Bulb-outs:* Visually narrowing the travel lane, physically slowing turning speeds, and reducing pedestrian crossing distance.
> - And for high-crash hot spots like 125th Street, conducting formal **MUTCD Signal Warrant Studies** to determine whether conversion to an all-way stop or a full actuated traffic signal is warranted." `[advance slide]`

---

## Slide 10: Conclusions and Limitations
**Visual:** Summary of key findings, academic limitations, and closing takeaway quote.  
**Target Duration:** 50 seconds `[Elapsed: 9:10 – 10:00]`

> "To conclude, this research delivers three key findings: `[glance at jury]`
> 
> 1. Traffic control types produce distinct crash signatures: signalized intersections suffer disproportionately from high-severity turning and failure-to-yield conflicts, while unsignalized intersections generate higher frequencies of mid-day merge and sideswipe incidents.
> 2. The crash severity contrast is statistically decisive: signalized crashes produce an injury rate of 35.12% versus 27.81% at unsignalized locations ($\chi^2 = 32.09, p < 0.0001$).
> 3. Targeted engineering solutions — specifically LPIs and intersection daylighting — directly counteract these localized conflict points. `[pause]`
> 
> Finally, we must acknowledge the limitations of this study: the absence of traffic volume exposure data, reliance on police-reported incidents, and the geometric assumptions of our 30-meter buffer. 
> 
> Above all, this study demonstrates that **raw crash counts must never be confused with safety metrics**. 
> 
> Thank you for your time, and I am now ready to answer any questions." `[end of presentation | Elapsed: ~9:55]`

---

### Potential Committee Q&A Preparation

**Q1: Why did signalized intersections have a higher percentage of injury crashes than unsignalized ones?**
> *"Thank you for the question, Professor. There are three main reasons: First, operating speed. Approaching a green signal, drivers often maintain or even increase speed to clear the junction, leading to higher impact energy ($E_k = \frac{1}{2}mv^2$). At unsignalized stops, drivers naturally decelerate. Second, arterial geometry: signalized intersections in Manhattan typically cross wider 4-to-6 lane avenues with longer pedestrian exposure. Third, pedestrian volumes are significantly higher on signalized avenues, meaning vehicle conflicts are far more likely to involve vulnerable road users."*

**Q2: How did you distinguish intersection crashes from mid-block crashes?**
> *"We used a 30-meter metric buffer around intersection centroid coordinates projected into UTM Zone 18N (EPSG:32618). Any crash occurring within that 30-meter radius was classified as intersection-related, while crashes outside this radius were categorized as mid-block and excluded. 30 meters aligns with standard AASHTO and FHWA intersection functional area guidelines for urban street grids."*

**Q3: Can we conclude that unsignalized intersections are safer because they have lower injury percentages?**
> *"No, sir. That would be an ecological fallacy because we do not have traffic exposure data (Annual Average Daily Traffic or pedestrian crossing counts). A signalized intersection might process 40,000 vehicles a day while an unsignalized side-street processes only 2,000. Without volume denominators to calculate crash rates per million entering vehicles, we can only describe crash patterns, not absolute risk."*
