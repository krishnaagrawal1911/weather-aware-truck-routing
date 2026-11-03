import React from 'react';

export default function RouteCards({ routes, activeRouteId, onSelectRoute }) {
  if (!routes || routes.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between border-b border-zinc-800 pb-2">
        <span className="text-[11px] font-mono tracking-widest uppercase text-zinc-400">
          Evaluated Route Options ({routes.length})
        </span>
        <span className="text-[11px] font-mono uppercase text-zinc-500">
          Ranked by safety criteria
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {routes.map((route) => {
          const isActive = route.route_id === activeRouteId;
          const isRec = route.is_recommended;
          const m = route.metrics || {};
          const totalMiles = route.distance_miles || 1;

          const lowPct = ((m.low_miles || 0) / totalMiles) * 100;
          const modPct = ((m.moderate_miles || 0) / totalMiles) * 100;
          const highPct = ((m.high_miles || 0) / totalMiles) * 100;
          const sevPct = ((m.severe_miles || 0) / totalMiles) * 100;
          const noTravelPct = ((m.no_travel_miles || 0) / totalMiles) * 100;

          return (
            <div
              key={route.route_id}
              onClick={() => onSelectRoute(route.route_id)}
              className={`p-4 rounded border transition cursor-pointer flex flex-col justify-between ${
                isActive
                  ? 'bg-zinc-900 border-white text-white ring-1 ring-white/50'
                  : 'bg-black border-zinc-800 hover:border-zinc-700 text-zinc-300'
              }`}
            >
              <div>
                {/* Header with recommendation tag */}
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs text-zinc-400">#{route.rank}</span>
                  {isRec ? (
                    <span className="text-[10px] font-mono uppercase tracking-wider px-2 py-0.5 rounded bg-white text-black font-semibold">
                      Recommended
                    </span>
                  ) : (
                    <span className="text-[10px] font-mono uppercase text-zinc-500">
                      Option {route.rank}
                    </span>
                  )}
                </div>

                <h4 className="font-sans font-semibold text-sm text-white mb-1.5">{route.name}</h4>

                <div className="flex items-center gap-4 text-xs font-mono text-zinc-400 mb-3">
                  <span>{route.distance_miles} mi</span>
                  <span>•</span>
                  <span>{route.duration_formatted}</span>
                  <span>•</span>
                  <span>Avg Risk: {m.average_risk_score}</span>
                </div>

                {/* Minimalist Grayscale Risk Distribution Bar */}
                <div className="mb-3">
                  <div className="flex items-center justify-between text-[10px] font-mono text-zinc-500 mb-1">
                    <span>Corridor Exposure</span>
                    <span>{route.checkpoints?.length || 0} pts</span>
                  </div>
                  <div className="w-full h-1.5 rounded bg-zinc-800 flex overflow-hidden border border-zinc-700">
                    <div style={{ width: `${lowPct}%` }} className="bg-white" title={`Low: ${m.low_miles} mi`} />
                    <div style={{ width: `${modPct}%` }} className="bg-zinc-400" title={`Moderate: ${m.moderate_miles} mi`} />
                    <div style={{ width: `${highPct}%` }} className="bg-zinc-600" title={`High: ${m.high_miles} mi`} />
                    <div style={{ width: `${sevPct}%` }} className="bg-zinc-800" title={`Severe: ${m.severe_miles} mi`} />
                    <div style={{ width: `${noTravelPct}%` }} className="bg-black" title={`No Travel: ${m.no_travel_miles} mi`} />
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono mb-3">
                  <div className="p-2 rounded bg-zinc-950 border border-zinc-800">
                    <div className="text-[10px] uppercase text-zinc-500">Severe Miles</div>
                    <div className="text-sm font-semibold text-white">{m.severe_miles} mi</div>
                  </div>
                  <div className="p-2 rounded bg-zinc-950 border border-zinc-800">
                    <div className="text-[10px] uppercase text-zinc-500">High Miles</div>
                    <div className="text-sm font-semibold text-white">{m.high_miles} mi</div>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-zinc-800 text-[11px] font-mono text-zinc-400 flex items-center justify-between">
                <span className="truncate pr-2">{route.recommendation_summary}</span>
                <span className="text-[10px] uppercase font-mono tracking-wider shrink-0 text-zinc-500">
                  {isActive ? '[Selected]' : 'View'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
