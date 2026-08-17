"use client";

import { ColorPattern } from "@/lib/api";

export interface PresetPuzzle {
  name: string;
  solution: string;
  rows: { id: string; pattern: ColorPattern[]; initialLetters?: string }[];
  description: string;
}

export const PRESETS: PresetPuzzle[] = [
  {
    name: "CAPUT (Screenshot Puzzle)",
    solution: "CAPUT",
    rows: [
      { id: "row_1", pattern: ["yellow", "gray", "gray", "gray", "gray"], initialLetters: "ABAKA" },
      { id: "row_2", pattern: ["gray", "yellow", "gray", "yellow", "gray"], initialLetters: "BUBAL" },
      { id: "row_3", pattern: ["green", "gray", "gray", "green", "yellow"], initialLetters: "CROUP" },
    ],
    description: "3-row reverse puzzle requiring joint Hard Mode validation.",
  },
  {
    name: "CRANE (Spec Sample)",
    solution: "CRANE",
    rows: [
      { id: "row_1", pattern: ["gray", "yellow", "gray", "green", "gray"] },
      { id: "row_2", pattern: ["gray", "green", "green", "yellow", "green"] },
    ],
    description: "Standard 2-row test puzzle from the project specification.",
  },
  {
    name: "SPEED (Duplicate E's)",
    solution: "SPEED",
    rows: [
      { id: "row_1", pattern: ["yellow", "gray", "gray", "yellow", "yellow"] },
    ],
    description: "Tests duplicate letter resolution for double E's.",
  },
];

interface PresetSelectorProps {
  onSelectPreset: (preset: PresetPuzzle) => void;
  onClear: () => void;
}

export default function PresetSelector({ onSelectPreset, onClear }: PresetSelectorProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 p-4 glass-panel rounded-xl border border-slate-800">
      <div className="flex items-center gap-2">
        <span className="font-pixel text-[10px] uppercase text-emerald-400 tracking-wider">PRESETS:</span>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((preset) => (
            <button
              key={preset.name}
              onClick={() => onSelectPreset(preset)}
              className="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 text-xs font-mono text-slate-200 border border-slate-700/60 hover:border-emerald-500/40 transition-all flex items-center gap-1.5 shadow-sm active:scale-95"
            >
              <span>{preset.name}</span>
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={onClear}
        className="px-3 py-1.5 rounded-lg bg-slate-900/60 hover:bg-rose-950/40 text-xs font-mono text-slate-400 hover:text-rose-300 border border-slate-800 hover:border-rose-500/40 transition-all"
      >
        Clear Grid
      </button>
    </div>
  );
}
