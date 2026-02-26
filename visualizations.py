# Flight data visualizations

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap

# Load data - get most recent fetch only
con = sqlite3.connect("flights.db")
df = pd.read_sql("""
    SELECT * FROM flights 
    WHERE fetched_at = (SELECT MAX(fetched_at) FROM flights)
""", con)

df_all = pd.read_sql("SELECT * FROM flights", con)
con.close()

print(f"Latest snapshot: {len(df)} flights")

plt.style.use("default")

# --- Plot 1: Live flight map ---
fig, ax = plt.subplots(figsize=(16, 9))
ax.set_facecolor("#e8f4f8")
fig.patch.set_facecolor("#e8f4f8")

airborne = df[df["on_ground"] == False]
ground = df[df["on_ground"] == True]

scatter = ax.scatter(airborne["lon"], airborne["lat"],
                     c=airborne["velocity"], cmap="turbo",
                     s=3, alpha=0.8, vmin=0, vmax=300)
ax.scatter(ground["lon"], ground["lat"],
           c="#aaaaaa", s=1, alpha=0.5)

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label("Speed (m/s)", fontsize=11)
ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_title("Live Global Flight Positions", fontsize=18, fontweight="bold", pad=15)
ax.set_xlabel("Longitude", fontsize=11)
ax.set_ylabel("Latitude", fontsize=11)
ax.grid(True, alpha=0.3, color="#cccccc")

plt.tight_layout()
plt.savefig("outputs/plot1_flight_map.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved plot1_flight_map.png")

# --- Plot 2: Bar chart top countries ---
top_countries = df_all.groupby("origin_country").size().reset_index(name="flights")
top_countries = top_countries.sort_values("flights", ascending=False).head(15)

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor("#f9f9f9")
ax.set_facecolor("#f9f9f9")

colors = plt.cm.turbo([x/15 for x in range(15)])
bars = ax.barh(top_countries["origin_country"], top_countries["flights"], color=colors)
ax.invert_yaxis()

# Add value labels
for bar, val in zip(bars, top_countries["flights"]):
    ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height()/2,
            str(val), va="center", fontsize=9, color="#333333")

ax.set_title("Top 15 Countries by Flight Count", fontsize=16, fontweight="bold", pad=15)
ax.set_xlabel("Number of Flights", fontsize=11)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(axis="x", alpha=0.3)

plt.tight_layout()
plt.savefig("outputs/plot2_top_countries.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved plot2_top_countries.png")

# --- Plot 3: Folium heatmap ---
airborne_positions = df[df["on_ground"] == False][["lat", "lon", "velocity"]].dropna()
heat_data = airborne_positions[["lat", "lon"]].values.tolist()

m = folium.Map(location=[30, 0], zoom_start=2,
               tiles="OpenStreetMap")
HeatMap(heat_data, radius=6, blur=4, min_opacity=0.4,
        gradient={0.2: "blue", 0.4: "cyan", 0.6: "lime", 0.8: "yellow", 1.0: "red"}).add_to(m)

m.save("outputs/plot3_heatmap.html")
print("Saved plot3_heatmap.html")

print("\nAll visualizations complete!")