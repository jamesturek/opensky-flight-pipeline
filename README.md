# OpenSky Flight Tracking ETL Pipeline

An end-to-end ETL pipeline in Python that fetches live global flight data from the OpenSky Network REST API, transforms it, and loads it into a SQLite database for analysis and visualisation.

---

## Live Demo

![Flight Map](outputs/plot1_flight_map.png)

![Top Countries](outputs/plot2_top_countries.png)

---

## Overview

This project ingests real-time AIS flight state data from the [OpenSky Network API](https://opensky-network.org/), cleans and structures it using pandas, and loads it into a SQLite database. The pipeline can be run repeatedly to build up a time series of global flight activity.

---

## Pipeline Architecture

```
OpenSky Network REST API
        ↓
pipeline.py   — Fetch, clean, and load live flight data
        ↓
flights.db    — SQLite database
        ↓
queries.py    — SQL analysis
        ↓
visualizations.py — Static maps and interactive heatmap
```

Run the full pipeline with:

```bash
python pipeline.py
```

---

## Data Source

- **Provider:** OpenSky Network (https://opensky-network.org/)
- **Endpoint:** `/api/states/all` — returns all current flight states
- **Update frequency:** ~10 seconds
- **Coverage:** Global
- **No API key required** for anonymous access

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Pipeline scripting |
| `requests` | REST API calls |
| `pandas` | Data transformation |
| `sqlalchemy` | Database connection |
| `matplotlib` | Static visualisations |
| `folium` | Interactive heatmap |
| SQLite | Lightweight portable database |

---

## Database Schema

**Table: `flights`**

| Column | Type | Description |
|--------|------|-------------|
| `icao24` | TEXT | Unique aircraft identifier |
| `callsign` | TEXT | Flight callsign |
| `origin_country` | TEXT | Country of registration |
| `lon` | REAL | Longitude (WGS84) |
| `lat` | REAL | Latitude (WGS84) |
| `baro_altitude` | REAL | Barometric altitude (metres) |
| `on_ground` | BOOLEAN | Whether aircraft is on ground |
| `velocity` | REAL | Speed (m/s) |
| `true_track` | REAL | Heading (degrees) |
| `fetched_at` | TEXT | UTC timestamp of data fetch |

---

## Example Queries

**Top countries by flight count:**
```sql
SELECT origin_country, COUNT(*) as flights
FROM flights
GROUP BY origin_country
ORDER BY flights DESC
LIMIT 10;
```

**Airborne vs on ground:**
```sql
SELECT 
    CASE WHEN on_ground = 1 THEN 'On Ground' ELSE 'Airborne' END as status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct
FROM flights
GROUP BY on_ground;
```

**Average speed and altitude by country:**
```sql
SELECT origin_country,
       ROUND(AVG(velocity), 1) as avg_speed_ms,
       ROUND(AVG(baro_altitude), 0) as avg_altitude_m
FROM flights
WHERE on_ground = 0
GROUP BY origin_country
ORDER BY avg_speed_ms DESC
LIMIT 10;
```

---

## Key Findings

- The **United States** accounts for the largest share of global flights at any given time, followed by the UK and Germany
- Approximately **90% of tracked aircraft** are airborne at any snapshot
- **UAE and Irish registered aircraft** fly at significantly higher average altitudes than European short-haul operators, reflecting their long-haul route networks
- Occasional extreme velocity outliers (>500 m/s) suggest military or data anomalies worth filtering in production

---

## Setup

1. Clone the repository
2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
```
3. Install dependencies:
```bash
pip install requests pandas sqlalchemy matplotlib seaborn folium
```
4. Run the pipeline:
```bash
python pipeline.py
```
5. Run analysis queries:
```bash
python queries.py
```
6. Generate visualisations:
```bash
python visualizations.py
```

---

## Project Structure

```
opensky-flight-pipeline/
├── pipeline.py          # ETL pipeline
├── queries.py           # SQL analysis
├── visualizations.py    # Charts and maps
├── outputs/
│   ├── plot1_flight_map.png
│   ├── plot2_top_countries.png
│   └── plot3_heatmap.html
├── flights.db           # SQLite database (generated)
└── README.md
```
