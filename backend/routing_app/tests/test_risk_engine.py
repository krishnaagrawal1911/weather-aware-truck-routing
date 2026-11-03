from django.test import TestCase
from routing_app.services.risk_engine import (
    RiskLevel,
    evaluate_wind_risk,
    evaluate_rain_risk,
    evaluate_snow_risk,
    evaluate_checkpoint_risk,
)

class RiskEngineTestCase(TestCase):
    def test_wind_thresholds_standard_load(self):
        # Base load = 20,000 lbs (no special modifiers)
        load = 20000.0
        
        # Low < 25 mph
        risk, _ = evaluate_wind_risk(15.0, load)
        self.assertEqual(risk, RiskLevel.LOW)
        
        risk, _ = evaluate_wind_risk(24.9, load)
        self.assertEqual(risk, RiskLevel.LOW)
        
        # Moderate 25-34 mph
        risk, _ = evaluate_wind_risk(25.0, load)
        self.assertEqual(risk, RiskLevel.MODERATE)
        
        risk, _ = evaluate_wind_risk(34.0, load)
        self.assertEqual(risk, RiskLevel.MODERATE)
        
        # High 35-44 mph
        risk, _ = evaluate_wind_risk(35.0, load)
        self.assertEqual(risk, RiskLevel.HIGH)
        
        risk, _ = evaluate_wind_risk(44.0, load)
        self.assertEqual(risk, RiskLevel.HIGH)
        
        # Severe 45-54 mph
        risk, _ = evaluate_wind_risk(45.0, load)
        self.assertEqual(risk, RiskLevel.SEVERE)
        
        risk, _ = evaluate_wind_risk(54.0, load)
        self.assertEqual(risk, RiskLevel.SEVERE)
        
        # No Travel >= 55 mph
        risk, _ = evaluate_wind_risk(55.0, load)
        self.assertEqual(risk, RiskLevel.NO_TRAVEL)
        
        risk, _ = evaluate_wind_risk(70.0, load)
        self.assertEqual(risk, RiskLevel.NO_TRAVEL)

    def test_load_weight_modifiers(self):
        # 1. >= 55 mph -> No Travel for any load
        risk, _ = evaluate_wind_risk(56.0, 5000.0)
        self.assertEqual(risk, RiskLevel.NO_TRAVEL)
        
        # 2. 45-54 mph + >30,000 lb -> No Travel
        # At 30,000 lb, still Severe
        risk, _ = evaluate_wind_risk(48.0, 30000.0)
        self.assertEqual(risk, RiskLevel.SEVERE)
        # At 30,001 lb, upgrades to No Travel
        risk, reason = evaluate_wind_risk(48.0, 30001.0)
        self.assertEqual(risk, RiskLevel.NO_TRAVEL)
        self.assertIn("triggers No Travel", reason)
        
        # 3. 35-44 mph + >40,000 lb -> Severe
        # At 40,000 lb, still High
        risk, _ = evaluate_wind_risk(40.0, 40000.0)
        self.assertEqual(risk, RiskLevel.HIGH)
        # At 45,000 lb, upgrades to Severe
        risk, reason = evaluate_wind_risk(40.0, 45000.0)
        self.assertEqual(risk, RiskLevel.SEVERE)
        self.assertIn("upgraded to Severe", reason)

    def test_rain_thresholds(self):
        # Low < 0.10 in/hr
        risk, _ = evaluate_rain_risk(0.05)
        self.assertEqual(risk, RiskLevel.LOW)
        
        # Moderate 0.10–0.25 in/hr
        risk, _ = evaluate_rain_risk(0.10)
        self.assertEqual(risk, RiskLevel.MODERATE)
        risk, _ = evaluate_rain_risk(0.25)
        self.assertEqual(risk, RiskLevel.MODERATE)
        
        # High 0.25–0.50 in/hr
        risk, _ = evaluate_rain_risk(0.35)
        self.assertEqual(risk, RiskLevel.HIGH)
        
        # Severe 0.50–1.00 in/hr
        risk, _ = evaluate_rain_risk(0.75)
        self.assertEqual(risk, RiskLevel.SEVERE)
        risk, _ = evaluate_rain_risk(1.00)
        self.assertEqual(risk, RiskLevel.SEVERE)
        
        # No Travel > 1.00 in/hr
        risk, _ = evaluate_rain_risk(1.05)
        self.assertEqual(risk, RiskLevel.NO_TRAVEL)

    def test_snow_thresholds(self):
        # Low < 0.5 in/hr
        risk, _ = evaluate_snow_risk(0.2)
        self.assertEqual(risk, RiskLevel.LOW)
        
        # Moderate 0.5–1.0 in/hr
        risk, _ = evaluate_snow_risk(0.5)
        self.assertEqual(risk, RiskLevel.MODERATE)
        risk, _ = evaluate_snow_risk(1.0)
        self.assertEqual(risk, RiskLevel.MODERATE)
        
        # High 1.0–2.0 in/hr
        risk, _ = evaluate_snow_risk(1.5)
        self.assertEqual(risk, RiskLevel.HIGH)
        
        # Severe 2.0–3.0 in/hr
        risk, _ = evaluate_snow_risk(2.5)
        self.assertEqual(risk, RiskLevel.SEVERE)
        risk, _ = evaluate_snow_risk(3.0)
        self.assertEqual(risk, RiskLevel.SEVERE)
        
        # No Travel > 3.0 in/hr
        risk, _ = evaluate_snow_risk(3.2)
        self.assertEqual(risk, RiskLevel.NO_TRAVEL)

    def test_checkpoint_composite_risk(self):
        # Max severity should dominate:
        # Wind is Low (10 mph), Rain is Severe (0.8 in/hr), Snow is Low (0 in/hr)
        result = evaluate_checkpoint_risk(10.0, 0.8, 0.0, 20000.0)
        self.assertEqual(result["overall_risk"], RiskLevel.SEVERE.value)
        self.assertEqual(result["primary_hazard"], "Rain")
        
        # Wind upgraded by weight triggers No Travel
        result = evaluate_checkpoint_risk(48.0, 0.1, 0.0, 35000.0)
        self.assertEqual(result["overall_risk"], RiskLevel.NO_TRAVEL.value)
        self.assertEqual(result["primary_hazard"], "Wind")
