import React, { useState } from 'react';
import { ArrowRight, Loader2 } from 'lucide-react';

const PRESET_CORRIDORS = [
  { name: "Chicago → Denver", origin: "Chicago, IL", dest: "Denver, CO", weight: 35000 },
  { name: "Seattle → Salt Lake", origin: "Seattle, WA", dest: "Salt Lake City, UT", weight: 42000 },
  { name: "Dallas → Atlanta", origin: "Dallas, TX", dest: "Atlanta, GA", weight: 28000 },
];

export default function RouteForm({ onSubmit, isLoading }) {
  const [origin, setOrigin] = useState("Chicago, IL");
  const [destination, setDestination] = useState("Denver, CO");
  
  const getInitialDateTime = () => {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 16);
  };

  const [departureTime, setDepartureTime] = useState(getInitialDateTime());
  const [loadWeight, setLoadWeight] = useState(35000);
  const [sampleInterval, setSampleInterval] = useState(25);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!origin || !destination) return;
    onSubmit({
      origin,
      destination,
      departure_time: new Date(departureTime).toISOString(),
      load_weight_lbs: Number(loadWeight),
      sample_interval_miles: Number(sampleInterval),
    });
  };

  const applyPreset = (preset) => {
    setOrigin(preset.origin);
    setDestination(preset.dest);
    setLoadWeight(preset.weight);
  };

  return (
    <div className="bg-black border border-zinc-800 rounded-lg p-5 text-white">
      <div className="flex items-center justify-between mb-4 border-b border-zinc-800 pb-3">
        <span className="text-[11px] font-mono tracking-widest uppercase text-zinc-400">
          Trip Configuration
        </span>
        <div className="flex items-center gap-1.5 overflow-x-auto">
          <span className="text-[10px] font-mono uppercase text-zinc-500 mr-1 hidden sm:inline">Presets:</span>
          {PRESET_CORRIDORS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => applyPreset(p)}
              className="text-[11px] font-mono px-2 py-0.5 rounded border border-zinc-800 bg-zinc-900 hover:border-zinc-500 text-zinc-300 transition"
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-[11px] font-mono uppercase text-zinc-400 mb-1.5">
              Origin City / Terminal
            </label>
            <input
              type="text"
              required
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              placeholder="e.g. Chicago, IL"
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-white transition"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono uppercase text-zinc-400 mb-1.5">
              Destination Terminal
            </label>
            <input
              type="text"
              required
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="e.g. Denver, CO"
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-sm text-white placeholder-zinc-600 focus:outline-none focus:border-white transition"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-[11px] font-mono uppercase text-zinc-400 mb-1.5">
              Departure Time
            </label>
            <input
              type="datetime-local"
              required
              value={departureTime}
              onChange={(e) => setDepartureTime(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-white transition"
            />
          </div>

          <div>
            <label className="block text-[11px] font-mono uppercase text-zinc-400 mb-1.5 flex justify-between">
              <span>Load Weight</span>
              <span className="text-zinc-500">
                {loadWeight > 40000 ? ">40k lb (Heavy)" : loadWeight > 30000 ? ">30k lb (Mid)" : "Standard"}
              </span>
            </label>
            <div className="relative">
              <input
                type="number"
                min="1000"
                max="90000"
                step="500"
                required
                value={loadWeight}
                onChange={(e) => setLoadWeight(e.target.value)}
                className="w-full bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-sm font-mono text-white focus:outline-none focus:border-white transition pr-10"
              />
              <span className="absolute right-3 top-2 text-xs font-mono text-zinc-500 pointer-events-none">lbs</span>
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-mono uppercase text-zinc-400 mb-1.5">
              Sample Checkpoint Distance
            </label>
            <div className="grid grid-cols-3 gap-1 bg-zinc-900 border border-zinc-800 p-1 rounded">
              {[10, 25, 50].map((dist) => (
                <button
                  key={dist}
                  type="button"
                  onClick={() => setSampleInterval(dist)}
                  className={`text-xs font-mono py-1 rounded transition ${
                    sampleInterval === dist
                      ? 'bg-white text-black font-semibold'
                      : 'text-zinc-400 hover:text-white'
                  }`}
                >
                  {dist} mi
                </button>
              ))}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2.5 px-4 bg-white hover:bg-zinc-200 disabled:opacity-50 text-black text-xs font-mono uppercase tracking-widest font-semibold rounded flex items-center justify-center gap-2 transition cursor-pointer mt-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-black" />
              <span>Evaluating Corridors...</span>
            </>
          ) : (
            <>
              <span>Calculate 3 Routes & Evaluate Safety</span>
              <ArrowRight className="w-4 h-4 text-black" />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
