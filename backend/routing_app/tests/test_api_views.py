from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class ApiViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_check(self):
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("status"), "healthy")

    def test_route_plan_endpoint(self):
        payload = {
            "origin": {"lat": 41.8781, "lon": -87.6298, "name": "Chicago, IL"},
            "destination": {"lat": 39.7392, "lon": -104.9903, "name": "Denver, CO"},
            "departure_time": "2026-11-02T14:00:00",
            "load_weight_lbs": 35000,
            "sample_interval_miles": 50
        }
        response = self.client.post('/api/routes/plan/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertIn("routes", data)
        self.assertEqual(len(data["routes"]), 3)
        self.assertIn("heatmap_timeline", data)
        self.assertIn("frames", data["heatmap_timeline"])
        
        # Check that one route is recommended
        rec_count = sum(1 for r in data["routes"] if r.get("is_recommended"))
        self.assertEqual(rec_count, 1)
        
        # Check checkpoints have weather and risk
        first_route = data["routes"][0]
        self.assertTrue(len(first_route["checkpoints"]) > 0)
        first_cp = first_route["checkpoints"][0]
        self.assertIn("weather", first_cp)
        self.assertIn("risk", first_cp)
