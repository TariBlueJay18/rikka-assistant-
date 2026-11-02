import React, { useRef } from "react";
import { ThemeMode, BackendEngine, ModelTier } from "../types";
import { Cloud, Zap, Minus, X, GripVertical, Music, Sparkles, Brain, Cpu } from "lucide-react";

interface TitleBarProps {
  mode: ThemeMode;
  backend: BackendEngine;
  modelTier: ModelTier;
  onToggleBackend: () => void;
  onToggleMode: (originPoint?: { x: number; y: number }) => void;
  onCycleModelTier: () => void;
  onOpenMusic: () => void;
  onOpenImage: () => void;
  onMinimize?: () => void;
  onClose?: () => void;
}

export const TitleBar: React.FC<TitleBarProps> = ({
  mode,
  backend,
  modelTier,
  onToggleBackend,
  onToggleMode,
  onCycleModelTier,
  onOpenMusic,
  onOpenImage,
  onMinimize,
  onClose,
}) => {
  const isRikka = mode === "rikka";
  const isCloud = backend === "gemini";
  const modeBtnRef = useRef<HTMLButtonElement>(null);

  const handleModeClick = () => {
    if (modeBtnRef.current) {
      const rect = modeBtnRef.current.getBoundingClientRect();
      onToggleMode({
        x: rect.left + rect.width / 2,
        y: rect.top + rect.height / 2,
      });
    } else {
      onToggleMode();
    }
  };

  const getTierBadge = () => {
    switch (modelTier) {
      case "fast":
        return { label: "Fast", icon: Zap, color: "text-amber-400 border-amber-400/40 bg-amber-400/10" };
      case "complex":
        return { label: "Argon", icon: Brain, color: "text-purple-400 border-purple-400/40 bg-purple-400/10" };
      case "general":
      default:
        return { label: "General", icon: Cpu, color: "text-sky-400 border-sky-400/40 bg-sky-400/10" };
    }
  };

  const tierBadge = getTierBadge();
  const TierIcon = tierBadge.icon;

  return (
    <header
      className={`h-11 px-3.5 flex items-center justify-between select-none border-b transition-colors duration-300 ${
        isRikka
          ? "border-[rgba(124,77,255,0.22)] bg-transparent"
          : "border-[rgba(255,255,255,0.08)] bg-transparent"
      }`}
    >
      {/* Left: Grip & Title */}
      <div className="flex items-center gap-2">
        <span title="Drag assistant">
          <GripVertical className="w-4 h-4 text-white/30 cursor-grab active:cursor-grabbing hover:text-white/60 transition-colors" />
        </span>
        <h1
          className={`text-xs font-semibold tracking-wider flex items-center gap-1.5 ${
            isRikka ? "text-[#ae86ff]" : "text-white"
          }`}
        >
          {isRikka ? "✦  Rikka Assistant" : "AI Assistant"}
        </h1>
      </div>

      {/* Right: Studio Shortcuts, Tiers & Controls */}
      <div className="flex items-center gap-1.5">
        {/* Model Tier Pill (Fast / General / Argon) */}
        {isCloud && (
          <button
            onClick={onCycleModelTier}
            className={`text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1 transition-all cursor-pointer ${tierBadge.color}`}
            title={`Active Gemini Model Tier: ${tierBadge.label} (Click to cycle Fast 3.1-lite -> General 3.8-flash -> Complex 4-argon)`}
          >
            <TierIcon className="w-3 h-3" />
            <span>{tierBadge.label}</span>
          </button>
        )}

        {/* Music Studio Shortcut */}
        <button
          onClick={onOpenMusic}
          className="p-1 rounded-lg text-white/60 hover:text-[#e879f9] hover:bg-white/10 transition-colors cursor-pointer"
          title="Summon Music (Lyria 3)"
        >
          <Music className="w-3.5 h-3.5" />
        </button>

        {/* Image Studio Shortcut */}
        <button
          onClick={onOpenImage}
          className="p-1 rounded-lg text-white/60 hover:text-[#e879f9] hover:bg-white/10 transition-colors cursor-pointer"
          title="Image Alchemy (gemini-nano-banana-2.1)"
        >
          <Sparkles className="w-3.5 h-3.5" />
        </button>

        {/* Backend Toggle (Local vs Cloud) */}
        <button
          onClick={onToggleBackend}
          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1 transition-all cursor-pointer ${
            isCloud
              ? "bg-[rgba(56,189,248,0.14)] border border-[rgba(56,189,248,0.38)] text-[#38bdf8] hover:bg-[rgba(56,189,248,0.25)] hover:border-[#38bdf8] hover:text-white"
              : "bg-[rgba(74,222,128,0.14)] border border-[rgba(74,222,128,0.38)] text-[#4ade80] hover:bg-[rgba(74,222,128,0.25)] hover:border-[#4ade80] hover:text-white"
          }`}
          title={
            isCloud
              ? "Running on Cloud via Gemini API. Click to switch to Local (Ollama)."
              : "Running locally via Ollama. Click to switch to Cloud (Gemini)."
          }
        >
          {isCloud ? (
            <>
              <Cloud className="w-3 h-3" />
              <span>Cloud</span>
            </>
          ) : (
            <>
              <Zap className="w-3 h-3" />
              <span>Local</span>
            </>
          )}
        </button>

        {/* Mode Toggle Button (Rikka vs AI Assistant) */}
        <button
          ref={modeBtnRef}
          onClick={handleModeClick}
          className={`text-[10px] font-semibold px-2 py-0.5 rounded-full flex items-center gap-1 transition-all cursor-pointer ${
            isRikka
              ? "bg-[rgba(124,77,255,0.18)] border border-[rgba(174,134,255,0.38)] text-[#e879f9] hover:bg-[rgba(208,80,232,0.28)] hover:border-[#d050e8] hover:text-white"
              : "bg-white/10 border border-white/20 text-[#38bdf8] hover:bg-[#38bdf8]/25 hover:border-[#38bdf8] hover:text-white"
          }`}
          title={
            isRikka
              ? "Active: Chunibyo Magic. Click for wave transition to AI Assistant Mode."
              : "Active: AI Assistant Mode. Click for wave transition to Rikka Mode."
          }
        >
          <span>{isRikka ? "🫧 AI" : "✦ Rikka"}</span>
        </button>

        {/* Window controls */}
        <button
          onClick={onMinimize}
          className="w-6 h-6 flex items-center justify-center rounded-md text-white/50 hover:bg-white/10 hover:text-white transition-colors cursor-pointer text-xs"
          title="Minimise"
        >
          <Minus className="w-3 h-3" />
        </button>
        <button
          onClick={onClose}
          className="w-6 h-6 flex items-center justify-center rounded-md text-white/50 hover:bg-red-500/30 hover:text-red-400 transition-colors cursor-pointer text-xs"
          title="Close"
        >
          <X className="w-3 h-3" />
        </button>
      </div>
    </header>
  );
};
