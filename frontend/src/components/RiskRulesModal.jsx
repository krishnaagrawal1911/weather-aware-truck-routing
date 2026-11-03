import React from 'react';
import { X } from 'lucide-react';

export default function RiskRulesModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
      <div className="bg-black border border-zinc-700 rounded-lg max-w-2xl w-full p-6 text-white font-mono shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-zinc-400 hover:text-white p-1 rounded hover:bg-zinc-900 transition"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="mb-4 border-b border-zinc-800 pb-3">
          <h2 className="text-sm uppercase tracking-widest font-bold text-white">
            Truck Safety & Load Risk Protocol
          </h2>
          <p className="text-xs text-zinc-500 mt-0.5">Threshold specifications and rollover prevention rules</p>
        </div>

        {/* Hazard Thresholds Table */}
        <div className="overflow-x-auto mb-5">
          <table className="w-full text-left text-xs border border-zinc-800">
            <thead className="bg-zinc-900 text-zinc-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="p-2.5 border-b border-zinc-800">Condition</th>
                <th className="p-2.5 border-b border-zinc-800">Low</th>
                <th className="p-2.5 border-b border-zinc-800">Moderate</th>
                <th className="p-2.5 border-b border-zinc-800">High</th>
                <th className="p-2.5 border-b border-zinc-800">Severe</th>
                <th className="p-2.5 border-b border-zinc-800 text-white font-bold">No Travel</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800 text-[11px]">
              <tr>
                <td className="p-2.5 font-semibold text-zinc-300">Wind</td>
                <td className="p-2.5 text-zinc-400">&lt;25 mph</td>
                <td className="p-2.5 text-zinc-400">25–34</td>
                <td className="p-2.5 text-zinc-400">35–44</td>
                <td className="p-2.5 text-zinc-400">45–54</td>
                <td className="p-2.5 font-bold text-white">≥55 mph</td>
              </tr>
              <tr>
                <td className="p-2.5 font-semibold text-zinc-300">Rain</td>
                <td className="p-2.5 text-zinc-400">&lt;0.10 in/hr</td>
                <td className="p-2.5 text-zinc-400">0.10–0.25</td>
                <td className="p-2.5 text-zinc-400">0.25–0.50</td>
                <td className="p-2.5 text-zinc-400">0.50–1.00</td>
                <td className="p-2.5 font-bold text-white">&gt;1.00 in/hr</td>
              </tr>
              <tr>
                <td className="p-2.5 font-semibold text-zinc-300">Snow</td>
                <td className="p-2.5 text-zinc-400">&lt;0.5 in/hr</td>
                <td className="p-2.5 text-zinc-400">0.5–1.0</td>
                <td className="p-2.5 text-zinc-400">1.0–2.0</td>
                <td className="p-2.5 text-zinc-400">2.0–3.0</td>
                <td className="p-2.5 font-bold text-white">&gt;3.0 in/hr</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Load Rules */}
        <div className="bg-zinc-950 border border-zinc-800 rounded p-4 mb-5 text-xs space-y-2">
          <div className="text-[10px] uppercase tracking-widest text-zinc-400 font-bold">
            Load Weight Modifiers
          </div>
          <ul className="space-y-1.5 text-zinc-300 text-[11px]">
            <li>• <strong className="text-white">≥55 mph Wind:</strong> Immediate <strong>No Travel</strong> shutdown for any vehicle load.</li>
            <li>• <strong className="text-white">45–54 mph Wind + &gt;30,000 lb Load:</strong> Escalates to <strong>No Travel</strong> (rollover prevention).</li>
            <li>• <strong className="text-white">35–44 mph Wind + &gt;40,000 lb Load:</strong> Upgrades from High to <strong>Severe</strong>.</li>
          </ul>
        </div>

        {/* Priority Order */}
        <div className="border border-zinc-800 rounded p-4 text-[11px] text-zinc-400 space-y-1 mb-5">
          <div className="text-[10px] uppercase tracking-widest text-white font-bold mb-1">
            Recommendation Hierarchy
          </div>
          <div>1. Fewest Severe & No Travel miles</div>
          <div>2. Fewest High risk miles</div>
          <div>3. Lowest average risk index</div>
          <div>4. Shortest travel time</div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-white text-black text-xs uppercase font-semibold rounded hover:bg-zinc-200 transition"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
}
