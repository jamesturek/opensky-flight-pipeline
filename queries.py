# Analysis queries against the OpenSky flights database

import sqlite3
import pandas as pd

con = sqlite3.connect("flights.db")

# 1. Top 10 countries by flight count
print("--- Top 10 Countries by Flight Count ---")
print(pd.read_sql("""
    SELECT origin_country, COUNT(*) as flights
    FROM flights
    GROUP BY origin_country
    ORDER BY flights DESC
    LIMIT 10
""", con))

# 2. Airborne vs on the ground
print("\n--- Airborne vs On Ground ---")
print(pd.read_sql("""
    SELECT 
        CASE WHEN on_ground = 1 THEN 'On Ground' ELSE 'Airborne' END as status,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct
    FROM flights
    GROUP BY on_ground
""", con))

# 3. Average speed and altitude by country (top 10 busiest)
print("\n--- Avg Speed & Altitude by Country (Top 10) ---")
print(pd.read_sql("""
    SELECT origin_country,
           COUNT(*) as flights,
           ROUND(AVG(velocity), 1) as avg_speed_ms,
           ROUND(AVG(baro_altitude), 0) as avg_altitude_m
    FROM flights
    WHERE on_ground = 0
    AND velocity IS NOT NULL
    AND baro_altitude IS NOT NULL
    GROUP BY origin_country
    ORDER BY flights DESC
    LIMIT 10
""", con))

# 4. Fastest flights
print("\n--- Top 10 Fastest Flights ---")
print(pd.read_sql("""
    SELECT callsign, origin_country, 
           ROUND(velocity, 1) as speed_ms,
           ROUND(baro_altitude, 0) as altitude_m
    FROM flights
    WHERE on_ground = 0
    AND velocity IS NOT NULL
    ORDER BY velocity DESC
    LIMIT 10
""", con))

# 5. Highest flying flights
print("\n--- Top 10 Highest Flying Flights ---")
print(pd.read_sql("""
    SELECT callsign, origin_country,
           ROUND(baro_altitude, 0) as altitude_m
    FROM flights
    WHERE on_ground = 0
    AND baro_altitude IS NOT NULL
    ORDER BY baro_altitude DESC
    LIMIT 10
""", con))

con.close()