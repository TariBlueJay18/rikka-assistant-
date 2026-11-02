import React, { useState, useRef, useEffect } from "react";
import { ThemeMode, ModelTier, GroundingMode } from "../types";
import {
  BarChart3,
  Trash2,
  Settings,
  ArrowUp,
  Monitor,
  Globe,
  MapPin,
  Music,
  Sparkles,
  Zap,
  Cpu,
  Brain,
} from "lucide-react";

interface InputBarProps {
  mode: ThemeMode;
  isBusy: boolean;
  screenEnabled: boolean;
  systemEnabled: boolean;
  modelTier: ModelTier;
  groundingMode: GroundingMode;
  onSendMessage: (text: string) => void;
  onStats: () => void;
  onClear: () => void;
  onSettings: () => void;
  onToggleScreen: () => void;
  onToggleSystem: () => void;
  onCycleModelTier: () => void;
  onToggleGrounding: () => void;
  onOpenMusic: () => void;
  onOpenImage: () => void;
}

export const InputBar: React.FC<InputBarProps> = ({
  mode,
  isBusy,
  screenEnabled,
  systemEnabled,
  modelTier,
  groundingMode,
  onSendMessage,
  onStats,
  onClear,
  onSettings,
  onToggleScreen,
  onToggleSystem,
  onCycleModelTier,
  onToggleGrounding,
  onOpenMusic,
  onOpenImage,
}) => {
  const isRikka = mode === "rikka";
  const [inputText, setInputText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto resize textarea height (1-5 lines)
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(Math.max(scrollHeight, 42), 120)}px`;
    }
  }, [inputText]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleSubmit = () => {
    const trimmed = inputText.trim();
    if (!trimmed || isBusy) return;
    onSendMessage(trimmed);
    setInputText("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "42px";
    }
  };

  const getTierInfo = () => {
    switch (modelTier) {
      case "fast":
        return { label: "Fast", icon: Zap, tooltip: "gemini-3.1-flash-lite (Ultra Fast)" };
      case "complex":
        return { label: "Argon", icon: Brain, tooltip: "gemini-4-argon (Complex reasoning & STEM)" };
      case "general":
      default:
        return { label: "General", icon: Cpu, tooltip: "gemini-3.8-flash (Balanced multimodal & tools)" };
    }
  };

  const tier = getTierInfo();
  const TierIcon = tier.icon;

  const getGroundingLabel = () => {
    switch (groundingMode) {
      case "search":
        return { label: "Search ON", icon: Globe, color: "text-sky-300 border-sky-400/40 bg-sky-500/15" };
      case "maps":
        return { label: "Maps ON", icon: MapPin, color: "text-emerald-300 border-emerald-400/40 bg-emerald-500/15" };
      case "none":
        return { label: "Ground OFF", icon: Globe, color: "text-white/40 border-white/10 bg-white/5" };
      case "auto":
      default:
        return { label: "Ground Auto", icon: Globe, color: "text-[#ae86ff] border-[#ae86ff]/40 bg-[#ae86ff]/10" };
    }
  };

  const ground = getGroundingLabel();
  const GroundIcon = ground.icon;

  return (
    <footer
      className={`p-3 border-t transition-colors duration-300 ${
        isRikka
          ? "border-[rgba(124,77,255,0.22)] bg-transparent"
          : "border-white/[0.08] bg-transparent"
      }`}
    >
      {/* ── Action & Privacy Toggles Row ── */}
      <div className="flex items-center justify-between gap-1 mb-2 overflow-x-auto pb-1 scrollbar-none">
        {/* Core Actions */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Hardware Stats */}
          <button
            onClick={onStats}
            disabled={isBusy}
            className={`w-7 h-7 flex items-center justify-center rounded-lg border transition-all cursor-pointer ${
              isRikka
                ? "bg-[rgba(124,77,255,0.10)] border-[rgba(124,77,255,0.18)] text-[#ae86ff] hover:bg-[rgba(124,77,255,0.22)] hover:border-[#ae86ff]"
                : "bg-white/[0.06] border-white/10 text-slate-300 hover:bg-white/12 hover:border-white/20"
            }`}
            title="System hardware metrics"
          >
            <BarChart3 className="w-3.5 h-3.5" />
          </button>

          {/* Clear History */}
          <button
            onClick={onClear}
            disabled={isBusy}
            className={`w-7 h-7 flex items-center justify-center rounded-lg border transition-all cursor-pointer ${
              isRikka
                ? "bg-[rgba(124,77,255,0.10)] border-[rgba(124,77,255,0.18)] text-[#ae86ff] hover:bg-[rgba(124,77,255,0.22)] hover:border-[#ae86ff]"
                : "bg-white/[0.06] border-white/10 text-slate-300 hover:bg-white/12 hover:border-white/20"
            }`}
            title="Clear conversation history"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>

          {/* Settings Modal */}
          <button
            onClick={onSettings}
            className={`w-7 h-7 flex items-center justify-center rounded-lg border transition-all cursor-pointer ${
              isRikka
                ? "bg-[rgba(124,77,255,0.10)] border-[rgba(124,77,255,0.18)] text-[#ae86ff] hover:bg-[rgba(124,77,255,0.22)] hover:border-[#ae86ff]"
                : "bg-white/[0.06] border-white/10 text-slate-300 hover:bg-white/12 hover:border-white/20"
            }`}
            title="Open Settings dialog"
          >
            <Settings className="w-3.5 h-3.5" />
          </button>

          {/* Music Generation Trigger */}
          <button
            onClick={onOpenMusic}
            className="w-7 h-7 flex items-center justify-center rounded-lg border border-[#e879f9]/30 bg-[#e879f9]/10 text-[#e879f9] hover:bg-[#e879f9]/25 transition-all cursor-pointer"
            title="Generate Music with Lyria 3"
          >
            <Music className="w-3.5 h-3.5" />
          </button>

          {/* Image Generation Trigger */}
          <button
            onClick={onOpenImage}
            className="w-7 h-7 flex items-center justify-center rounded-lg border border-[#38BDF8]/30 bg-[#38BDF8]/10 text-[#38BDF8] hover:bg-[#38BDF8]/25 transition-all cursor-pointer"
            title="Create & Edit Images with gemini-nano-banana-2.1"
          >
            <Sparkles className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Feature Toggles */}
        <div className="flex items-center gap-1 flex-shrink-0">
          {/* Model Tier Pill */}
          <button
            onClick={onCycleModelTier}
            className="text-[9.5px] font-semibold px-2 py-0.5 rounded-md border flex items-center gap-1 bg-white/5 border-white/15 text-white/80 hover:bg-white/10 cursor-pointer transition-all"
            title={tier.tooltip}
          >
            <TierIcon className="w-3 h-3 text-[#38BDF8]" />
            <span>{tier.label}</span>
          </button>

          {/* Grounding Toggle */}
          <button
            onClick={onToggleGrounding}
            className={`text-[9.5px] font-semibold px-2 py-0.5 rounded-md border flex items-center gap-1 transition-all cursor-pointer ${ground.color}`}
            title="Cycle Grounding: Auto -> Search -> Maps -> Off"
          >
            <GroundIcon className="w-3 h-3" />
            <span>{ground.label}</span>
          </button>

          {/* Screen Context Toggle */}
          <button
            onClick={onToggleScreen}
            className={`text-[9.5px] font-semibold px-1.5 py-0.5 rounded-md border flex items-center gap-1 transition-all cursor-pointer ${
              screenEnabled
                ? isRikka
                  ? "bg-[rgba(124,77,255,0.25)] border-[#ae86ff] text-[#ede7f6]"
                  : "bg-[#38BDF8]/20 border-[#38BDF8] text-white"
                : "bg-white/[0.04] border-white/10 text-slate-400 hover:bg-white/10 hover:text-white"
            }`}
            title="Attach screen screenshot to queries"
          >
            <Monitor className="w-3 h-3" />
            <span>Screen:{screenEnabled ? "ON" : "OFF"}</span>
          </button>
        </div>
      </div>

      {/* ── Text Input & Send Button Row ── */}
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Invoke command or query… (Enter to send | Shift+Enter for newline)"
          rows={1}
          className={`flex-1 rounded-xl px-3 py-2 text-[13px] leading-relaxed resize-none outline-none border transition-all ${
            isRikka
              ? "bg-[#100e26]/85 border-[rgba(124,77,255,0.38)] text-[#ede7f6] placeholder-[#9d8fc2]/50 focus:border-[#ae86ff]"
              : "bg-white/[0.07] border-white/15 text-white placeholder-slate-400/60 focus:border-[#38BDF8] focus:bg-white/10"
          }`}
        />

        <button
          onClick={handleSubmit}
          disabled={!inputText.trim() || isBusy}
          className={`w-10 h-10 flex-shrink-0 rounded-xl flex items-center justify-center transition-all cursor-pointer shadow-md disabled:opacity-40 disabled:cursor-not-allowed ${
            isRikka
              ? "bg-gradient-to-br from-[#7c4dff] to-[#d050e8] hover:from-[#ae86ff] hover:to-[#e879f9] text-white border border-white/20"
              : "bg-gradient-to-br from-[#0071E3] to-[#0056B3] hover:from-[#38BDF8] hover:to-[#0071E3] text-white border border-white/25"
          }`}
          title="Send message (Enter)"
        >
          <ArrowUp className="w-4 h-4 stroke-[2.5]" />
        </button>
      </div>
    </footer>
  );
};
