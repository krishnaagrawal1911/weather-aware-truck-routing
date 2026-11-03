from django.test import TestCase
from routing_app.services.recommendation_engine import (
    calculate_route_metrics,
    rank_and_recommend_routes,
)
from routing_app.services.risk_engine import RiskLevel

class RecommendationEngineTestCase(TestCase):
    def make_dummy_route(self, route_id, name, severe_mi, high_mi, avg_score, dur_hrs, no_travel_mi=0.0):
        # Build dummy checkpoints matching the miles
        checkpoints = []
        if no_travel_mi > 0:
            checkpoints.append({
                "step_distance_miles": no_travel_mi,
                "risk": {"overall_risk": RiskLevel.NO_TRAVEL.value, "overall_risk_score": 5.0}
            })
        if severe_mi > 0:
            checkpoints.append({
                "step_distance_miles": severe_mi,
                "risk": {"overall_risk": RiskLevel.SEVERE.value, "overall_risk_score": 4.0}
            })
        if high_mi > 0:
            checkpoints.append({
                "step_distance_miles": high_mi,
                "risk": {"overall_risk": RiskLevel.HIGH.value, "overall_risk_score": 3.0}
            })
        # Use avg_score for the baseline checkpoint to allow testing average score differences
        checkpoints.append({
            "step_distance_miles": 50.0,
            "risk": {"overall_risk": RiskLevel.MODERATE.value if avg_score > 1.5 else RiskLevel.LOW.value, "overall_risk_score": avg_score}
        })
        return {
            "route_id": route_id,
            "name": name,
            "duration_hours": dur_hrs,
            "duration_formatted": f"{dur_hrs}h",
            "checkpoints": checkpoints,
        }

    def test_priority_1_fewest_severe_miles(self):
        # Route A has 10 severe miles, Route B has 20 severe miles, even if Route B is shorter
        route_a = self.make_dummy_route("A", "Route A", severe_mi=10.0, high_mi=0.0, avg_score=2.0, dur_hrs=5.0)
        route_b = self.make_dummy_route("B", "Route B", severe_mi=20.0, high_mi=0.0, avg_score=1.5, dur_hrs=3.0)
        
        ranked = rank_and_recommend_routes([route_b, route_a])
        self.assertEqual(ranked[0]["route_id"], "A")
        self.assertTrue(ranked[0]["is_recommended"])

    def test_priority_2_fewest_high_miles_when_severe_tied(self):
        # Both have 0 severe miles. Route A has 15 high miles, Route B has 5 high miles.
        route_a = self.make_dummy_route("A", "Route A", severe_mi=0.0, high_mi=15.0, avg_score=2.0, dur_hrs=4.0)
        route_b = self.make_dummy_route("B", "Route B", severe_mi=0.0, high_mi=5.0, avg_score=1.8, dur_hrs=5.0)
        
        ranked = rank_and_recommend_routes([route_a, route_b])
        self.assertEqual(ranked[0]["route_id"], "B")
        self.assertTrue(ranked[0]["is_recommended"])

    def test_priority_3_lowest_average_risk_when_high_tied(self):
        # Both have 0 severe, 0 high. Route A has more moderate risk than Route B.
        route_a = self.make_dummy_route("A", "Route A", severe_mi=0.0, high_mi=0.0, avg_score=1.8, dur_hrs=4.0)
        route_b = self.make_dummy_route("B", "Route B", severe_mi=0.0, high_mi=0.0, avg_score=1.2, dur_hrs=4.5)
        
        ranked = rank_and_recommend_routes([route_a, route_b])
        self.assertEqual(ranked[0]["route_id"], "B")
        self.assertTrue(ranked[0]["is_recommended"])

    def test_priority_4_shortest_duration_when_all_risk_tied(self):
        # Both have 0 severe, 0 high, identical average risk.
        route_a = self.make_dummy_route("A", "Route A", severe_mi=0.0, high_mi=0.0, avg_score=1.0, dur_hrs=6.0)
        route_b = self.make_dummy_route("B", "Route B", severe_mi=0.0, high_mi=0.0, avg_score=1.0, dur_hrs=4.2)
        
        ranked = rank_and_recommend_routes([route_a, route_b])
        self.assertEqual(ranked[0]["route_id"], "B")
        self.assertTrue(ranked[0]["is_recommended"])
