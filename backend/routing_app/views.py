from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from routing_app.services.geocoding_service import geocode_address
from routing_app.services.routing_service import get_three_routes
from routing_app.services.weather_service import enrich_routes_with_weather_and_risk, parse_iso_datetime
from routing_app.services.recommendation_engine import rank_and_recommend_routes
from routing_app.services.heatmap_service import build_corridor_heatmap_timeline

class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "healthy", "service": "Weather-Aware Truck Routing API"})

class GeocodeView(APIView):
    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q or len(q) < 2:
            return Response([])
        results = geocode_address(q)
        return Response(results)

class RoutePlanView(APIView):
    def post(self, request):
        data = request.data or {}
        
        # 1. Parse Origin
        origin_data = data.get("origin")
        if isinstance(origin_data, str):
            geo = geocode_address(origin_data, limit=1)
            if not geo:
                return Response({"error": f"Could not geocode origin: '{origin_data}'"}, status=status.HTTP_400_BAD_REQUEST)
            origin_pt = (geo[0]["lat"], geo[0]["lon"])
            origin_name = geo[0]["display_name"]
        elif isinstance(origin_data, dict) and "lat" in origin_data and "lon" in origin_data:
            origin_pt = (float(origin_data["lat"]), float(origin_data["lon"]))
            origin_name = origin_data.get("name", f"{origin_pt[0]:.3f}, {origin_pt[1]:.3f}")
        else:
            return Response({"error": "Invalid origin. Provide lat/lon or search query."}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Parse Destination
        dest_data = data.get("destination")
        if isinstance(dest_data, str):
            geo = geocode_address(dest_data, limit=1)
            if not geo:
                return Response({"error": f"Could not geocode destination: '{dest_data}'"}, status=status.HTTP_400_BAD_REQUEST)
            dest_pt = (geo[0]["lat"], geo[0]["lon"])
            dest_name = geo[0]["display_name"]
        elif isinstance(dest_data, dict) and "lat" in dest_data and "lon" in dest_data:
            dest_pt = (float(dest_data["lat"]), float(dest_data["lon"]))
            dest_name = dest_data.get("name", f"{dest_pt[0]:.3f}, {dest_pt[1]:.3f}")
        else:
            return Response({"error": "Invalid destination. Provide lat/lon or search query."}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Departure Date/Time
        dep_str = data.get("departure_time")
        if dep_str:
            try:
                departure_time = parse_iso_datetime(dep_str)
            except Exception:
                departure_time = datetime.utcnow()
        else:
            departure_time = datetime.utcnow()

        # 4. Load Weight
        try:
            load_lbs = float(data.get("load_weight_lbs", 35000))
        except (ValueError, TypeError):
            load_lbs = 35000.0

        # 5. Checkpoint Interval (10, 25, 50 miles)
        try:
            interval_miles = float(data.get("sample_interval_miles", 25))
            if interval_miles not in [10.0, 25.0, 50.0]:
                interval_miles = 25.0
        except (ValueError, TypeError):
            interval_miles = 25.0

        # Step 1: Generate 3 route options
        routes = get_three_routes(origin_pt, dest_pt, departure_time, interval_miles)

        # Step 2: Sample weather and calculate risk
        routes_with_weather = enrich_routes_with_weather_and_risk(routes, load_lbs)

        # Step 3: Recommend best route
        ranked_routes = rank_and_recommend_routes(routes_with_weather)

        # Step 4: Build corridor heatmap timeline (0-48 hours)
        heatmap_timeline = build_corridor_heatmap_timeline(ranked_routes, departure_time, load_lbs)

        response_payload = {
            "origin": {
                "name": origin_name,
                "lat": origin_pt[0],
                "lon": origin_pt[1],
            },
            "destination": {
                "name": dest_name,
                "lat": dest_pt[0],
                "lon": dest_pt[1],
            },
            "departure_time": departure_time.isoformat(),
            "load_weight_lbs": load_lbs,
            "sample_interval_miles": interval_miles,
            "routes": ranked_routes,
            "heatmap_timeline": heatmap_timeline,
        }

        return Response(response_payload)
