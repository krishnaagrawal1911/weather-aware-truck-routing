import React from 'react';
import { Truck, HelpCircle } from 'lucide-react';

export default function Navbar({ onOpenRules }) {
  return (
    <header className="bg-black border-b border-zinc-800 px-6 py-3.5 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded border border-zinc-700 bg-zinc-900 flex items-center justify-center text-white">
            <Truck className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm tracking-widest uppercase font-bold text-white">
                TRUCK ROUTING
              </span>
              <span className="text-[10px] font-mono uppercase px-1.5 py-0.5 border border-zinc-700 text-zinc-400 rounded">
                48H WEATHER
              </span>
            </div>
            <p className="text-[11px] text-zinc-500 font-mono hidden sm:block">
              Multi-route safety evaluation & wind/precipitation hazard engine
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={onOpenRules}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-mono uppercase text-zinc-300 border border-zinc-700 hover:border-zinc-400 hover:text-white rounded transition"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Risk Matrix</span>
          </button>
        </div>
      </div>
    </header>
  );
}
