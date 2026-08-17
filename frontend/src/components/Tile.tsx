"use client";

import { useState } from "react";
import { ColorPattern } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────────

interface TileProps {
  letter: string;
  color: ColorPattern;
  position: number;
  rowIndex: number;
  onColorCycle: (rowIndex: number, position: number) => void;
  onLetterChange: (rowIndex: number, position: number, letter: string) => void;
  isResult?: boolean;
}

// ── Color Configuration ───────────────────────────────────────────────────────

const TILE_BG: Record<ColorPattern, string> = {
  gray:   "rgba(10, 16, 30, 0.9)",
  yellow: "rgba(234, 179, 8, 0.18)",
  green:  "rgba(16, 185, 129, 0.2)",
};

const TILE_BORDER: Record<ColorPattern, string> = {
  gray:   "rgba(0, 210, 255, 0.3)",
  yellow: "rgba(234, 179, 8, 0.65)",
  green:  "rgba(16, 185, 129, 0.7)",
};

const TILE_GLOW: Record<ColorPattern, string> = {
  gray:   "none",
  yellow: "0 0 15px rgba(234, 179, 8, 0.25)",
  green:  "0 0 18px rgba(16, 185, 129, 0.3)",
};

const TILE_TEXT: Record<ColorPattern, string> = {
  gray:   "#ffffff",
  yellow: "#fde68a",
  green:  "#6ee7b7",
};

// ── Tile Component ────────────────────────────────────────────────────────────

export function Tile({ letter, color, position, rowIndex, onColorCycle, onLetterChange, isResult }: TileProps) {
  const [flipping, setFlipping] = useState(false);

  const handleClick = () => {
    if (isResult) return;
    setFlipping(true);
    setTimeout(() => setFlipping(false), 320);
    onColorCycle(rowIndex, position);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (isResult) return;
    if (e.key.length === 1 && /[a-zA-Z]/.test(e.key)) {
      e.preventDefault();
      onLetterChange(rowIndex, position, e.key.toUpperCase());
    } else if (e.key === "Backspace" || e.key === "Delete") {
      e.preventDefault();
      onLetterChange(rowIndex, position, "");
    }
  };

  return (
    <div
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={isResult ? -1 : 0}
      role="button"
      aria-label={`Tile ${position + 1}, color: ${color}, letter: ${letter || "empty"}`}
      className={`
        relative flex-1 aspect-square rounded-sm flex items-center justify-center
        cursor-pointer select-none outline-none
        transition-all duration-150
        focus-visible:ring-1 focus-visible:ring-[#00f0ff]
        ${!isResult ? "hover:brightness-125 hover:border-[#00f0ff]" : ""}
        ${flipping ? "animate-tile-flip" : ""}
      `}
      style={{
        background: TILE_BG[color],
        border: `1.5px solid ${TILE_BORDER[color]}`,
        boxShadow: TILE_GLOW[color],
        maxWidth: 54,
      }}
    >
      {/* Letter in VT323 pixel font */}
      <span
        className="font-pixel text-2xl sm:text-3xl z-10 pointer-events-none select-none tracking-widest"
        style={{
          color: TILE_TEXT[color],
          textShadow: color === "gray" 
            ? "0 2px 4px rgba(0,0,0,0.8)" 
            : `0 0 10px ${TILE_TEXT[color]}`,
        }}
      >
        {letter || ""}
      </span>

      {/* Subtle CRT scanline effect on tile */}
      <div
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{ background: "repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.3) 2px, rgba(0,0,0,0.3) 4px)" }}
      />
    </div>
  );
}

// ── PuzzleRow Component ───────────────────────────────────────────────────────

interface PuzzleRowProps {
  rowIndex: number;
  wordLength: number;
  letters: string[];
  colors: ColorPattern[];
  onColorCycle: (rowIndex: number, position: number) => void;
  onLetterChange: (rowIndex: number, position: number, letter: string) => void;
  rowId: string;
  bestGuess?: string | null;
  candidates?: string[];
  isUnsolvable?: boolean;
  isResult?: boolean;
}

export function PuzzleRow({
  rowIndex,
  wordLength,
  letters,
  colors,
  onColorCycle,
  onLetterChange,
  rowId,
  bestGuess,
  candidates,
  isUnsolvable,
  isResult,
}: PuzzleRowProps) {
  const [showCandidates, setShowCandidates] = useState(false);
  const displayLetters = bestGuess ? bestGuess.split("") : letters;
  const rowNumber = rowId.split("_")[1] || (rowIndex + 1).toString();

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-4">
        {/* Row Label */}
        <div className="w-16 flex-shrink-0 flex items-center justify-end gap-1.5 pr-2 select-none">
          <span className="font-pixel text-xs text-[#00f0ff] opacity-70 tracking-wider">
            ROW
          </span>
          <span className="font-pixel text-sm text-[#00f0ff] font-bold">
            {rowNumber}
          </span>
        </div>

        {/* Tile Grid Container */}
        <div className="flex gap-2 flex-1 max-w-[340px]">
          {Array.from({ length: wordLength }).map((_, i) => (
            <Tile
              key={i}
              letter={displayLetters[i] ?? ""}
              color={colors[i] ?? "gray"}
              position={i}
              rowIndex={rowIndex}
              onColorCycle={onColorCycle}
              onLetterChange={onLetterChange}
              isResult={isResult}
            />
          ))}
        </div>

        {/* Result status / Best Guess output */}
        {isResult && (
          <div className="ml-2 flex items-center gap-2 flex-wrap">
            {isUnsolvable ? (
              <span className="font-pixel text-xs text-rose-400 px-2 py-1 border border-rose-500/30 bg-rose-950/30">
                UNSOLVABLE
              </span>
            ) : bestGuess ? (
              <>
                <span
                  className="font-pixel text-sm sm:text-base px-3 py-1.5 text-[#6ee7b7] bg-emerald-500/10 border border-emerald-400/40 shadow-[0_0_12px_rgba(16,185,129,0.2)] tracking-widest"
                >
                  {bestGuess}
                </span>
                {candidates && candidates.length > 1 && (
                  <button
                    onClick={() => setShowCandidates((v) => !v)}
                    className="font-pixel text-xs text-[#00f0ff] hover:text-white px-1.5 py-1 border border-cyan-500/30 hover:border-cyan-400 bg-cyan-950/20 transition-all"
                  >
                    +{candidates.length - 1}
                  </button>
                )}
              </>
            ) : null}
          </div>
        )}
      </div>

      {/* Expanded Candidate Words */}
      {isResult && showCandidates && candidates && candidates.length > 1 && (
        <div className="ml-20 flex flex-wrap gap-2 pt-1 animate-fade-slide">
          {candidates.slice(1).map((w) => (
            <span
              key={w}
              className="font-pixel text-xs px-2 py-1 bg-slate-900 border border-cyan-500/20 text-slate-300 tracking-widest"
            >
              {w}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
