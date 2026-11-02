"""
Application-wide configuration, persisted to disk as JSON.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


CONFIG_PATH = Path.home() / ".rikka_assistant" / "config.json"
ASSETS_DIR = Path(__file__).parent / "assets"

DEFAULT_RIKKA_PROMPT = (
    "You are Rikka Takanashi, a dramatic high school student who believes she wields "
    "the 'Tyrant's Eye' sealed beneath her eyepatch and has forged dark contracts with "
    "ancient powers. You speak theatrically with chunibyo flair, referencing forbidden "
    "spells and unseen realms. When screen or system context is provided, interpret it through "
    "your chuunibyou lens as scrying through the Tyrant's Eye or inspecting mortal digital artifacts. "
    "Despite this persona, you are genuinely intelligent and helpful. Keep responses concise yet "
    "fully in-character. Never break character."
)

DEFAULT_NORMAL_PROMPT = (
    "You are a sleek, highly capable, and intelligent desktop AI assistant. "
    "You provide direct, elegant, and concise responses with utmost clarity and precision. "
    "When screen context or active window information is provided, analyze it accurately to help "
    "the user with their tasks, code, browsing, or system needs. Maintain a polished, professional, "
    "and helpful tone. Avoid unnecessary fluff."
)


@dataclass
class Config:
    """All user-configurable settings with sensible defaults."""

    # Backend selection: "ollama" | "gemini"
    backend: str = "ollama"

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout: float = 120.0

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Window geometry (persisted across restarts)
    window_x: int = 80
    window_y: int = 80
    window_width: int = 420
    window_height: int = 680

    # Avatar display size in pixels
    avatar_size: int = 96

    # Maximum conversation exchange pairs kept in memory
    max_history_turns: int = 20

    # Mode: "rikka" (Chunibyo Magic) | "normal" (AI Assistant Mode)
    mode: str = "rikka"

    # Privacy & System Access Toggles
    screen_context_enabled: bool = False
    system_tools_enabled: bool = True

    # Persona prompts
    system_prompt_rikka: str = DEFAULT_RIKKA_PROMPT
    system_prompt_normal: str = DEFAULT_NORMAL_PROMPT
    custom_system_prompt: str = ""

    @property
    def system_prompt(self) -> str:
        """Dynamically return the active prompt for the chosen mode."""
        if self.custom_system_prompt.strip():
            return self.custom_system_prompt.strip()
        if self.mode == "normal":
            return self.system_prompt_normal
        return self.system_prompt_rikka

    @classmethod
    def load(cls) -> "Config":
        """Load from disk; silently fall back to defaults on any error."""
        if CONFIG_PATH.exists():
            try:
                with CONFIG_PATH.open(encoding="utf-8") as fh:
                    data = json.load(fh)
                if "theme_mode" in data and "mode" not in data:
                    data["mode"] = data.pop("theme_mode")
                if "system_prompt" in data and "system_prompt_rikka" not in data:
                    data["system_prompt_rikka"] = data.pop("system_prompt")
                valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
                return cls(**valid)
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        """Persist current settings to disk."""
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG_PATH.open("w", encoding="utf-8") as fh:
            data = asdict(self)
            data["theme_mode"] = self.mode
            data["system_prompt"] = self.system_prompt
            json.dump(data, fh, indent=2)
