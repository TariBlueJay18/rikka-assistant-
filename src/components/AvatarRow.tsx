import React from "react";
import { AssistantState, ThemeMode, BackendEngine } from "../types";

interface AvatarRowProps {
  mode: ThemeMode;
  state: AssistantState;
  backend: BackendEngine;
  model: string;
}

export const AvatarRow: React.FC<AvatarRowProps> = ({
  mode,
  state,
  backend,
  model,
}) => {
  const isRikka = mode === "rikka";
  const isGenerating = state === "thinking" || state === "speaking";
  const isSpeaking = state === "speaking";
  const isLocal = backend === "ollama";

  // Status text matching Python implementation
  const getStatusText = () => {
    if (isRikka) {
      if (state === "thinking") return "⟳  Unsealing spell…";
      if (state === "speaking") return "◉  Tyrant's Eye active";
      return "○  Idle";
    } else {
      if (state === "thinking") return "⟳  Processing…";
      if (state === "speaking") return "◉  Responding";
      return "○  Ready";
    }
  };

  const name = isRikka ? "Rikka Takanashi" : "AI Assistant";

  return (
    <div
      className={`px-4 py-3 flex items-center gap-3.5 border-b transition-colors duration-300 ${
        isRikka
          ? "border-[rgba(124,77,255,0.18)] bg-white/[0.02]"
          : "border-white/[0.07] bg-white/[0.02]"
      }`}
    >
      {/* Avatar Container (96px or 80px) */}
      <div className="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
        {isRikka ? (
          // ── Rikka Mode Avatar ──────────────────────────────
          <div className="relative w-18 h-18 rounded-full flex items-center justify-center">
            {/* Outer magical aura glow */}
            {isGenerating && (
              <div
                className={`absolute inset-[-6px] rounded-full filter blur-md animate-pulse-glow transition-all duration-300 ${
                  isSpeaking
                    ? "bg-gradient-to-r from-[#d050e8] via-[#e879f9] to-[#ff79c6] opacity-70"
                    : "bg-gradient-to-r from-[#7c4dff] via-[#ae86ff] to-[#6b35cc] opacity-70"
                }`}
              />
            )}

            {/* Rotating Arcane Rune Ring (during generation) */}
            {isGenerating ? (
              <div
                className={`absolute inset-[-4px] rounded-full pointer-events-none animate-spin-fast border-2 border-dashed ${
                  isSpeaking ? "border-[#d050e8]" : "border-[#ae86ff]"
                }`}
              >
                {/* 6 Arcane Rune Dots */}
                {[0, 60, 120, 180, 240, 300].map((deg) => (
                  <span
                    key={deg}
                    className="absolute w-1.5 h-1.5 bg-white rounded-full shadow-[0_0_6px_#fff]"
                    style={{
                      top: "50%",
                      left: "50%",
                      transform: `rotate(${deg}deg) translate(38px) translate(-50%, -50%)`,
                    }}
                  />
                ))}
              </div>
            ) : (
              <div className="absolute inset-[-1px] rounded-full border border-[#ae86ff]/40 pointer-events-none" />
            )}

            {/* Circular portrait image */}
            <div className="relative w-full h-full rounded-full overflow-hidden border border-[#ae86ff]/50 bg-[#141032] shadow-inner">
              <img
                src="/assets/rikka_portrait.png"
                alt="Rikka Takanashi"
                className="w-full h-full object-cover select-none pointer-events-none"
                onError={(e) => {
                  // Fallback if image path differs
                  (e.target as HTMLElement).style.display = "none";
                }}
              />

              {/* Tyrant Eye Golden Flare when speaking */}
              {isGenerating && (
                <div
                  className="absolute w-6 h-6 rounded-full pointer-events-none animate-eye-flare"
                  style={{
                    top: "34%",
                    left: "36%",
                    background:
                      "radial-gradient(circle, rgba(255,220,50,0.95) 0%, rgba(255,140,0,0.6) 45%, rgba(255,140,0,0) 75%)",
                    boxShadow: "0 0 12px rgba(255, 215, 0, 0.8)",
                  }}
                />
              )}
            </div>
          </div>
        ) : (
          // ── AI Assistant Mode: Frosted Iridescent Orb ──────
          <div className="relative w-18 h-18 rounded-full flex items-center justify-center">
            {/* Siri Animated Iridescent Perimeter Ring */}
            {isGenerating ? (
              <div
                className="absolute inset-[-4px] rounded-full p-[3px] animate-siri"
                style={{
                  background:
                    "conic-gradient(#FF375F, #BF5AF2, #0A84FF, #30D158, #FF375F)",
                }}
              >
                <div className="w-full h-full rounded-full bg-[#0a0c12]" />
              </div>
            ) : (
              <div className="absolute inset-[-2px] rounded-full border border-white/20" />
            )}

            {/* Frosted Matte Core */}
            <div
              className={`relative w-full h-full rounded-full flex items-center justify-center overflow-hidden transition-all duration-500 shadow-lg ${
                isSpeaking
                  ? "bg-gradient-to-br from-[#FF7A95] via-[#A855F7] to-[#0284C7]"
                  : state === "thinking"
                  ? "bg-gradient-to-br from-[#FBBF24] via-[#F43F5E] to-[#9333EA]"
                  : "bg-gradient-to-br from-[#38BDF8] via-[#0284C7] to-[#0F172A]"
              }`}
            >
              {/* Soft Satin Matte Diffusion Layer */}
              <div className="absolute inset-0 bg-white/20 backdrop-blur-md rounded-full pointer-events-none" />
              <div className="absolute top-0 left-1/4 right-1/4 h-1/2 bg-gradient-to-b from-white/40 to-transparent rounded-full pointer-events-none filter blur-[1px]" />

              {/* Central Glyph */}
              <span className="relative z-10 text-white font-bold text-xl drop-shadow select-none">
                {state === "thinking" ? "◌" : state === "speaking" ? "≋" : "✦"}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Text column & Engine Badge */}
      <div className="flex flex-col gap-0.5 min-w-0">
        <h2 className="text-sm font-semibold text-white tracking-wide truncate">
          {name}
        </h2>

        {/* Breathing LED Engine Badge */}
        <div className="flex items-center gap-1.5 py-0.5">
          <div className="relative flex items-center justify-center w-3 h-3">
            {/* Halo pulse */}
            <span
              className={`absolute w-full h-full rounded-full animate-ping opacity-60 ${
                isLocal ? "bg-[#4ade80]" : "bg-[#38bdf8]"
              }`}
            />
            {/* Inner solid dot */}
            <span
              className={`relative w-2 h-2 rounded-full ${
                isLocal ? "bg-[#4ade80]" : "bg-[#38bdf8]"
              }`}
            />
          </div>
          <span className="text-[10px] font-semibold tracking-wider text-white/80 uppercase">
            {isLocal ? "LOCAL" : "CLOUD"} ·{" "}
            <span className="normal-case text-white/70 font-mono text-[9.5px]">
              {model}
            </span>
          </span>
        </div>

        {/* State label */}
        <p
          className={`text-[11px] transition-colors duration-200 ${
            isRikka ? "text-[#9d8fc2]" : "text-[#94A3B8]"
          }`}
        >
          {getStatusText()}
        </p>
      </div>
    </div>
  );
};
