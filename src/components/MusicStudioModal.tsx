import React, { useState } from "react";
import { ThemeMode, GeneratedMusic } from "../types";
import { X, Music, Sparkles, RefreshCw, Send, Radio } from "lucide-react";
import { AudioPlayerWidget } from "./AudioPlayerWidget";

interface MusicStudioModalProps {
  isOpen: boolean;
  mode: ThemeMode;
  onClose: () => void;
  onMusicCreated: (music: GeneratedMusic) => void;
  screenContextB64?: string | null;
}

export const MusicStudioModal: React.FC<MusicStudioModalProps> = ({
  isOpen,
  mode,
  onClose,
  onMusicCreated,
  screenContextB64,
}) => {
  if (!isOpen) return null;

  const isRikka = mode === "rikka";

  const [prompt, setPrompt] = useState("");
  const [duration, setDuration] = useState<"clip" | "pro">("clip");
  const [includeImage, setIncludeImage] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedMusic, setGeneratedMusic] = useState<GeneratedMusic | null>(null);

  const presets = isRikka
    ? [
        "Dramatic anime gothic opening with intense violins, celestial choir, and dark synth bass",
        "Ethereal dark fantasy lullaby with glockenspiel and melancholic piano melodies",
        "High-energy chuunibyo battle climax theme with electric guitars and rapid orchestra",
        "Mystical void incantation melody with haunting vocal hums and deep temple bells",
      ]
    : [
        "Sleek modern ambient electronic soundscape with warm synthesizer pads and gentle pulses",
        "Uplifting cinematic neoclassical piano with soaring strings and subtle tape delay",
        "Futuristic cybernetic chillout groove with crisp hi-hats and deep sub-bass",
        "Deep focus study beat with jazzy Rhodes chords and soothing rain textures",
      ];

  const handleGenerate = async () => {
    if (!prompt.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/music/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          duration,
          imageBase64: includeImage && screenContextB64 ? screenContextB64 : undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Failed to generate music");
      }

      const musicItem: GeneratedMusic = {
        audioUrl: data.audioDataUrl,
        lyrics: data.lyrics,
        prompt: prompt.trim(),
        model: data.model,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setGeneratedMusic(musicItem);
    } catch (err: any) {
      setError(err.message || "Failed to generate music.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendToChat = () => {
    if (generatedMusic) {
      onMusicCreated(generatedMusic);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fade-in">
      <div
        className={`w-full max-w-lg max-h-[92vh] flex flex-col rounded-[22px] border shadow-2xl overflow-hidden transition-all ${
          isRikka
            ? "bg-[#0e0c24] border-[rgba(124,77,255,0.4)] text-[#ede7f6]"
            : "bg-gradient-to-b from-[#181c26]/95 to-[#0e1018]/98 border-white/20 text-white"
        }`}
      >
        {/* Header */}
        <div className="px-5 py-3.5 flex items-center justify-between border-b border-white/10">
          <div className="flex items-center gap-2">
            <Music className="w-4 h-4 text-[#e879f9]" />
            <h2 className="text-sm font-bold tracking-wide">
              {isRikka ? "Forbidden Music Grimoire" : "Lyria Music Synthesis"}
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 font-mono text-white/70">
              {duration === "clip" ? "lyria-3-clip-preview" : "lyria-3-pro-preview"}
            </span>
          </div>

          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-white/50 hover:bg-white/10 hover:text-white cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
          {/* Track duration model switch */}
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-[#ae86ff] mb-1.5 block">
              Track Length & Model
            </label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setDuration("clip")}
                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                  duration === "clip"
                    ? isRikka
                      ? "bg-[#7c4dff]/25 border-[#ae86ff] text-white"
                      : "bg-[#0071E3]/25 border-[#38BDF8] text-white"
                    : "bg-white/[0.04] border-white/10 text-white/60 hover:bg-white/10"
                }`}
              >
                <div className="flex items-center justify-between mb-0.5">
                  <span className="font-bold text-xs">Short Clip (≤ 30s)</span>
                  <Radio className="w-3.5 h-3.5" />
                </div>
                <p className="text-[10px] text-white/50 font-mono">
                  lyria-3-clip-preview · Rapid sample
                </p>
              </button>

              <button
                type="button"
                onClick={() => setDuration("pro")}
                className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                  duration === "pro"
                    ? isRikka
                      ? "bg-[#7c4dff]/25 border-[#ae86ff] text-white"
                      : "bg-[#0071E3]/25 border-[#38BDF8] text-white"
                    : "bg-white/[0.04] border-white/10 text-white/60 hover:bg-white/10"
                }`}
              >
                <div className="flex items-center justify-between mb-0.5">
                  <span className="font-bold text-xs">Full-Length Track</span>
                  <Radio className="w-3.5 h-3.5" />
                </div>
                <p className="text-[10px] text-white/50 font-mono">
                  lyria-3-pro-preview · Master quality
                </p>
              </button>
            </div>
          </div>

          {/* Prompt */}
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-[#ae86ff] mb-1.5 block">
              Musical Composition Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              placeholder="Describe the style, instrumentation, mood, tempo, and atmosphere..."
              className="w-full bg-white/5 border border-white/15 rounded-xl p-3 text-xs text-white placeholder-white/30 resize-none outline-none focus:border-[#38BDF8] leading-relaxed"
            />
          </div>

          {/* Presets */}
          <div>
            <p className="text-[10px] text-white/60 mb-1.5 font-medium">
              Summoning Presets:
            </p>
            <div className="flex flex-wrap gap-1.5">
              {presets.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => setPrompt(preset)}
                  className="text-[10.5px] px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/10 hover:bg-white/10 text-white/80 transition-colors text-left cursor-pointer"
                >
                  {preset.slice(0, 48)}…
                </button>
              ))}
            </div>
          </div>

          {/* Screen context inspiration (Optional) */}
          {screenContextB64 && (
            <div className="flex items-center gap-2 p-2.5 rounded-xl bg-white/[0.03] border border-white/10">
              <input
                type="checkbox"
                id="includeScreenMusic"
                checked={includeImage}
                onChange={(e) => setIncludeImage(e.target.checked)}
                className="rounded accent-[#ae86ff] cursor-pointer"
              />
              <label
                htmlFor="includeScreenMusic"
                className="text-[11px] text-white/80 cursor-pointer select-none"
              >
                Feed current screen snapshot into Lyria as visual inspiration
              </label>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-200 text-xs">
              {error}
            </div>
          )}

          {/* Generating Loading Animation */}
          {isLoading && (
            <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 flex flex-col items-center justify-center gap-3">
              <div className="flex items-center gap-1.5 h-10">
                {[15, 30, 45, 60, 40, 20, 50, 70, 35, 60, 25].map((h, i) => (
                  <span
                    key={i}
                    className={`w-1.5 rounded-full animate-pulse ${
                      isRikka ? "bg-[#d050e8]" : "bg-[#38BDF8]"
                    }`}
                    style={{
                      height: `${h}%`,
                      animationDelay: `${i * 90}ms`,
                      animationDuration: "800ms",
                    }}
                  />
                ))}
              </div>
              <p className="text-xs font-semibold tracking-wide text-white animate-pulse">
                {isRikka
                  ? "Transcribing forbidden celestial harmonies with Lyria…"
                  : `Generating audio stream using ${
                      duration === "clip" ? "lyria-3-clip-preview" : "lyria-3-pro-preview"
                    }…`}
              </p>
            </div>
          )}

          {/* Result Player */}
          {generatedMusic && !isLoading && (
            <div className="space-y-3">
              <AudioPlayerWidget music={generatedMusic} mode={mode} />

              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={handleSendToChat}
                  className={`flex items-center gap-1.5 px-4 py-1.5 rounded-lg font-semibold text-xs text-white shadow-md transition-all cursor-pointer ${
                    isRikka
                      ? "bg-gradient-to-r from-[#7c4dff] to-[#d050e8] hover:scale-105"
                      : "bg-gradient-to-r from-[#0071E3] to-[#38BDF8] hover:scale-105"
                  }`}
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>Send Track to Chat</span>
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg border border-white/15 text-white/70 hover:text-white hover:bg-white/5 text-xs transition-colors cursor-pointer"
          >
            Close
          </button>

          <button
            type="button"
            onClick={handleGenerate}
            disabled={!prompt.trim() || isLoading}
            className={`flex items-center gap-1.5 px-5 py-1.5 rounded-lg font-semibold text-xs text-white shadow-md transition-all cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${
              isRikka
                ? "bg-gradient-to-r from-[#7c4dff] to-[#d050e8] hover:from-[#ae86ff] hover:to-[#e879f9]"
                : "bg-gradient-to-r from-[#0071E3] to-[#0056B3] hover:from-[#38BDF8] hover:to-[#0071E3]"
            }`}
          >
            {isLoading ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Composing…</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Generate Music</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
