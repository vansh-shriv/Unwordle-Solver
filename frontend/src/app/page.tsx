"use client";

import { useCallback, useReducer, useState } from "react";
import Header from "@/components/Header";
import { PuzzleRow } from "@/components/Tile";
import { ColorPattern, solvePuzzle, SolveResponse } from "@/lib/api";

// ── State Types ──────────────────────────────────────────────────────────────

interface RowState {
  id: string;
  letters: string[];
  colors: ColorPattern[];
}

interface PuzzleState {
  solution: string;
  wordLength: number;
  rows: RowState[];
}

type Action =
  | { type: "SET_SOLUTION"; value: string }
  | { type: "SET_WORD_LENGTH"; length: number }
  | { type: "ADD_ROW" }
  | { type: "REMOVE_ROW"; rowIndex: number }
  | { type: "CYCLE_COLOR"; rowIndex: number; position: number }
  | { type: "SET_LETTER"; rowIndex: number; position: number; letter: string }
  | { type: "CLEAR" };

function makeEmptyRow(id: string, length: number): RowState {
  return {
    id,
    letters: Array(length).fill(""),
    colors: Array(length).fill("gray") as ColorPattern[],
  };
}

const CYCLE: ColorPattern[] = ["gray", "yellow", "green"];

function nextColor(current: ColorPattern): ColorPattern {
  return CYCLE[(CYCLE.indexOf(current) + 1) % CYCLE.length];
}

function reducer(state: PuzzleState, action: Action): PuzzleState {
  switch (action.type) {
    case "SET_SOLUTION": {
      const val = action.value.toUpperCase().replace(/[^A-Z]/g, "").slice(0, 10);
      return { ...state, solution: val };
    }
    case "SET_WORD_LENGTH": {
      const l = action.length;
      return {
        ...state,
        wordLength: l,
        rows: state.rows.map((row) => ({
          ...row,
          letters: Array(l).fill("").map((_, i) => row.letters[i] ?? ""),
          colors: Array(l).fill("gray").map((_, i) => row.colors[i] ?? "gray") as ColorPattern[],
        })),
      };
    }
    case "ADD_ROW": {
      if (state.rows.length >= 8) return state;
      const nextId = `row_${state.rows.length + 1}`;
      return { ...state, rows: [...state.rows, makeEmptyRow(nextId, state.wordLength)] };
    }
    case "REMOVE_ROW": {
      if (state.rows.length <= 1) return state;
      const newRows = state.rows.filter((_, i) => i !== action.rowIndex).map((r, i) => ({ ...r, id: `row_${i + 1}` }));
      return { ...state, rows: newRows };
    }
    case "CYCLE_COLOR": {
      const newRows = state.rows.map((row, ri) => {
        if (ri !== action.rowIndex) return row;
        const newColors = row.colors.map((c, ci) =>
          ci === action.position ? nextColor(c) : c
        );
        return { ...row, colors: newColors };
      });
      return { ...state, rows: newRows };
    }
    case "SET_LETTER": {
      const newRows = state.rows.map((row, ri) => {
        if (ri !== action.rowIndex) return row;
        const newLetters = row.letters.map((l, li) =>
          li === action.position ? action.letter : l
        );
        return { ...row, letters: newLetters };
      });
      return { ...state, rows: newRows };
    }
    case "CLEAR": {
      return {
        solution: "",
        wordLength: 5,
        rows: [makeEmptyRow("row_1", 5)],
      };
    }
  }
}

const INITIAL: PuzzleState = {
  solution: "",
  wordLength: 5,
  rows: [makeEmptyRow("row_1", 5)],
};

const LEGEND = [
  { color: "green" as ColorPattern, label: "Green (Correct)", bg: "bg-emerald-500/20", border: "border-emerald-400/40", text: "text-emerald-300" },
  { color: "yellow" as ColorPattern, label: "Yellow (Wrong Pos)", bg: "bg-amber-500/20", border: "border-amber-400/40", text: "text-amber-300" },
  { color: "gray" as ColorPattern, label: "Gray (Not in Word)", bg: "bg-slate-800", border: "border-cyan-500/30", text: "text-slate-400" },
];

export default function SolverPage() {
  const [state, dispatch] = useReducer(reducer, INITIAL);
  const [result, setResult] = useState<SolveResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [distinctWords, setDistinctWords] = useState(true);

  const handleColorCycle = useCallback((rowIndex: number, position: number) => {
    dispatch({ type: "CYCLE_COLOR", rowIndex, position });
  }, []);

  const handleLetterChange = useCallback((rowIndex: number, position: number, letter: string) => {
    dispatch({ type: "SET_LETTER", rowIndex, position, letter });
  }, []);

  const handleSolve = async () => {
    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const payload = {
        solution: state.solution,
        rows: state.rows.map((row) => ({ id: row.id, pattern: row.colors })),
        options: {
          max_candidates_per_row: 20,
          distinct_words_across_rows: distinctWords,
        },
      };
      const res = await solvePuzzle(payload);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "An unknown error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setResult(null);
    setError(null);
    dispatch({ type: "CLEAR" });
  };

  const unsolvableSet = new Set(result?.unsolvable_row_ids ?? []);
  const canSolve = state.solution.length === state.wordLength && state.rows.length > 0;

  return (
    <div className="min-h-screen flex flex-col bg-[#04070d] relative overflow-x-hidden">
      {/* Background Cyber Elements */}
      <div className="fixed inset-0 pixel-grid-bg pointer-events-none" />
      <div className="fixed inset-0 bg-glow-cyan pointer-events-none" />
      <div className="fixed inset-0 scanline-overlay opacity-30 pointer-events-none" />

      {/* Main Header */}
      <Header />

      {/* Main Content Area */}
      <main className="relative z-10 flex-1 w-full max-w-2xl mx-auto px-4 pb-16 space-y-6">

        {/* Cyber Main Container Card (matching POOPLE SOLVER reference image) */}
        <div className="cyber-card cyber-card-corners-bottom p-6 sm:p-8 space-y-6">

          {/* Solution Input Box */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-pixel text-xs text-[#00f0ff] tracking-widest uppercase flex items-center gap-1.5">
                <span>⚡</span> SOLUTION WORD
              </span>
              <button
                onClick={handleClear}
                className="font-pixel text-xs text-slate-400 hover:text-rose-400 border border-slate-700 hover:border-rose-500/40 px-2.5 py-1 bg-slate-900/60 transition-colors"
              >
                CLEAR
              </button>
            </div>

            <div className="relative">
              <input
                type="text"
                value={state.solution}
                onChange={(e) => dispatch({ type: "SET_SOLUTION", value: e.target.value })}
                maxLength={10}
                placeholder={`ENTER ${state.wordLength}-LETTER TARGET WORD…`}
                className="w-full cyber-input px-4 py-4 font-pixel text-2xl sm:text-3xl text-center uppercase tracking-[0.25em] rounded-none"
              />
              {state.solution && (
                <span className={`absolute right-4 top-1/2 -translate-y-1/2 font-pixel text-xs ${state.solution.length === state.wordLength ? "text-emerald-400" : "text-amber-400"}`}>
                  {state.solution.length}/{state.wordLength}
                </span>
              )}
            </div>
          </div>

          {/* Word Length Selector & Options */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2 border-t border-cyan-500/20">
            {/* Word Length */}
            <div className="flex items-center gap-2">
              <span className="font-pixel text-xs text-slate-400 tracking-wider">
                WORD LENGTH:
              </span>
              <div className="flex gap-1">
                {[4, 5, 6, 7, 8].map((n) => (
                  <button
                    key={n}
                    onClick={() => dispatch({ type: "SET_WORD_LENGTH", length: n })}
                    className={`font-pixel text-sm w-8 h-8 flex items-center justify-center border transition-all ${
                      state.wordLength === n
                        ? "bg-[#00f0ff]/20 border-[#00f0ff] text-[#00f0ff] shadow-[0_0_10px_rgba(0,240,255,0.4)]"
                        : "bg-slate-900/80 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>

            {/* Distinct Toggle */}
            <label className="flex items-center gap-2.5 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={distinctWords}
                onChange={(e) => setDistinctWords(e.target.checked)}
                className="w-3.5 h-3.5 accent-[#00f0ff] bg-slate-900 border-slate-700 rounded-none cursor-pointer"
              />
              <span className="font-pixel text-xs text-slate-400 tracking-wider">
                DISTINCT WORDS
              </span>
            </label>
          </div>

          {/* Puzzle Grid Section */}
          <div className="space-y-4 pt-4 border-t border-cyan-500/20">
            <div className="flex items-center justify-between">
              <span className="font-pixel text-xs text-[#00f0ff] tracking-widest uppercase flex items-center gap-1.5">
                <span>⚙</span> ROW PATTERNS
              </span>
              <span className="font-pixel text-xs text-slate-500">
                CLICK TILE = CYCLE COLOR
              </span>
            </div>

            {/* Puzzle Rows */}
            <div className="space-y-3">
              {state.rows.map((row, rowIndex) => (
                <div key={row.id} className="relative group">
                  <PuzzleRow
                    rowIndex={rowIndex}
                    wordLength={state.wordLength}
                    letters={row.letters}
                    colors={row.colors}
                    onColorCycle={handleColorCycle}
                    onLetterChange={handleLetterChange}
                    rowId={row.id}
                  />
                  {state.rows.length > 1 && (
                    <button
                      onClick={() => dispatch({ type: "REMOVE_ROW", rowIndex })}
                      className="absolute -right-2 -top-1 font-pixel text-xs text-rose-500 hover:text-rose-300 w-5 h-5 flex items-center justify-center border border-rose-500/30 bg-slate-900 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Remove row"
                    >
                      ×
                    </button>
                  )}
                </div>
              ))}
            </div>

            {state.rows.length < 8 && (
              <button
                onClick={() => dispatch({ type: "ADD_ROW" })}
                className="w-full py-2.5 font-pixel text-xs text-slate-400 hover:text-[#00f0ff] border border-dashed border-cyan-500/30 hover:border-[#00f0ff] bg-cyan-950/10 transition-all tracking-widest uppercase flex items-center justify-center gap-2"
              >
                + ADD ROW
              </button>
            )}
          </div>

          {/* Action Button: SOLVER LADDER in Silkscreen Blocky Font */}
          <div className="pt-2">
            <button
              onClick={handleSolve}
              disabled={!canSolve || loading}
              className="w-full py-4 cyber-btn-primary font-pixel-title text-sm sm:text-base tracking-[0.2em] uppercase flex items-center justify-center gap-2"
            >
              {loading ? (
                <span>SOLVING PUZZLE…</span>
              ) : (
                <span>SOLVE PUZZLE &rarr;</span>
              )}
            </button>
          </div>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="cyber-card p-4 border-rose-500/40 bg-rose-950/20 text-rose-300 animate-fade-slide">
            <p className="font-pixel text-xs text-rose-400 mb-1">ERROR</p>
            <p className="font-mono text-xs text-rose-300">{error}</p>
          </div>
        )}

        {/* Results Container Card (styled matching POOPLE SOLVER results box) */}
        {result && (
          <div className="cyber-card cyber-card-corners-bottom p-6 space-y-5 animate-fade-slide border-[#00f0ff]/40">
            <div className="flex items-center justify-between pb-3 border-b border-cyan-500/20">
              <div>
                <p className="font-pixel text-xs text-[#00f0ff] tracking-widest uppercase">
                  RESULT FOUND
                </p>
                <h3 className="font-pixel-title text-sm sm:text-base text-white tracking-wider mt-1">
                  {result.rows.filter(r => r.best_guess).length} STEPS TRANSFORMATION
                </h3>
              </div>
              <div className="font-pixel text-xs px-3 py-1.5 bg-[#00f0ff]/10 border border-[#00f0ff]/30 text-[#00f0ff]">
                TARGET: {result.solution}
              </div>
            </div>

            {/* Step Results */}
            <div className="space-y-4">
              {result.rows.map((rowResult) => {
                const isUnsolvable = unsolvableSet.has(rowResult.id);
                return (
                  <PuzzleRow
                    key={rowResult.id}
                    rowIndex={0}
                    wordLength={result.word_length}
                    letters={rowResult.best_guess ? rowResult.best_guess.split("") : []}
                    colors={rowResult.pattern}
                    onColorCycle={() => {}}
                    onLetterChange={() => {}}
                    rowId={rowResult.id}
                    bestGuess={rowResult.best_guess}
                    candidates={rowResult.candidates}
                    isUnsolvable={isUnsolvable}
                    isResult={true}
                  />
                );
              })}
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
