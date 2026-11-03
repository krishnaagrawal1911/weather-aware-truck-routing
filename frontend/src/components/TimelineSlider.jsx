import React, { useEffect, useState } from 'react';
import { Play, Pause, RotateCcw } from 'lucide-react';

export default function TimelineSlider({
  timeline,
  currentHour,
  onHourChange,
  activeMetric,
  onMetricChange,
  showHeatmap,
  onToggleHeatmap,
}) {
  const [isPlaying, setIsPlaying] = useState(false);

  const frames = timeline?.frames || [];
  const currentFrame = frames[currentHour] || {};

  useEffect(() => {
    let interval = null;
    if (isPlaying) {
      interval = setInterval(() => {
        onHourChange((prev) => {
          if (prev >= 48) {
            setIsPlaying(false);
            return 48;
          }
          return prev + 1;
        });
      }, 700);
    }
    return () => clearInterval(interval);
  }, [isPlaying, onHourChange]);

  const togglePlay = () => {
    if (currentHour >= 48) {
      onHourChange(0);
      setIsPlaying(true);
    } else {
      setIsPlaying(!isPlaying);
    }
  };

  return (
    <div className="bg-black border border-zinc-800 rounded-lg p-4 text-white">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        {/* Controls and timeline readout */}
        <div className="flex items-center gap-3">
          <button
            onClick={togglePlay}
            className="p-2 rounded border border-zinc-700 bg-zinc-900 hover:bg-white hover:text-black text-white transition cursor-pointer"
            title={isPlaying ? "Pause" : "Play 48h Forecast"}
          >
            {isPlaying ? <Pause className="w-3.5 h-3.5 fill-current" /> : <Play className="w-3.5 h-3.5 fill-current" />}
          </button>

          <button
            onClick={() => onHourChange(0)}
            className="p-2 rounded border border-zinc-800 bg-zinc-900 hover:border-zinc-500 text-zinc-300 transition"
            title="Reset to Hour 0"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold text-white uppercase">
                T+{currentHour}H
              </span>
              <span className="text-[11px] font-mono text-zinc-400">
                {currentFrame.display_time || "Departure"}
              </span>
            </div>
            <p className="text-[10px] font-mono uppercase text-zinc-500">
              Trip Corridor 0-48h Weather Evolution
            </p>
          </div>
        </div>

        {/* Toggles */}
        <div className="flex items-center gap-2">
          <button
            onClick={onToggleHeatmap}
            className={`px-2.5 py-1 text-xs font-mono uppercase rounded border transition ${
              showHeatmap
                ? 'bg-white text-black font-semibold border-white'
                : 'bg-zinc-900 text-zinc-400 border-zinc-800 hover:text-white'
            }`}
          >
            Heatmap {showHeatmap ? 'ON' : 'OFF'}
          </button>

          <div className="flex items-center bg-zinc-900 border border-zinc-800 p-0.5 rounded text-xs font-mono uppercase">
            {['risk', 'wind', 'rain', 'snow'].map((m) => (
              <button
                key={m}
                onClick={() => onMetricChange(m)}
                className={`px-2 py-0.5 rounded transition ${
                  activeMetric === m
                    ? 'bg-white text-black font-semibold'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="relative pt-1">
        <input
          type="range"
          min="0"
          max="48"
          step="1"
          value={currentHour}
          onChange={(e) => onHourChange(Number(e.target.value))}
          className="w-full h-1.5 bg-zinc-800 rounded appearance-none cursor-pointer accent-white"
        />
        <div className="flex justify-between text-[10px] font-mono text-zinc-600 mt-1">
          <span>00H (DEPARTURE)</span>
          <span>+12H</span>
          <span>+24H</span>
          <span>+36H</span>
          <span>+48H (HORIZON)</span>
        </div>
      </div>
    </div>
  );
}
