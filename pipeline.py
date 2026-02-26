# pipeline.py
# OpenSky Network flight tracking ETL pipeline

import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timezone

# --- EXTRACT ---
def extract_flights():
    print("Fetching live flight data from OpenSky Network...")
    url = "https://opensky-network.org/api/states/all"
    response = requests.get(url, timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"API request failed with status {response.status_code}")
    
    data = response.json()
    print(f"Retrieved {len(data['states'])} flights")
    return data['states']

# --- TRANSFORM ---
def transform_flights(raw_states):
    columns = [
        "icao24", "callsign", "origin_country", "time_position",
        "last_contact", "lon", "lat", "baro_altitude", "on_ground",
        "velocity", "true_track", "vertical_rate", "sensors",
        "geo_altitude", "squawk", "spi", "position_source"
    ]
    
    df = pd.DataFrame(raw_states, columns=columns)
    
    # Clean up
    df = df[[
        "icao24", "callsign", "origin_country", "lon", "lat",
        "baro_altitude", "on_ground", "velocity", "true_track"
    ]]
    df["callsign"] = df["callsign"].str.strip()
    df["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    
    # Drop rows with no position
    df = df.dropna(subset=["lon", "lat"])
    
    print(f"Clean rows after transform: {len(df)}")
    return df

# --- LOAD ---
def load_flights(df):
    engine = create_engine("sqlite:///flights.db")
    df.to_sql("flights", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into flights.db")

# --- RUN ---
if __name__ == "__main__":
    raw = extract_flights()
    df = transform_flights(raw)
    load_flights(df)
    print("\nPipeline complete!")
    print(df.head())
