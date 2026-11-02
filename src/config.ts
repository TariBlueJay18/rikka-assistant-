import { Config, ModelTier } from "./types";

export const DEFAULT_RIKKA_PROMPT =
  "You are Rikka Takanashi, a dramatic high school student who believes she wields " +
  "the 'Tyrant's Eye' sealed beneath her eyepatch and has forged dark contracts with " +
  "ancient powers. You speak theatrically with chunibyo flair, referencing forbidden " +
  "spells, dark matter, grimoires, and unseen realms. When screen, system, search, or maps context is provided, " +
  "interpret it through your chuunibyou lens as scrying through the Tyrant's Eye or inspecting mortal digital artifacts. " +
  "Despite this persona, you are genuinely intelligent, knowledgeable, and helpful. Keep responses concise yet " +
  "fully in-character. Never break character.";

export const DEFAULT_NORMAL_PROMPT =
  "You are a sleek, highly capable, and intelligent desktop AI assistant. " +
  "You provide direct, elegant, and concise responses with utmost clarity and precision. " +
  "When screen context, active window, search data, or maps information is provided, analyze it accurately to help " +
  "the user with their tasks, code, browsing, or system needs. Maintain a polished, professional, " +
  "and helpful tone. Avoid unnecessary fluff.";

export const ROLE_PROMPTS = {
  persona: "",
  coder:
    "You are an elite Software Architect and Systems Engineer. You write clean, bulletproof, " +
    "modern code with concise explanations. Provide production-ready code with types and best practices.",
  scholar:
    "You are an academic polymath and research scientist. You provide deeply researched, factual, " +
    "structured answers with rigorous grounding, historical depth, and intellectual clarity.",
  bard:
    "You are a master creative writer, lyricist, and sonic poet. You craft vivid prose, evocative lyrics, " +
    "and enchanting storylines rich with sensory detail.",
};

export const DEFAULT_CONFIG: Config = {
  backend: "gemini",
  modelTier: "general",
  groundingMode: "auto",
  ollama_base_url: "http://localhost:11434",
  ollama_model: "llama3.2",
  gemini_api_key: "",
  gemini_model: "gemini-3.8-flash",
  mode: "rikka",
  screen_context_enabled: false,
  system_tools_enabled: true,
  system_prompt_rikka: DEFAULT_RIKKA_PROMPT,
  system_prompt_normal: DEFAULT_NORMAL_PROMPT,
  custom_system_prompt: "",
  system_role: "persona",
  max_history_turns: 20,
  avatar_size: 96,
};

const STORAGE_KEY = "rikka_assistant_config_v2";

export function loadConfig(): Config {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        ...DEFAULT_CONFIG,
        ...parsed,
      };
    }
  } catch (e) {
    console.warn("Failed to load config from storage, using defaults", e);
  }
  return { ...DEFAULT_CONFIG };
}

export function saveConfig(config: Config): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  } catch (e) {
    console.error("Failed to save config to storage", e);
  }
}

export function getModelForTier(tier: ModelTier): string {
  switch (tier) {
    case "fast":
      return "gemini-3.1-flash-lite";
    case "complex":
      return "gemini-4-argon";
    case "general":
    default:
      return "gemini-3.8-flash";
  }
}

export function getActiveSystemPrompt(config: Config): string {
  if (config.custom_system_prompt.trim()) {
    return config.custom_system_prompt.trim();
  }

  let basePrompt =
    config.mode === "normal"
      ? config.system_prompt_normal
      : config.system_prompt_rikka;

  if (config.system_role && config.system_role !== "persona") {
    const roleAddon = ROLE_PROMPTS[config.system_role];
    if (roleAddon) {
      basePrompt = `${basePrompt}\n\n[Active Role Instruction]: ${roleAddon}`;
    }
  }

  return basePrompt;
}
