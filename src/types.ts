export type AssistantState = "idle" | "thinking" | "speaking";
export type ThemeMode = "rikka" | "normal";
export type BackendEngine = "ollama" | "gemini";
export type ModelTier = "fast" | "general" | "complex";
export type GroundingMode = "none" | "search" | "maps" | "auto";

export interface GroundingSource {
  type: "web" | "maps";
  title: string;
  url: string;
  snippet?: string;
}

export interface GeneratedMusic {
  audioUrl: string;
  lyrics?: string;
  prompt: string;
  model: string;
  timestamp: string;
}

export interface GeneratedImage {
  imageUrl: string;
  prompt: string;
  text?: string;
  timestamp: string;
  aspectRatio: string;
  isEdit?: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "bot" | "system" | "error";
  text: string;
  timestamp: string;
  isStreaming?: boolean;
  imagePreview?: string;
  activeWindow?: string;
  modelUsed?: string;
  groundingSources?: GroundingSource[];
  musicAttachment?: GeneratedMusic;
  imageAttachment?: GeneratedImage;
}

export interface Config {
  backend: BackendEngine;
  modelTier: ModelTier;
  groundingMode: GroundingMode;
  ollama_base_url: string;
  ollama_model: string;
  gemini_api_key: string;
  gemini_model: string;
  mode: ThemeMode;
  screen_context_enabled: boolean;
  system_tools_enabled: boolean;
  system_prompt_rikka: string;
  system_prompt_normal: string;
  custom_system_prompt: string;
  system_role: "persona" | "coder" | "scholar" | "bard";
  max_history_turns: number;
  avatar_size: number;
}

export interface SystemStats {
  cpu_percent: number;
  cpu_count_logical: number;
  cpu_count_physical: number;
  ram_total_gb: number;
  ram_used_gb: number;
  ram_percent: number;
  disk_total_gb?: number;
  disk_used_gb?: number;
  disk_percent?: number;
  battery_percent?: number;
  battery_plugged?: boolean;
  platform?: string;
  hostname?: string;
  uptime_hours?: number;
}
