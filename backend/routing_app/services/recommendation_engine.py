from typing import List, Dict, Any
from routing_app.services.risk_engine import RiskLevel

def calculate_route_metrics(route: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aggregates distance traveled under each risk level and computes average risk score.
    """
    checkpoints = route.get("checkpoints", [])
    
    no_travel_miles = 0.0
    severe_miles = 0.0
    high_miles = 0.0
    moderate_miles = 0.0
    low_miles = 0.0
    
    total_dist = 0.0
    weighted_risk_sum = 0.0
    
    for cp in checkpoints:
        dist = float(cp.get("step_distance_miles", 0.0))
        risk_info = cp.get("risk", {})
        level = risk_info.get("overall_risk", RiskLevel.LOW.value)
        score = float(risk_info.get("overall_risk_score", 1.0))
        
        total_dist += dist
        weighted_risk_sum += score * dist
        
        if level == RiskLevel.NO_TRAVEL.value:
            no_travel_miles += dist
        elif level == RiskLevel.SEVERE.value:
            severe_miles += dist
        elif level == RiskLevel.HIGH.value:
            high_miles += dist
        elif level == RiskLevel.MODERATE.value:
            moderate_miles += dist
        else:
            low_miles += dist

    if total_dist > 0:
        avg_risk = round(weighted_risk_sum / total_dist, 2)
    elif checkpoints:
        scores = [cp.get("risk", {}).get("overall_risk_score", 1.0) for cp in checkpoints]
        avg_risk = round(sum(scores) / len(scores), 2)
    else:
        avg_risk = 1.0

    return {
        "no_travel_miles": round(no_travel_miles, 1),
        "severe_miles": round(severe_miles, 1),
        "high_miles": round(high_miles, 1),
        "moderate_miles": round(moderate_miles, 1),
        "low_miles": round(low_miles, 1),
        "average_risk_score": avg_risk,
    }


def rank_and_recommend_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks routes according to strict priority rules:
      1. Fewest Severe miles (No Travel miles heavily prioritized to avoid unsafe closure)
      2. Fewest High miles
      3. Lowest average risk
      4. Shortest travel times
    """
    if not routes:
        return []

    # First attach metrics to each route
    for route in routes:
        metrics = calculate_route_metrics(route)
        route["metrics"] = metrics

    # Sorting key tuple:
    # (no_travel_miles, severe_miles, high_miles, average_risk_score, duration_hours)
    sorted_routes = sorted(
        routes,
        key=lambda r: (
            r["metrics"]["no_travel_miles"],
            r["metrics"]["severe_miles"],
            r["metrics"]["high_miles"],
            r["metrics"]["average_risk_score"],
            r.get("duration_hours", 0.0),
        )
    )

    # Assign ranks and badges
    for rank_idx, route in enumerate(sorted_routes):
        route["rank"] = rank_idx + 1
        route["is_recommended"] = (rank_idx == 0)
        
        m = route["metrics"]
        reasons = []
        if route["is_recommended"]:
            if m["no_travel_miles"] == 0 and m["severe_miles"] == 0 and m["high_miles"] == 0:
                reasons.append("Zero High or Severe weather risk along the entire trip corridor")
            else:
                if m["no_travel_miles"] == 0:
                    reasons.append("Avoids mandatory No Travel shutdown zones")
                if m["severe_miles"] == 0:
                    reasons.append("Avoids all Severe risk miles")
                else:
                    reasons.append(f"Lowest Severe exposure ({m['severe_miles']} mi)")
                
                reasons.append(f"Lowest average hazard score ({m['average_risk_score']})")

            reasons.append(f"Estimated trip time: {route.get('duration_formatted', '')}")
            route["recommendation_summary"] = " • ".join(reasons)
        else:
            diffs = []
            if m["no_travel_miles"] > 0:
                diffs.append(f"{m['no_travel_miles']} mi of No Travel conditions")
            if m["severe_miles"] > 0:
                diffs.append(f"{m['severe_miles']} mi Severe weather")
            if m["high_miles"] > 0:
                diffs.append(f"{m['high_miles']} mi High risk")
            if not diffs:
                diffs.append(f"+{round(route.get('duration_hours', 0) - sorted_routes[0].get('duration_hours', 0), 1)} hrs travel time")
            route["recommendation_summary"] = "Higher risk exposure: " + ", ".join(diffs)

    return sorted_routes
