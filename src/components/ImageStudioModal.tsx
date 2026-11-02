import React, { useState } from "react";
import { ThemeMode, GeneratedImage } from "../types";
import { X, Sparkles, Image as ImageIcon, Download, Send, Upload, RefreshCw } from "lucide-react";

interface ImageStudioModalProps {
  isOpen: boolean;
  mode: ThemeMode;
  onClose: () => void;
  onImageCreated: (image: GeneratedImage) => void;
  screenContextB64?: string | null;
}

export const ImageStudioModal: React.FC<ImageStudioModalProps> = ({
  isOpen,
  mode,
  onClose,
  onImageCreated,
  screenContextB64,
}) => {
  if (!isOpen) return null;

  const isRikka = mode === "rikka";

  const [prompt, setPrompt] = useState("");
  const [aspectRatio, setAspectRatio] = useState("1:1");
  const [imageBase64, setImageBase64] = useState<string | null>(screenContextB64 || null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedResult, setGeneratedResult] = useState<GeneratedImage | null>(null);

  const presets = isRikka
    ? [
        "Rikka Takanashi unleashing the Tyrant's Eye in an arcane magical storm, anime style",
        "Glowing violet magical summoning circle with glowing runes and dark flames",
        "A wicked grimoire sealed with golden chains and celestial sigils",
        "Dramatic anime gothic high school girl casting a forbidden void spell",
      ]
    : [
        "Futuristic holographic AI assistant interface with glowing frosted glass dials",
        "Minimalist aesthetic geometric prism floating in twilight neon atmosphere",
        "Cyberpunk workstation with frosted acrylic monitors and ambient blue backlights",
        "High-tech spherical AI core pulsing with iridescent particle streams",
      ];

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const base64 = result.replace(/^data:image\/[a-z]+;base64,/, "");
      setImageBase64(base64);
    };
    reader.readAsDataURL(file);
  };

  const handleGenerate = async () => {
    if (!prompt.trim() || isLoading) return;

    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/image/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          aspectRatio,
          imageBase64: imageBase64 || undefined,
        }),
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || "Failed to generate image");
      }

      const img: GeneratedImage = {
        imageUrl: data.imageUrl,
        prompt: prompt.trim(),
        text: data.text,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        aspectRatio,
        isEdit: !!imageBase64,
      };

      setGeneratedResult(img);
    } catch (err: any) {
      setError(err.message || "Failed to generate image.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendToChat = () => {
    if (generatedResult) {
      onImageCreated(generatedResult);
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
            <Sparkles className="w-4 h-4 text-[#e879f9]" />
            <h2 className="text-sm font-bold tracking-wide">
              {isRikka ? "Arcane Image Alchemist" : "Image Synthesis Studio"}
            </h2>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-white/10 font-mono text-white/70">
              gemini-nano-banana-2.1
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
          {/* Prompt input */}
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-[#ae86ff] mb-1.5 block">
              {imageBase64 ? "Edit Instruction Prompt" : "Image Description Prompt"}
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
              placeholder={
                imageBase64
                  ? "e.g. Add glowing neon runes and a cosmic purple storm around the subject..."
                  : "e.g. Rikka summoning the dark magical realm in Tokyo night rain, ultra high detail..."
              }
              className="w-full bg-white/5 border border-white/15 rounded-xl p-3 text-xs text-white placeholder-white/30 resize-none outline-none focus:border-[#38BDF8] leading-relaxed"
            />
          </div>

          {/* Quick Preset Ideas */}
          <div>
            <p className="text-[10px] text-white/60 mb-1.5 font-medium">
              Magical Inspiration Presets:
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

          {/* Image Edit Source (Optional) */}
          <div className="p-3 rounded-xl bg-white/[0.03] border border-white/10 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-white/80">
                Image Source (Optional for Image-to-Image editing):
              </span>
              {imageBase64 && (
                <button
                  type="button"
                  onClick={() => setImageBase64(null)}
                  className="text-[10px] text-red-400 hover:underline"
                >
                  Remove Image
                </button>
              )}
            </div>

            {imageBase64 ? (
              <div className="relative rounded-lg overflow-hidden border border-white/20 max-h-32 bg-black/40 flex items-center justify-center">
                <img
                  src={`data:image/png;base64,${imageBase64}`}
                  alt="Edit source"
                  className="max-h-32 object-contain"
                />
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/15 bg-white/5 hover:bg-white/10 text-white text-[11px] font-semibold cursor-pointer transition-colors">
                  <Upload className="w-3.5 h-3.5" />
                  <span>Upload Image to Edit</span>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>

                {screenContextB64 && (
                  <button
                    type="button"
                    onClick={() => setImageBase64(screenContextB64)}
                    className="px-3 py-1.5 rounded-lg border border-white/15 bg-white/5 hover:bg-white/10 text-white text-[11px] font-semibold cursor-pointer transition-colors"
                  >
                    Use Screen Capture
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Aspect Ratio Selector */}
          <div>
            <label className="text-[11px] font-bold uppercase tracking-wider text-[#ae86ff] mb-1.5 block">
              Aspect Ratio
            </label>
            <div className="grid grid-cols-5 gap-2">
              {["1:1", "16:9", "9:16", "4:3", "3:4"].map((ratio) => (
                <button
                  key={ratio}
                  type="button"
                  onClick={() => setAspectRatio(ratio)}
                  className={`py-1.5 rounded-lg text-center font-mono text-xs border transition-all cursor-pointer ${
                    aspectRatio === ratio
                      ? isRikka
                        ? "bg-[#7c4dff]/40 border-[#ae86ff] text-white shadow-md"
                        : "bg-[#0071E3]/40 border-[#38BDF8] text-white shadow-md"
                      : "bg-white/[0.04] border-white/10 text-white/70 hover:bg-white/10"
                  }`}
                >
                  {ratio}
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-200 text-xs">
              {error}
            </div>
          )}

          {/* Summoning Loading State */}
          {isLoading && (
            <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/10 flex flex-col items-center justify-center gap-3">
              <div className="relative w-16 h-16 flex items-center justify-center">
                <div
                  className={`absolute inset-0 rounded-full border-2 border-dashed animate-spin-fast ${
                    isRikka ? "border-[#d050e8]" : "border-[#38BDF8]"
                  }`}
                />
                <Sparkles className="w-6 h-6 animate-pulse text-[#e879f9]" />
              </div>
              <p className="text-xs font-semibold tracking-wide text-white animate-pulse">
                {isRikka
                  ? "Weaving celestial pixels through Tyrant's Eye…"
                  : "Synthesizing high-fidelity image with gemini-nano-banana-2.1…"}
              </p>
            </div>
          )}

          {/* Generated Result Preview */}
          {generatedResult && !isLoading && (
            <div className="space-y-2 p-3 rounded-2xl bg-black/30 border border-white/15">
              <div className="rounded-xl overflow-hidden shadow-2xl border border-white/20 bg-black/60">
                <img
                  src={generatedResult.imageUrl}
                  alt={generatedResult.prompt}
                  className="w-full h-auto object-cover max-h-72"
                />
              </div>

              {generatedResult.text && (
                <p className="text-[11px] text-white/80 italic leading-relaxed">
                  "{generatedResult.text}"
                </p>
              )}

              <div className="flex items-center justify-between pt-1">
                <a
                  href={generatedResult.imageUrl}
                  download={`rikka-art-${Date.now()}.png`}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-white/15 text-white/80 hover:text-white hover:bg-white/10 transition-colors text-xs font-medium cursor-pointer"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Image</span>
                </a>

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
                  <span>Send to Chat</span>
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
                <span>Conjuring…</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>{imageBase64 ? "Transform Image" : "Generate Artwork"}</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
