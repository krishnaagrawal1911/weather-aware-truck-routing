import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Popup, useMap } from 'react-leaflet';
import WeatherHeatmapOverlay from './WeatherHeatmapOverlay';

function MapBoundsUpdater({ routes, origin, destination }) {
  const map = useMap();

  useEffect(() => {
    if (!routes || routes.length === 0) {
      if (origin && destination) {
        map.fitBounds([
          [origin.lat, origin.lon],
          [destination.lat, destination.lon],
        ], { padding: [60, 60] });
      }
      return;
    }

    const allCoords = [];
    routes.forEach((r) => {
      (r.coordinates || []).forEach(([lon, lat]) => {
        allCoords.push([lat, lon]);
      });
    });

    if (allCoords.length > 0) {
      map.fitBounds(allCoords, { padding: [50, 50], maxZoom: 11 });
    }
  }, [routes, origin, destination, map]);

  return null;
}

export default function MapView({
  routes,
  activeRouteId,
  onSelectRoute,
  origin,
  destination,
  timeline,
  currentHour,
  activeMetric,
  showHeatmap,
}) {
  const defaultCenter = [39.8283, -98.5795];
  const activeRoute = routes?.find((r) => r.route_id === activeRouteId) || routes?.[0];
  const activeFrame = timeline?.frames?.[currentHour];

  const getCheckpointMarkerStyle = (riskLevel) => {
    switch (riskLevel) {
      case 'No Travel':
        return { color: '#ffffff', fillColor: '#000000', weight: 2.5, radius: 8 };
      case 'Severe':
        return { color: '#ffffff', fillColor: '#27272a', weight: 1.5, radius: 7 };
      case 'High':
        return { color: '#000000', fillColor: '#71717a', weight: 1, radius: 6 };
      case 'Moderate':
        return { color: '#000000', fillColor: '#d4d4d8', weight: 1, radius: 5 };
      default: // Low
        return { color: '#000000', fillColor: '#ffffff', weight: 1, radius: 5 };
    }
  };

  return (
    <div className="relative w-full h-[600px] lg:h-full rounded-lg overflow-hidden border border-zinc-800 bg-black">
      <MapContainer
        center={defaultCenter}
        zoom={5}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a> & OpenStreetMap'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png"
        />

        <MapBoundsUpdater routes={routes} origin={origin} destination={destination} />

        <WeatherHeatmapOverlay
          frame={activeFrame}
          activeMetric={activeMetric}
          showHeatmap={showHeatmap}
        />

        {/* Alternative Inactive routes */}
        {routes?.filter((r) => r.route_id !== activeRouteId).map((r) => {
          const latLngs = (r.coordinates || []).map(([lon, lat]) => [lat, lon]);
          return (
            <Polyline
              key={r.route_id}
              positions={latLngs}
              eventHandlers={{
                click: () => onSelectRoute(r.route_id),
              }}
              pathOptions={{
                color: '#52525b',
                weight: 2.5,
                dashArray: '4, 6',
                opacity: 0.7,
              }}
            />
          );
        })}

        {/* Active Route in solid white */}
        {activeRoute && (
          <Polyline
            positions={(activeRoute.coordinates || []).map(([lon, lat]) => [lat, lon])}
            pathOptions={{
              color: '#ffffff',
              weight: 4,
              opacity: 0.95,
            }}
          />
        )}

        {/* Checkpoint Markers */}
        {activeRoute?.checkpoints?.map((cp) => {
          const riskLevel = cp.risk?.overall_risk || 'Low';
          const style = getCheckpointMarkerStyle(riskLevel);

          return (
            <CircleMarker
              key={`cp-${cp.index}-${cp.lat}-${cp.lon}`}
              center={[cp.lat, cp.lon]}
              radius={style.radius}
              pathOptions={{
                color: style.color,
                fillColor: style.fillColor,
                fillOpacity: 1,
                weight: style.weight,
              }}
            >
              <Popup>
                <div className="p-2 min-w-[210px] text-white font-mono text-xs space-y-1.5">
                  <div className="flex items-center justify-between border-b border-zinc-800 pb-1">
                    <span className="text-zinc-400 uppercase">CP #{cp.index + 1}</span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold border border-zinc-700 bg-zinc-900 text-white">
                      {riskLevel}
                    </span>
                  </div>

                  <div className="flex justify-between text-zinc-400">
                    <span>Distance:</span>
                    <span className="text-white">{cp.distance_from_origin_miles} mi</span>
                  </div>
                  <div className="flex justify-between text-zinc-400">
                    <span>ETA:</span>
                    <span className="text-white">{new Date(cp.eta).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
                  </div>

                  <div className="bg-zinc-950 border border-zinc-800 rounded p-1.5 space-y-1 text-[11px] my-1">
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Wind:</span>
                      <span className="text-white font-semibold">{cp.weather?.wind_speed_mph} mph</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Rain:</span>
                      <span className="text-white font-semibold">{cp.weather?.rain_in_hr} in/hr</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-zinc-500">Snow:</span>
                      <span className="text-white font-semibold">{cp.weather?.snow_in_hr} in/hr</span>
                    </div>
                  </div>

                  {cp.risk?.summary && (
                    <div className="text-[10px] text-zinc-400 border border-zinc-800 bg-zinc-900 rounded p-1">
                      {cp.risk.summary}
                    </div>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          );
        })}

        {/* Origin Marker */}
        {origin && (
          <CircleMarker
            center={[origin.lat, origin.lon]}
            radius={7}
            pathOptions={{ color: '#000000', fillColor: '#ffffff', fillOpacity: 1, weight: 2 }}
          >
            <Popup>
              <div className="text-xs font-mono p-1 text-white">
                <span className="text-zinc-400 uppercase block text-[10px]">Origin</span>
                <strong>{origin.name}</strong>
              </div>
            </Popup>
          </CircleMarker>
        )}

        {/* Destination Marker */}
        {destination && (
          <CircleMarker
            center={[destination.lat, destination.lon]}
            radius={7}
            pathOptions={{ color: '#ffffff', fillColor: '#000000', fillOpacity: 1, weight: 2 }}
          >
            <Popup>
              <div className="text-xs font-mono p-1 text-white">
                <span className="text-zinc-400 uppercase block text-[10px]">Destination</span>
                <strong>{destination.name}</strong>
              </div>
            </Popup>
          </CircleMarker>
        )}
      </MapContainer>

      {/* Minimalist Legend */}
      <div className="absolute top-4 right-4 z-20 bg-black/90 border border-zinc-800 rounded p-3 text-white text-[10px] font-mono pointer-events-auto">
        <div className="uppercase tracking-widest text-zinc-500 mb-2 border-b border-zinc-800 pb-1">
          Hazard Index
        </div>
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-white border border-black"></span>
            <span>Low (&lt;25 mph / &lt;0.10 in)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-zinc-300"></span>
            <span>Moderate (25-34 mph)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-zinc-500"></span>
            <span>High (35-44 mph)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-zinc-800 border border-white"></span>
            <span>Severe (45-54 mph)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-black border border-white"></span>
            <span className="font-semibold text-white">No Travel (&gt;=55 mph)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
