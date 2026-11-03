import math
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from routing_app.services.risk_engine import evaluate_checkpoint_risk

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

def parse_iso_datetime(dt_str: str) -> datetime:
    clean = dt_str.replace("Z", "+00:00")
    if "+" in clean:
        clean = clean.split("+")[0]
    return datetime.fromisoformat(clean)

def find_closest_hour_index(time_list: List[str], target_dt: datetime) -> int:
    if not time_list:
        return 0
    target_str = target_dt.strftime("%Y-%m-%dT%H:00")
    try:
        return time_list.index(target_str)
    except ValueError:
        pass

    best_idx = 0
    min_diff = float("inf")
    for i, t_str in enumerate(time_list):
        try:
            slot_dt = datetime.fromisoformat(t_str)
            diff = abs((slot_dt - target_dt).total_seconds())
            if diff < min_diff:
                min_diff = diff
                best_idx = i
        except Exception:
            continue
    return best_idx


def fetch_weather_for_coords(coords: List[Dict[str, float]]) -> List[Dict[str, Any]]:
    if not coords:
        return []

    results = []
    chunk_size = 40
    for i in range(0, len(coords), chunk_size):
        chunk = coords[i:i + chunk_size]
        lats = ",".join(f"{c['lat']:.4f}" for c in chunk)
        lons = ",".join(f"{c['lon']:.4f}" for c in chunk)
        
        params = {
            "latitude": lats,
            "longitude": lons,
            "hourly": "temperature_2m,precipitation,rain,snowfall,wind_speed_10m,weather_code",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "UTC",
            "forecast_days": 3,
        }
        
        try:
            resp = requests.get(OPEN_METEO_URL, params=params, timeout=9.0)
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    results.extend(data)
                elif isinstance(data, dict):
                    results.append(data)
            else:
                print(f"Open-Meteo HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"Open-Meteo fetch error: {e}")

    return results


def fallback_weather_simulation(lat: float, lon: float, dt: datetime) -> Dict[str, Any]:
    """Generates realistic weather simulation if live external API is unreachable."""
    hour = dt.hour
    # Use spatial hash for consistent variation
    seed = math.sin(lat * 5.2 + lon * 3.7 + hour * 0.5)
    
    wind = 15.0 + 20.0 * abs(seed)  # 15 to 35 mph
    rain = 0.0
    snow = 0.0
    temp = 45.0 + 20.0 * math.cos(lat * 0.1)
    
    if seed > 0.4:
        rain = (seed - 0.4) * 0.8  # up to 0.48 in/hr
    if temp < 32.0 and seed > 0.3:
        snow = (seed - 0.3) * 1.5
        rain = 0.0
        
    return {
        "wind_speed_mph": round(wind, 1),
        "rain_in_hr": round(rain, 2),
        "snow_in_hr": round(snow, 2),
        "temperature_f": round(temp, 1),
        "weather_code": 3,
        "is_simulated": True,
    }


def enrich_routes_with_weather_and_risk(routes: List[Dict[str, Any]], load_lbs: float) -> List[Dict[str, Any]]:
    """
    Queries weather for every checkpoint across all routes at their respective ETAs,
    computes risk using risk_engine rules, and enriches checkpoint data.
    """
    # 1. Collect all checkpoints
    all_checkpoints = []
    for r in routes:
        all_checkpoints.extend(r.get("checkpoints", []))

    if not all_checkpoints:
        return routes

    # 2. Extract unique coords to avoid duplicate API calls
    coord_reqs = [{"lat": cp["lat"], "lon": cp["lon"]} for cp in all_checkpoints]
    weather_responses = fetch_weather_for_coords(coord_reqs)

    # 3. Match each checkpoint
    has_live_weather = len(weather_responses) == len(coord_reqs)

    for idx, cp in enumerate(all_checkpoints):
        eta_dt = parse_iso_datetime(cp["eta"])
        
        weather_item = None
        if has_live_weather:
            weather_item = weather_responses[idx]
        elif weather_responses:
            # Map by closest coordinate
            for wr in weather_responses:
                wlat = wr.get("latitude", 0)
                wlon = wr.get("longitude", 0)
                if abs(wlat - cp["lat"]) < 0.08 and abs(wlon - cp["lon"]) < 0.08:
                    weather_item = wr
                    break

        if weather_item and "hourly" in weather_item:
            hourly = weather_item["hourly"]
            times = hourly.get("time", [])
            h_idx = find_closest_hour_index(times, eta_dt)

            wind_mph = float(hourly.get("wind_speed_10m", [0])[h_idx] or 0.0)
            rain_in = float(hourly.get("rain", [0])[h_idx] or 0.0)
            snow_in = float(hourly.get("snowfall", [0])[h_idx] or 0.0)
            precip_in = float(hourly.get("precipitation", [0])[h_idx] or 0.0)
            temp_f = float(hourly.get("temperature_2m", [65])[h_idx] or 65.0)
            code = int(hourly.get("weather_code", [0])[h_idx] or 0)
            
            # If rain is 0 but precipitation > 0 and snow is 0, attribute to rain
            if rain_in == 0.0 and snow_in == 0.0 and precip_in > 0:
                if temp_f <= 32:
                    snow_in = precip_in
                else:
                    rain_in = precip_in
            
            weather_data = {
                "wind_speed_mph": round(wind_mph, 1),
                "rain_in_hr": round(rain_in, 2),
                "snow_in_hr": round(snow_in, 2),
                "temperature_f": round(temp_f, 1),
                "weather_code": code,
                "is_simulated": False,
            }
        else:
            weather_data = fallback_weather_simulation(cp["lat"], cp["lon"], eta_dt)

        # Calculate risk using risk_engine
        risk_data = evaluate_checkpoint_risk(
            wind_mph=weather_data["wind_speed_mph"],
            rain_in_hr=weather_data["rain_in_hr"],
            snow_in_hr=weather_data["snow_in_hr"],
            load_lbs=load_lbs,
        )

        cp["weather"] = weather_data
        cp["risk"] = risk_data

    return routes
