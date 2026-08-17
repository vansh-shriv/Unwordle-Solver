"use client";

export default function Header() {
  return (
    <header className="w-full pt-8 pb-4 px-4 flex flex-col items-center justify-center text-center relative z-20">
      {/* Algorithm Version Pill */}
      <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-[#020712] border border-[#00f0ff]/40 shadow-[0_0_10px_rgba(0,240,255,0.25)] mb-4">
        <span className="font-pixel text-xs text-[#00f0ff] tracking-widest uppercase">
          &gt;_ ALGORITHM VERSION 1.0
        </span>
      </div>

      {/* Main Title - UNWORDLE SOLVER in Silkscreen Blocky Pixel Font */}
      <h1 className="font-pixel-title text-2xl sm:text-4xl text-[#00f0ff] tracking-wider uppercase drop-shadow-[0_0_18px_rgba(0,240,255,0.6)] mb-2">
        UNWORDLE SOLVER
      </h1>

      {/* Subtitle in VT323 retro font */}
      <p className="font-pixel text-base sm:text-lg text-slate-400 tracking-wider">
        Minimalist Multi-Row Constraint Logic Solver
      </p>
    </header>
  );
}
