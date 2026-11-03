from enum import Enum
from typing import Dict, Any, Tuple

class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"
    NO_TRAVEL = "No Travel"

RISK_ORDER = {
    RiskLevel.LOW: 1,
    RiskLevel.MODERATE: 2,
    RiskLevel.HIGH: 3,
    RiskLevel.SEVERE: 4,
    RiskLevel.NO_TRAVEL: 5,
}

# Minimalist high-contrast monochrome tokens
RISK_COLORS = {
    RiskLevel.LOW: "#ffffff",
    RiskLevel.MODERATE: "#a1a1aa",
    RiskLevel.HIGH: "#71717a",
    RiskLevel.SEVERE: "#27272a",
    RiskLevel.NO_TRAVEL: "#000000",
}

def evaluate_wind_risk(wind_mph: float, load_lbs: float) -> Tuple[RiskLevel, str]:
    if wind_mph >= 55.0:
        return RiskLevel.NO_TRAVEL, "Wind >= 55 mph: mandatory shutdown"
    
    if 45.0 <= wind_mph <= 54.0:
        if load_lbs > 30000.0:
            return RiskLevel.NO_TRAVEL, f"Wind 45-54 mph ({wind_mph:.1f} mph) with load >30k lbs triggers No Travel"
        return RiskLevel.SEVERE, f"Wind 45-54 mph ({wind_mph:.1f} mph)"
        
    if 35.0 <= wind_mph < 45.0:
        if load_lbs > 40000.0:
            return RiskLevel.SEVERE, f"Wind 35-44 mph ({wind_mph:.1f} mph) with load >40k lbs upgraded to Severe"
        return RiskLevel.HIGH, f"Wind 35-44 mph ({wind_mph:.1f} mph)"
        
    if 25.0 <= wind_mph < 35.0:
        return RiskLevel.MODERATE, f"Wind 25-34 mph ({wind_mph:.1f} mph)"
        
    return RiskLevel.LOW, f"Wind < 25 mph ({wind_mph:.1f} mph)"


def evaluate_rain_risk(rain_in_hr: float) -> Tuple[RiskLevel, str]:
    if rain_in_hr > 1.00:
        return RiskLevel.NO_TRAVEL, f"Rain > 1.00 in/hr ({rain_in_hr:.2f} in/hr) triggers No Travel"
    if rain_in_hr > 0.50:
        return RiskLevel.SEVERE, f"Rain 0.50-1.00 in/hr ({rain_in_hr:.2f} in/hr)"
    if rain_in_hr > 0.25:
        return RiskLevel.HIGH, f"Rain 0.25-0.50 in/hr ({rain_in_hr:.2f} in/hr)"
    if rain_in_hr >= 0.10:
        return RiskLevel.MODERATE, f"Rain 0.10-0.25 in/hr ({rain_in_hr:.2f} in/hr)"
    return RiskLevel.LOW, f"Rain < 0.10 in/hr ({rain_in_hr:.2f} in/hr)"


def evaluate_snow_risk(snow_in_hr: float) -> Tuple[RiskLevel, str]:
    if snow_in_hr > 3.0:
        return RiskLevel.NO_TRAVEL, f"Snow > 3.0 in/hr ({snow_in_hr:.2f} in/hr) triggers No Travel"
    if snow_in_hr > 2.0:
        return RiskLevel.SEVERE, f"Snow 2.0-3.0 in/hr ({snow_in_hr:.2f} in/hr)"
    if snow_in_hr > 1.0:
        return RiskLevel.HIGH, f"Snow 1.0-2.0 in/hr ({snow_in_hr:.2f} in/hr)"
    if snow_in_hr >= 0.5:
        return RiskLevel.MODERATE, f"Snow 0.5-1.0 in/hr ({snow_in_hr:.2f} in/hr)"
    return RiskLevel.LOW, f"Snow < 0.5 in/hr ({snow_in_hr:.2f} in/hr)"


def evaluate_checkpoint_risk(wind_mph: float, rain_in_hr: float, snow_in_hr: float, load_lbs: float) -> Dict[str, Any]:
    wind_risk, wind_reason = evaluate_wind_risk(wind_mph, load_lbs)
    rain_risk, rain_reason = evaluate_rain_risk(rain_in_hr)
    snow_risk, snow_reason = evaluate_snow_risk(snow_in_hr)

    candidates = [
        (wind_risk, wind_reason, "Wind"),
        (rain_risk, rain_reason, "Rain"),
        (snow_risk, snow_reason, "Snow"),
    ]
    candidates.sort(key=lambda x: RISK_ORDER[x[0]], reverse=True)
    highest_risk, highest_reason, primary_hazard = candidates[0]

    return {
        "overall_risk": highest_risk.value,
        "overall_risk_score": RISK_ORDER[highest_risk],
        "primary_hazard": primary_hazard,
        "color": RISK_COLORS[highest_risk],
        "wind": {
            "value_mph": round(wind_mph, 1),
            "risk": wind_risk.value,
            "reason": wind_reason,
        },
        "rain": {
            "value_in_hr": round(rain_in_hr, 2),
            "risk": rain_risk.value,
            "reason": rain_reason,
        },
        "snow": {
            "value_in_hr": round(snow_in_hr, 2),
            "risk": snow_risk.value,
            "reason": snow_reason,
        },
        "summary": highest_reason,
    }
