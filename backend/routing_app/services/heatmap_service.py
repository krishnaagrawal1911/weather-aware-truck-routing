import math
from datetime import datetime, timedelta
from typing import List, Dict, Any
from routing_app.services.weather_service import fetch_weather_for_coords
from routing_app.services.risk_engine import evaluate_checkpoint_risk

def generate_corridor_grid(routes: List[Dict[str, Any]], grid_steps: int = 5) -> List[Dict[str, float]]:
    """
    Computes bounding box of all route coordinates and generates a corridor grid.
    """
    all_lats = []
    all_lons = []
    
    for r in routes:
        for lon, lat in r.get("coordinates", []):
            all_lats.append(lat)
            all_lons.append(lon)
            
    if not all_lats or not all_lons:
        return []

    min_lat, max_lat = min(all_lats), max(all_lats)
    min_lon, max_lon = min(all_lons), max(all_lons)
    
    # Add corridor padding
    lat_pad = max((max_lat - min_lat) * 0.15, 0.4)
    lon_pad = max((max_lon - min_lon) * 0.15, 0.4)
    
    min_lat -= lat_pad
    max_lat += lat_pad
    min_lon -= lon_pad
    max_lon += lon_pad

    grid_pts = []
    lat_step = (max_lat - min_lat) / (grid_steps - 1) if grid_steps > 1 else 1.0
    lon_step = (max_lon - min_lon) / (grid_steps - 1) if grid_steps > 1 else 1.0

    for i in range(grid_steps):
        lat = min_lat + i * lat_step
        for j in range(grid_steps):
            lon = min_lon + j * lon_step
            grid_pts.append({"lat": round(lat, 4), "lon": round(lon, 4)})

    return grid_pts


def build_corridor_heatmap_timeline(routes: List[Dict[str, Any]], departure_time: datetime, load_lbs: float) -> Dict[str, Any]:
    """
    Constructs a 0–48 hour timeline of spatial weather risk points along the trip corridor.
    """
    grid_coords = generate_corridor_grid(routes, grid_steps=5) # 25 grid points
    if not grid_coords:
        return {"hours": [], "points": []}

    weather_responses = fetch_weather_for_coords(grid_coords)
    has_live = len(weather_responses) == len(grid_coords)

    # We want hours 0 to 48
    num_hours = 49  # 0 to 48 inclusive
    hours_labels = [(departure_time + timedelta(hours=h)).strftime("%b %d, %H:00") for h in range(num_hours)]
    
    timeline_frames = []
    
    for h in range(num_hours):
        frame_pts = []
        frame_dt = departure_time + timedelta(hours=h)
        
        for idx, pt in enumerate(grid_coords):
            wind = 15.0
            rain = 0.0
            snow = 0.0
            temp = 60.0
            
            if has_live and idx < len(weather_responses):
                w_item = weather_responses[idx]
                hourly = w_item.get("hourly", {})
                times = hourly.get("time", [])
                
                # Match or use offset h
                h_idx = min(h, len(times) - 1) if times else 0
                wind = float(hourly.get("wind_speed_10m", [15.0])[h_idx] or 15.0)
                rain = float(hourly.get("rain", [0.0])[h_idx] or 0.0)
                snow = float(hourly.get("snowfall", [0.0])[h_idx] or 0.0)
                precip = float(hourly.get("precipitation", [0.0])[h_idx] or 0.0)
                temp = float(hourly.get("temperature_2m", [60.0])[h_idx] or 60.0)
                
                if rain == 0 and snow == 0 and precip > 0:
                    if temp <= 32:
                        snow = precip
                    else:
                        rain = precip
            else:
                # Deterministic spatial simulation
                seed = math.sin(pt["lat"] * 3.5 + pt["lon"] * 2.1 + h * 0.15)
                wind = 18.0 + 22.0 * abs(seed)
                if seed > 0.35:
                    rain = (seed - 0.35) * 0.9
                if seed < -0.4:
                    snow = abs(seed + 0.4) * 1.5

            risk_eval = evaluate_checkpoint_risk(wind, rain, snow, load_lbs)
            
            frame_pts.append({
                "lat": pt["lat"],
                "lon": pt["lon"],
                "wind_mph": round(wind, 1),
                "rain_in": round(rain, 2),
                "snow_in": round(snow, 2),
                "risk_score": risk_eval["overall_risk_score"],
                "risk_level": risk_eval["overall_risk"],
                "color": risk_eval["color"],
            })
            
        timeline_frames.append({
            "hour_offset": h,
            "display_time": hours_labels[h],
            "iso_time": (departure_time + timedelta(hours=h)).isoformat(),
            "points": frame_pts,
        })

    return {
        "num_frames": len(timeline_frames),
        "frames": timeline_frames,
    }
