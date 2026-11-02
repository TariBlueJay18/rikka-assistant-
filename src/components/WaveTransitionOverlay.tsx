import React, { useEffect, useState } from "react";
import { ThemeMode } from "../types";

interface WaveTransitionOverlayProps {
  origin: { x: number; y: number } | null;
  toMode: ThemeMode;
  onAnimationEnd: () => void;
}

export const WaveTransitionOverlay: React.FC<WaveTransitionOverlayProps> = ({
  origin,
  toMode,
  onAnimationEnd,
}) => {
  const [active, setActive] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setActive(false);
      onAnimationEnd();
    }, 650);
    return () => clearTimeout(timer);
  }, [onAnimationEnd]);

  if (!active || !origin) return null;

  const isToRikka = toMode === "rikka";

  return (
    <div
      className="absolute inset-0 pointer-events-none z-50 overflow-hidden rounded-[22px]"
      style={{
        ["--wave-origin-x" as any]: `${origin.x}px`,
        ["--wave-origin-y" as any]: `${origin.y}px`,
      }}
    >
      {/* Liquid expanding wave boundary */}
      <div
        className={`w-full h-full animate-wave-ripple shadow-2xl transition-opacity ${
          isToRikka
            ? "bg-gradient-to-b from-[#141032] via-[#0e0c24] to-[#060412] border border-[#ae86ff]/40"
            : "bg-gradient-to-b from-white/10 via-[#181c26]/95 to-[#0a0c12]/98 border border-white/20 backdrop-blur-xl"
        }`}
      >
        {/* Subtle luminous crest ring */}
        <div
          className={`w-full h-full ${
            isToRikka
              ? "bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#ae86ff]/20 via-transparent to-transparent"
              : "bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#38bdf8]/20 via-transparent to-transparent"
          }`}
        />
      </div>
    </div>
  );
};
