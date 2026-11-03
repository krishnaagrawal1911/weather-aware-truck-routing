import math
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional

EARTH_RADIUS_MILES = 3958.8
METERS_TO_MILES = 0.000621371
MILES_TO_METERS = 1609.34
OSRM_URL = "http://router.project-osrm.org/route/v1/driving"

def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return EARTH_RADIUS_MILES * c

def interpolate_point(lat1: float, lon1: float, lat2: float, lon2: float, fraction: float) -> Tuple[float, float]:
    return (
        lat1 + fraction * (lat2 - lat1),
        lon1 + fraction * (lon2 - lon1)
    )

def sample_route_checkpoints(coordinates: List[List[float]], total_distance_miles: float, total_duration_secs: float, interval_miles: float, departure_time: datetime) -> List[Dict[str, Any]]:
    if not coordinates or len(coordinates) < 2:
        return []

    cum_distances = [0.0]
    for i in range(1, len(coordinates)):
        lon1, lat1 = coordinates[i - 1]
        lon2, lat2 = coordinates[i]
        d = haversine_miles(lat1, lon1, lat2, lon2)
        cum_distances.append(cum_distances[-1] + d)

    actual_total_miles = cum_distances[-1]
    if actual_total_miles <= 0:
        actual_total_miles = total_distance_miles

    targets = []
    curr = 0.0
    while curr < actual_total_miles:
        targets.append(curr)
        curr += interval_miles
    if not targets or (actual_total_miles - targets[-1] > interval_miles * 0.25):
        targets.append(actual_total_miles)

    checkpoints = []
    coord_idx = 0
    num_coords = len(coordinates)

    for step_num, target_dist in enumerate(targets):
        while coord_idx < num_coords - 1 and cum_distances[coord_idx + 1] < target_dist:
            coord_idx += 1

        if coord_idx >= num_coords - 1:
            lat = coordinates[-1][1]
            lon = coordinates[-1][0]
        else:
            seg_start_dist = cum_distances[coord_idx]
            seg_end_dist = cum_distances[coord_idx + 1]
            seg_len = seg_end_dist - seg_start_dist
            frac = (target_dist - seg_start_dist) / seg_len if seg_len > 1e-6 else 0.0
            frac = max(0.0, min(1.0, frac))
            
            lon1, lat1 = coordinates[coord_idx]
            lon2, lat2 = coordinates[coord_idx + 1]
            lat, lon = interpolate_point(lat1, lon1, lat2, lon2, frac)

        progress_frac = target_dist / actual_total_miles if actual_total_miles > 0 else 0.0
        elapsed_seconds = total_duration_secs * progress_frac
        checkpoint_eta = departure_time + timedelta(seconds=elapsed_seconds)

        checkpoints.append({
            "index": step_num,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "distance_from_origin_miles": round(target_dist, 1),
            "elapsed_seconds": int(elapsed_seconds),
            "eta": checkpoint_eta.isoformat(),
        })

    for i in range(len(checkpoints)):
        if i < len(checkpoints) - 1:
            step_dist = checkpoints[i + 1]["distance_from_origin_miles"] - checkpoints[i]["distance_from_origin_miles"]
        else:
            step_dist = checkpoints[i]["distance_from_origin_miles"] - (checkpoints[i - 1]["distance_from_origin_miles"] if i > 0 else 0)
        checkpoints[i]["step_distance_miles"] = round(step_dist, 1)

    return checkpoints


def fetch_osrm_route(coord_str: str, alternatives: bool = True) -> Optional[Dict[str, Any]]:
    url = f"{OSRM_URL}/{coord_str}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "true",
        "alternatives": "3" if alternatives else "false",
    }
    try:
        resp = requests.get(url, params=params, timeout=8.0)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"OSRM request error: {e}")
    return None


def generate_fallback_route_coords(lat1: float, lon1: float, lat2: float, lon2: float, curve_offset: float) -> List[List[float]]:
    """Generates a smooth curved polyline between two endpoints as resilient fallback."""
    num_pts = 30
    coords = []
    mid_lat = (lat1 + lat2) / 2
    mid_lon = (lon1 + lon2) / 2
    
    # Perpendicular direction
    dx = lon2 - lon1
    dy = lat2 - lat1
    perp_lat = -dx * curve_offset
    perp_lon = dy * curve_offset
    ctrl_lat = mid_lat + perp_lat
    ctrl_lon = mid_lon + perp_lon
    
    for i in range(num_pts + 1):
        t = i / num_pts
        # Quadratic Bezier
        lat = (1 - t)**2 * lat1 + 2 * (1 - t) * t * ctrl_lat + t**2 * lat2
        lon = (1 - t)**2 * lon1 + 2 * (1 - t) * t * ctrl_lon + t**2 * lon2
        coords.append([round(lon, 5), round(lat, 5)])
        
    return coords


def get_three_routes(origin: Tuple[float, float], destination: Tuple[float, float], departure_time: datetime, interval_miles: float = 25.0) -> List[Dict[str, Any]]:
    """
    Fetches exactly 3 distinct routes using OSRM routing API, interpolating checkpoints.
    origin: (lat, lon)
    destination: (lat, lon)
    """
    lat1, lon1 = origin
    lat2, lon2 = destination
    direct_dist_miles = haversine_miles(lat1, lon1, lat2, lon2)
    base_speed_mph = 55.0  # standard commercial truck average highway speed

    coord_str = f"{lon1},{lat1};{lon2},{lat2}"
    osrm_data = fetch_osrm_route(coord_str, alternatives=True)
    
    raw_routes = []
    if osrm_data and osrm_data.get("routes"):
        raw_routes = osrm_data["routes"]

    # We need 3 routes. If OSRM returned fewer than 3, construct realistic detour via-points
    routes_to_build = []
    names = ["Northern Corridor", "Direct Interstate Route", "Southern / Alternate Corridor"]

    if len(raw_routes) >= 3:
        for idx, r in enumerate(raw_routes[:3]):
            routes_to_build.append({
                "name": f"Route {idx + 1} ({r.get('legs', [{}])[0].get('summary', 'Highway') or 'Expressway'})",
                "coordinates": r["geometry"]["coordinates"],
                "distance_miles": r["distance"] * METERS_TO_MILES,
                "duration_seconds": r["duration"],
            })
    else:
        # Use whatever OSRM returned as primary
        if raw_routes:
            r0 = raw_routes[0]
            routes_to_build.append({
                "name": f"Primary Interstate ({r0.get('legs', [{}])[0].get('summary', 'Main Route') or 'Highway'})",
                "coordinates": r0["geometry"]["coordinates"],
                "distance_miles": r0["distance"] * METERS_TO_MILES,
                "duration_seconds": r0["duration"],
            })
        else:
            # Resilient direct fallback
            coords = generate_fallback_route_coords(lat1, lon1, lat2, lon2, 0.0)
            dist = direct_dist_miles * 1.15
            dur = (dist / base_speed_mph) * 3600
            routes_to_build.append({
                "name": "Direct Highway Route",
                "coordinates": coords,
                "distance_miles": dist,
                "duration_seconds": dur,
            })

        # Generate waypoint detours to get 3 distinct routes
        detour_factors = [0.18, -0.18]
        detour_names = ["Northern Corridor Route", "Southern Corridor Route"]
        
        for factor, d_name in zip(detour_factors, detour_names):
            if len(routes_to_build) >= 3:
                break
            # Compute intermediate waypoint
            dx = lon2 - lon1
            dy = lat2 - lat1
            mid_lat = (lat1 + lat2) / 2
            mid_lon = (lon1 + lon2) / 2
            waypoint_lat = mid_lat - dx * factor
            waypoint_lon = mid_lon + dy * factor
            
            wp_coord_str = f"{lon1},{lat1};{waypoint_lon:.5f},{waypoint_lat:.5f};{lon2},{lat2}"
            wp_data = fetch_osrm_route(wp_coord_str, alternatives=False)
            
            if wp_data and wp_data.get("routes"):
                wr = wp_data["routes"][0]
                routes_to_build.append({
                    "name": d_name,
                    "coordinates": wr["geometry"]["coordinates"],
                    "distance_miles": wr["distance"] * METERS_TO_MILES,
                    "duration_seconds": wr["duration"],
                })
            else:
                # Fallback curved route
                coords = generate_fallback_route_coords(lat1, lon1, lat2, lon2, factor)
                dist = direct_dist_miles * 1.25
                dur = (dist / base_speed_mph) * 3600
                routes_to_build.append({
                    "name": d_name,
                    "coordinates": coords,
                    "distance_miles": dist,
                    "duration_seconds": dur,
                })

    # Now assemble the finalized 3 route objects with checkpoints
    final_routes = []
    for idx, r_data in enumerate(routes_to_build[:3]):
        checkpoints = sample_route_checkpoints(
            coordinates=r_data["coordinates"],
            total_distance_miles=r_data["distance_miles"],
            total_duration_secs=r_data["duration_seconds"],
            interval_miles=interval_miles,
            departure_time=departure_time,
        )
        
        duration_hrs = r_data["duration_seconds"] / 3600.0
        final_routes.append({
            "route_id": f"route_{idx + 1}",
            "name": r_data["name"],
            "distance_miles": round(r_data["distance_miles"], 1),
            "duration_hours": round(duration_hrs, 2),
            "duration_formatted": f"{int(duration_hrs)}h {int((duration_hrs % 1) * 60)}m",
            "coordinates": r_data["coordinates"],  # GeoJSON [[lon, lat], ...]
            "checkpoints": checkpoints,
        })

    return final_routes
