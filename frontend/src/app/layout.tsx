import type { Metadata } from "next";
import { VT323, JetBrains_Mono, Silkscreen } from "next/font/google";
import "./globals.css";

// Blocky arcade 8-bit font matching POOPLE SOLVER reference title
const silkscreen = Silkscreen({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-pixel-heading",
});

// Crisp retro monospace font matching POOPLE SOLVER inputs & buttons
const vt323 = VT323({
  weight: "400",
  subsets: ["latin"],
  variable: "--font-pixel",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "UnWordle Solver — Cyber Pixel Engine",
  description: "Reverse Wordle solver with multi-row Hard Mode constraint satisfaction and retro cyber pixel design.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${silkscreen.variable} ${vt323.variable} ${jetbrainsMono.variable} font-sans antialiased min-h-screen bg-[#04070d] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200`}
      >
        {children}
      </body>
    </html>
  );
}
