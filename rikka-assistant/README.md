# Rikka Assistant 🔮

A frameless, floating desktop AI assistant with a Rikka Takanashi persona.
Streams responses from **Ollama** (local) or **Gemini** (cloud), with live system stats and quick-launch actions.

---

## Project Structure

```
rikka-assistant/
├── main.py               # Entry point
├── config.py             # Settings dataclass (persisted to ~/.rikka_assistant/config.json)
├── llm_engine.py         # QThread-based streaming LLM client (Ollama + Gemini)
├── tools.py              # System stats (psutil) + app launcher
├── requirements.txt
├── assets/               # Optional PNG avatars: idle.png, thinking.png, speaking.png
└── gui/
    ├── __init__.py
    ├── styles.py          # Full QSS stylesheet + colour palette
    ├── avatar_widget.py   # Circular avatar with state switching
    ├── chat_widget.py     # Scrollable chat with streaming bubbles
    ├── input_bar.py       # Auto-expanding input + action buttons
    ├── settings_dialog.py # Modal settings panel
    └── main_window.py     # Frameless, draggable, always-on-top window
```

---

## Quick Start

### 1 — Create a virtual environment

```bash
cd C:\Users\negoe\projects\rikka-assistant

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

> **Optional GPU stats** (NVIDIA only):
> ```bash
> pip install GPUtil
> ```
> Then uncomment the `GPUtil` line in `requirements.txt`.

### 3 — Choose your LLM backend

#### Option A — Ollama (recommended for local use)

1. Install Ollama from <https://ollama.com>
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Start the server:
   ```bash
   ollama serve
   ```

#### Option B — Gemini (cloud)

1. Get an API key from <https://aistudio.google.com/app/apikey>
2. Open the app → click ⚙ Settings → select **gemini** backend → paste your key.

### 4 — Run

```bash
python main.py
```

---

## Custom Avatars

Drop three PNG images into `assets/` to replace the painted fallback icons:

| File | State |
|---|---|
| `assets/idle.png` | Default / waiting |
| `assets/thinking.png` | Generating response |
| `assets/speaking.png` | Streaming tokens |

Recommended size: **128 × 128 px** or larger (the widget scales them down).

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| **Enter** | Send message |
| **Shift + Enter** | Insert newline |

---

## Configuration

Settings are stored in `~/.rikka_assistant/config.json` and can be edited via ⚙ Settings in-app.

Key fields:

| Field | Default | Description |
|---|---|---|
| `backend` | `"ollama"` | `"ollama"` or `"gemini"` |
| `ollama_model` | `"llama3.2"` | Any model installed in Ollama |
| `gemini_model` | `"gemini-2.0-flash"` | Gemini model name |
| `max_history_turns` | `20` | Exchange pairs kept in context |
| `system_prompt` | Rikka persona | Override character behaviour |

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| *"Cannot reach Ollama"* | Run `ollama serve` first |
| *"Gemini API key not configured"* | Open ⚙ Settings and paste your key |
| Window appears behind other apps | Remove `WindowStaysOnTopHint` in `main_window.py` |
| Avatar shows emoji instead of image | Add PNG files to `assets/` |
| Transparent background not working | Ensure your compositor supports transparency (Linux: enable compositing) |
