import React from 'react';
import { Circle, Tooltip } from 'react-leaflet';

export default function WeatherHeatmapOverlay({ frame, activeMetric, showHeatmap }) {
  if (!showHeatmap || !frame || !frame.points || frame.points.length === 0) {
    return null;
  }

  const getMonochromeStyle = (pt) => {
    let opacity = 0.2;
    let color = "#ffffff";
    let label = "";

    if (activeMetric === 'wind') {
      const w = pt.wind_mph;
      label = `${w} mph wind`;
      if (w >= 55) { opacity = 0.65; color = "#ffffff"; }
      else if (w >= 45) { opacity = 0.50; color = "#e4e4e7"; }
      else if (w >= 35) { opacity = 0.35; color = "#a1a1aa"; }
      else if (w >= 25) { opacity = 0.20; color = "#71717a"; }
      else { opacity = 0.08; color = "#52525b"; }
    } else if (activeMetric === 'rain') {
      const r = pt.rain_in;
      label = `${r} in/hr rain`;
      if (r > 1.0) { opacity = 0.65; color = "#ffffff"; }
      else if (r >= 0.5) { opacity = 0.50; color = "#e4e4e7"; }
      else if (r >= 0.25) { opacity = 0.35; color = "#a1a1aa"; }
      else if (r >= 0.10) { opacity = 0.20; color = "#71717a"; }
      else { opacity = 0.08; color = "#52525b"; }
    } else if (activeMetric === 'snow') {
      const s = pt.snow_in;
      label = `${s} in/hr snow`;
      if (s > 3.0) { opacity = 0.65; color = "#ffffff"; }
      else if (s >= 2.0) { opacity = 0.50; color = "#e4e4e7"; }
      else if (s >= 1.0) { opacity = 0.35; color = "#a1a1aa"; }
      else if (s >= 0.5) { opacity = 0.20; color = "#71717a"; }
      else { opacity = 0.08; color = "#52525b"; }
    } else {
      // Risk score: 1 to 5
      const s = pt.risk_score || 1;
      label = `Risk: ${pt.risk_level}`;
      if (s >= 5) { opacity = 0.65; color = "#ffffff"; }
      else if (s === 4) { opacity = 0.45; color = "#d4d4d8"; }
      else if (s === 3) { opacity = 0.30; color = "#a1a1aa"; }
      else if (s === 2) { opacity = 0.18; color = "#71717a"; }
      else { opacity = 0.08; color = "#52525b"; }
    }

    return {
      color,
      fillColor: color,
      fillOpacity: opacity,
      radius: 46000,
      label,
    };
  };

  return (
    <>
      {frame.points.map((pt, idx) => {
        const style = getMonochromeStyle(pt);
        return (
          <Circle
            key={`${idx}-${pt.lat}-${pt.lon}`}
            center={[pt.lat, pt.lon]}
            radius={style.radius}
            pathOptions={{
              color: style.color,
              fillColor: style.fillColor,
              fillOpacity: style.fillOpacity,
              weight: 0,
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
              <div className="text-xs font-mono text-zinc-900">
                <strong>{style.label}</strong>
                <br />
                Wind: {pt.wind_mph} mph | Precip: {pt.rain_in || pt.snow_in} in/hr
              </div>
            </Tooltip>
          </Circle>
        );
      })}
    </>
  );
}
