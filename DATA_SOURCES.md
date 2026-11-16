# Data Sources – Project 7

Detailed documentation of every data source used in this project.

---

## 1. NYC Motor Vehicle Collisions – Crashes

| Field | Value |
|-------|-------|
| **Name** | Motor Vehicle Collisions – Crashes |
| **Provider** | NYC Open Data (NYPD) |
| **URL** | https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95 |
| **Format** | CSV |
| **Local file** | `data/raw/nyc_crashes.csv` |
| **Coverage** | All NYPD-reported motor vehicle collisions in NYC (July 2012 – present) |
| **Study period** | January 2023 – December 2024 |
| **Geographic filter** | Manhattan borough |
| **License** | NYC Open Data Terms of Use |
| **Download date** | November 2026 |

### Variables Used

| Column | Description |
|--------|-------------|
| `CRASH DATE` | Date of the crash (MM/DD/YYYY) |
| `CRASH TIME` | Time of the crash (HH:MM) |
| `BOROUGH` | NYC borough name |
| `ZIP CODE` | Zip code of crash location |
| `LATITUDE` | WGS 84 latitude |
| `LONGITUDE` | WGS 84 longitude |
| `ON STREET NAME` | Street where the crash occurred |
| `CROSS STREET NAME` | Cross street (indicates an intersection crash) |
| `NUMBER OF PERSONS INJURED` | Total persons injured |
| `NUMBER OF PERSONS KILLED` | Total persons killed |
| `NUMBER OF PEDESTRIANS INJURED` | Pedestrians injured |
| `NUMBER OF PEDESTRIANS KILLED` | Pedestrians killed |
| `NUMBER OF CYCLIST INJURED` | Cyclists injured |
| `NUMBER OF CYCLIST KILLED` | Cyclists killed |
| `NUMBER OF MOTORIST INJURED` | Motorists injured |
| `NUMBER OF MOTORIST KILLED` | Motorists killed |
| `CONTRIBUTING FACTOR VEHICLE 1` | Primary contributing factor |
| `CONTRIBUTING FACTOR VEHICLE 2`–`5` | Additional contributing factors |
| `COLLISION_ID` | Unique crash identifier (links to Vehicles table) |
| `VEHICLE TYPE CODE 1`–`5` | Vehicle types involved |

---

## 2. NYC Motor Vehicle Collisions – Vehicles

| Field | Value |
|-------|-------|
| **Name** | Motor Vehicle Collisions – Vehicles |
| **Provider** | NYC Open Data (NYPD) |
| **URL** | https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Vehicles/bm4k-52h4 |
| **Format** | CSV |
| **Local file** | `data/raw/nyc_vehicles.csv` |
| **Coverage** | Vehicle-level details for each crash |
| **License** | NYC Open Data Terms of Use |
| **Download date** | November 2026 |

### Variables Used

| Column | Description |
|--------|-------------|
| `UNIQUE_ID` | Unique vehicle record ID |
| `COLLISION_ID` | Links to the Crashes table |
| `VEHICLE_TYPE` | Type of vehicle (sedan, SUV, taxi, bus, bicycle, etc.) |
| `VEHICLE_MAKE` | Vehicle manufacturer |
| `TRAVEL_DIRECTION` | Direction of travel before crash |
| `POINT_OF_IMPACT` | Initial point of impact on the vehicle |
| `PRE_CRASH` | Vehicle action before crash |
| `CONTRIBUTING_FACTOR_1` | Contributing factor for this vehicle |
| `CONTRIBUTING_FACTOR_2` | Secondary contributing factor |
| `DRIVER_SEX` | Driver sex |

---

## 3. OpenStreetMap – Traffic Signal Nodes

| Field | Value |
|-------|-------|
| **Name** | OpenStreetMap traffic signal nodes |
| **Provider** | OpenStreetMap contributors |
| **URL** | https://www.openstreetmap.org/ |
| **Access method** | `osmnx.features_from_place()` with tag `highway=traffic_signals` |
| **Place query** | "New York City, New York, USA" |
| **Format** | GeoDataFrame (cached as GeoPackage) |
| **Local cache** | `data/processed/nyc_traffic_signals.gpkg` |
| **CRS** | EPSG:4326 (WGS 84) |
| **License** | Open Database License (ODbL) |
| **Attribution** | © OpenStreetMap contributors |
| **Retrieval date** | First run of `data_collection.py` |

### Usage

Traffic signal node point geometries are buffered by 30 metres (in UTM zone 18N / EPSG:32618) and used to spatially classify each intersection crash as signalized or unsignalized.

---

## Data Limitations

- **Crash underreporting**: Minor crashes may not be reported to NYPD.
- **Geocoding errors**: Some crash coordinates may be inaccurate.
- **OSM completeness**: Not every traffic signal may be mapped in OSM.
- **Temporal mismatch**: OSM data reflects the current state and may not perfectly align with signal installations during 2023-2024.
- **No traffic volume data**: Crash rates per vehicle or per intersection approach are not computed.
