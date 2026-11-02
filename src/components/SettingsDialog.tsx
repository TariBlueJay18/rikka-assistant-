import React, { useState } from "react";
import { Config, ThemeMode, BackendEngine, ModelTier, GroundingMode } from "../types";
import { DEFAULT_RIKKA_PROMPT, DEFAULT_NORMAL_PROMPT } from "../config";
import { X, Eye, EyeOff, RotateCcw, Brain, Globe, Shield, Sparkles } from "lucide-react";

interface SettingsDialogProps {
  config: Config;
  isOpen: boolean;
  onClose: () => void;
  onSave: (newConfig: Config) => void;
}

export const SettingsDialog: React.FC<SettingsDialogProps> = ({
  config,
  isOpen,
  onClose,
  onSave,
}) => {
  if (!isOpen) return null;

  const isRikka = config.mode === "rikka";

  const [form, setForm] = useState<Config>({ ...config });
  const [showKey, setShowKey] = useState(false);
  const [activePromptTab, setActivePromptTab] = useState<"rikka" | "normal" | "custom">(
    form.mode === "rikka" ? "rikka" : "normal"
  );

  const handleSave = () => {
    onSave(form);
    onClose();
  };

  const resetPrompt = (type: "rikka" | "normal") => {
    if (type === "rikka") {
      setForm((prev) => ({ ...prev, system_prompt_rikka: DEFAULT_RIKKA_PROMPT }));
    } else {
      setForm((prev) => ({ ...prev, system_prompt_normal: DEFAULT_NORMAL_PROMPT }));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div
        className={`w-full max-w-lg max-h-[90vh] flex flex-col rounded-2xl border shadow-2xl overflow-hidden transition-all ${
          isRikka
            ? "bg-[#0e0c24] border-[rgba(124,77,255,0.38)] text-[#ede7f6]"
            : "bg-gradient-to-b from-[#181c26]/95 to-[#0e1018]/98 border-white/20 text-white"
        }`}
      >
        {/* Header bar */}
        <div className="px-5 py-3.5 flex items-center justify-between border-b border-white/10">
          <h2 className="text-sm font-bold flex items-center gap-2 text-[#38BDF8]">
            <span>⚙</span>
            <span>Settings & Model Configuration</span>
          </h2>
          <button
            onClick={onClose}
            className="w-7 h-7 flex items-center justify-center rounded-lg text-white/50 hover:bg-white/10 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content body */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5 text-xs">
          {/* Appearance & Personality */}
          <div>
            <label className="text-[11px] font-bold tracking-wider uppercase text-[#ae86ff] mb-2 block">
              APPEARANCE & PERSONALITY
            </label>
            <div className="flex items-center justify-between gap-4">
              <span className="text-white/80">Active Mode:</span>
              <select
                value={form.mode}
                onChange={(e) =>
                  setForm({ ...form, mode: e.target.value as ThemeMode })
                }
                className="bg-white/5 border border-white/15 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-[#38BDF8]"
              >
                <option value="rikka" className="bg-[#0e0c24] text-white">
                  ✦  Rikka (Chunibyo Magic)
                </option>
                <option value="normal" className="bg-[#0e0c24] text-white">
                  🫧  AI Assistant Mode (Frosted Acrylic)
                </option>
              </select>
            </div>
          </div>

          {/* Specialized System Role Instruction */}
          <div className="pt-2 border-t border-white/10">
            <label className="text-[11px] font-bold tracking-wider uppercase text-[#ae86ff] mb-2 block">
              SPECIALIZED SYSTEM ROLE
            </label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: "persona", label: "Pure Persona (Default)", desc: "100% in-character voice" },
                { id: "coder", label: "Code Architect", desc: "Technical & programming focus" },
                { id: "scholar", label: "Research Scholar", desc: "Fact-dense & grounded answers" },
                { id: "bard", label: "Creative Bard", desc: "Sonic storytelling & lyrics" },
              ].map((role) => (
                <button
                  key={role.id}
                  type="button"
                  onClick={() => setForm({ ...form, system_role: role.id as any })}
                  className={`p-2.5 rounded-xl border text-left transition-all cursor-pointer ${
                    form.system_role === role.id
                      ? isRikka
                        ? "bg-[#7c4dff]/25 border-[#ae86ff] text-white"
                        : "bg-[#0071E3]/25 border-[#38BDF8] text-white"
                      : "bg-white/[0.03] border-white/10 text-white/60 hover:bg-white/10"
                  }`}
                >
                  <p className="font-semibold text-xs text-white">{role.label}</p>
                  <p className="text-[10px] text-white/50">{role.desc}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Model Routing & Grounding */}
          <div className="pt-2 border-t border-white/10">
            <label className="text-[11px] font-bold tracking-wider uppercase text-[#ae86ff] mb-2 block">
              MODEL ROUTING & GROUNDING
            </label>

            <div className="space-y-3">
              <div className="flex items-center justify-between gap-4">
                <span className="text-white/80">Default Task Tier:</span>
                <select
                  value={form.modelTier}
                  onChange={(e) =>
                    setForm({ ...form, modelTier: e.target.value as ModelTier })
                  }
                  className="bg-white/5 border border-white/15 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-[#38BDF8]"
                >
                  <option value="fast" className="bg-[#0e0c24]">
                    ⚡ Fast (gemini-3.1-flash-lite)
                  </option>
                  <option value="general" className="bg-[#0e0c24]">
                    ✦ General (gemini-3.8-flash)
                  </option>
                  <option value="complex" className="bg-[#0e0c24]">
                    🧠 Complex (gemini-4-argon)
                  </option>
                </select>
              </div>

              <div className="flex items-center justify-between gap-4">
                <span className="text-white/80">Grounding Policy:</span>
                <select
                  value={form.groundingMode}
                  onChange={(e) =>
                    setForm({ ...form, groundingMode: e.target.value as GroundingMode })
                  }
                  className="bg-white/5 border border-white/15 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-[#38BDF8]"
                >
                  <option value="auto" className="bg-[#0e0c24]">
                    Auto-detect (Search & Maps where relevant)
                  </option>
                  <option value="search" className="bg-[#0e0c24]">
                    Always Google Search Grounding
                  </option>
                  <option value="maps" className="bg-[#0e0c24]">
                    Always Google Maps Grounding
                  </option>
                  <option value="none" className="bg-[#0e0c24]">
                    Grounding Disabled
                  </option>
                </select>
              </div>
            </div>
          </div>

          {/* Backend Engine */}
          <div className="pt-2 border-t border-white/10">
            <label className="text-[11px] font-bold tracking-wider uppercase text-[#ae86ff] mb-2 block">
              BACKEND ENGINE
            </label>
            <div className="flex items-center justify-between gap-4 mb-3">
              <span className="text-white/80">Active Engine:</span>
              <select
                value={form.backend}
                onChange={(e) =>
                  setForm({ ...form, backend: e.target.value as BackendEngine })
                }
                className="bg-white/5 border border-white/15 rounded-lg px-3 py-1.5 text-xs text-white outline-none focus:border-[#38BDF8]"
              >
                <option value="gemini" className="bg-[#0e0c24] text-white">
                  Cloud (Google Gemini)
                </option>
                <option value="ollama" className="bg-[#0e0c24] text-white">
                  Local (Ollama)
                </option>
              </select>
            </div>

            {/* Local Ollama Configuration */}
            {form.backend === "ollama" && (
              <div className="space-y-3 p-3 rounded-xl bg-white/[0.03] border border-white/10">
                <div>
                  <label className="text-[11px] text-white/70 block mb-1">
                    Ollama Base URL
                  </label>
                  <input
                    type="text"
                    value={form.ollama_base_url}
                    onChange={(e) =>
                      setForm({ ...form, ollama_base_url: e.target.value })
                    }
                    placeholder="http://localhost:11434"
                    className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-xs text-white placeholder-white/30 outline-none focus:border-[#38BDF8] font-mono"
                  />
                </div>

                <div>
                  <label className="text-[11px] text-white/70 block mb-1">
                    Ollama Model Name
                  </label>
                  <input
                    type="text"
                    value={form.ollama_model}
                    onChange={(e) =>
                      setForm({ ...form, ollama_model: e.target.value })
                    }
                    placeholder="llama3.2"
                    className="w-full bg-white/5 border border-white/15 rounded-lg px-3 py-2 text-xs text-white placeholder-white/30 outline-none focus:border-[#38BDF8] font-mono"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Persona System Prompts */}
          <div className="pt-2 border-t border-white/10">
            <div className="flex items-center justify-between mb-2">
              <label className="text-[11px] font-bold tracking-wider uppercase text-[#ae86ff]">
                PERSONA PROMPTS
              </label>
              {activePromptTab !== "custom" && (
                <button
                  type="button"
                  onClick={() => resetPrompt(activePromptTab as "rikka" | "normal")}
                  className="text-[10px] text-white/50 hover:text-white flex items-center gap-1 cursor-pointer"
                >
                  <RotateCcw className="w-3 h-3" />
                  <span>Reset Default</span>
                </button>
              )}
            </div>

            {/* Prompt Tabs */}
            <div className="flex gap-1 mb-2 border-b border-white/10 pb-1">
              <button
                type="button"
                onClick={() => setActivePromptTab("rikka")}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
                  activePromptTab === "rikka"
                    ? "bg-[#7c4dff]/30 text-[#e879f9] border border-[#7c4dff]/50"
                    : "text-white/60 hover:text-white"
                }`}
              >
                Rikka Chuunibyo
              </button>
              <button
                type="button"
                onClick={() => setActivePromptTab("normal")}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
                  activePromptTab === "normal"
                    ? "bg-[#38BDF8]/20 text-[#38BDF8] border border-[#38BDF8]/40"
                    : "text-white/60 hover:text-white"
                }`}
              >
                AI Assistant
              </button>
              <button
                type="button"
                onClick={() => setActivePromptTab("custom")}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all cursor-pointer ${
                  activePromptTab === "custom"
                    ? "bg-white/15 text-white border border-white/30"
                    : "text-white/60 hover:text-white"
                }`}
              >
                Custom Override
              </button>
            </div>

            {activePromptTab === "rikka" && (
              <textarea
                value={form.system_prompt_rikka}
                onChange={(e) =>
                  setForm({ ...form, system_prompt_rikka: e.target.value })
                }
                rows={4}
                className="w-full bg-white/5 border border-white/15 rounded-lg p-2.5 text-xs text-white leading-relaxed resize-none outline-none focus:border-[#38BDF8]"
              />
            )}

            {activePromptTab === "normal" && (
              <textarea
                value={form.system_prompt_normal}
                onChange={(e) =>
                  setForm({ ...form, system_prompt_normal: e.target.value })
                }
                rows={4}
                className="w-full bg-white/5 border border-white/15 rounded-lg p-2.5 text-xs text-white leading-relaxed resize-none outline-none focus:border-[#38BDF8]"
              />
            )}

            {activePromptTab === "custom" && (
              <div>
                <textarea
                  value={form.custom_system_prompt}
                  onChange={(e) =>
                    setForm({ ...form, custom_system_prompt: e.target.value })
                  }
                  rows={4}
                  placeholder="Enter a custom persona prompt (leave blank to use the active mode's prompt above)..."
                  className="w-full bg-white/5 border border-white/15 rounded-lg p-2.5 text-xs text-white placeholder-white/30 leading-relaxed resize-none outline-none focus:border-[#38BDF8]"
                />
              </div>
            )}
          </div>
        </div>

        {/* Footer actions */}
        <div className="px-5 py-3 border-t border-white/10 flex items-center justify-end gap-2 bg-black/20">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg border border-white/15 text-white/70 hover:text-white hover:bg-white/5 text-xs transition-colors cursor-pointer"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className={`px-5 py-1.5 rounded-lg font-semibold text-xs text-white shadow-md transition-all cursor-pointer ${
              isRikka
                ? "bg-gradient-to-r from-[#7c4dff] to-[#d050e8] hover:from-[#ae86ff] hover:to-[#e879f9]"
                : "bg-gradient-to-r from-[#0071E3] to-[#0056B3] hover:from-[#38BDF8] hover:to-[#0071E3]"
            }`}
          >
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
};
