# Rikka Assistant 🔮

A sleek floating desktop-style AI assistant with **Rikka Takanashi (Chunibyo Magic)** and **Frosted Acrylic AI Assistant** modes.
Rewritten from Python/PyQt6 to a production-grade full-stack **React + Express** application, preserving all core features and business logic.

---

## Features

- **Dual Personas & Themes**:
  - **Rikka Mode**: Authentic circular portrait of Rikka Takanashi, live animated rotating Arcane Magic Circle / Tyrant's Eye rune aura, golden eye-flare during generation, and Chunibyo dramatic responses.
  - **AI Assistant Mode**: Frosted Matte Acrylic aesthetic, diffuse satin luminescence, Siri-inspired rotating iridescent aura perimeter ring, and clear concise responses.
- **Google Pixel-Inspired Fluid Wave Transition**:
  - Seamless liquid ripple wave expanding across the interface when switching between modes.
- **Dual Engine Backends**:
  - **Cloud (Google Gemini)**: Real-time streaming with modern `@google/genai` TypeScript SDK (`gemini-3.8-flash`).
  - **Local (Ollama)**: Connects to local Ollama endpoints (e.g. `http://localhost:11434` with `llama3.2`).
  - 1-Click quick toggle with breathing LED pulse halo indicator badge.
- **Multimodal Screen Context**:
  - Real browser screen capture via `navigator.mediaDevices.getDisplayMedia`, downscaled and attached as image context for vision queries.
  - Privacy toggle to enable or disable with one click.
- **System & Web Tools**:
  - Direct quick action intents: `search for ...` / `google ...`, `open youtube`, `open github`, `open reddit`, etc.
  - Privacy toggle to disable/enable tool executions.
  - Hardware vitals snapshot: live CPU usage, logical/physical cores, RAM utilization, disk, and battery statistics.
- **Full Settings Panel**:
  - Configure models, Ollama base URL, Gemini API keys, and custom system prompt overrides.
  - Settings persisted across sessions in browser storage.

---

## Project Structure

```
├── server.ts              # Full-stack Express backend (Gemini API & Ollama proxy + system metrics)
├── vite.config.ts         # Vite configuration with Tailwind CSS
├── index.html             # HTML entry point with synchronized metadata
├── public/
│   └── assets/            # Rikka portrait and avatar image assets
└── src/
    ├── main.tsx           # React DOM root entry
    ├── App.tsx            # Main application layout, state & streaming coordinator
    ├── types.ts           # TypeScript interfaces (Config, ChatMessage, AssistantState, etc.)
    ├── config.ts          # Default settings, prompts & localStorage persistence
    ├── tools.ts           # System intent matcher and hardware metrics formatter
    ├── index.css          # Theme design tokens, animations & scrollbar styles
    ├── utils/
    │   └── screenCapture.ts # Browser screen capture helper with JPEG downscaler
    └── components/
        ├── TitleBar.tsx              # Draggable title, quick backend & mode toggles, controls
        ├── AvatarRow.tsx             # Animated circular avatar with rune aura / Siri ring & LED badge
        ├── ChatWidget.tsx            # Message bubbles (User, Bot, System, Error), code & streaming
        ├── InputBar.tsx              # Auto-expanding textarea, privacy pills & action buttons
        ├── SettingsDialog.tsx        # Modal panel for engine, models, API keys & custom prompts
        └── WaveTransitionOverlay.tsx # Google Pixel-style liquid wave ripple animation
```

---

## Development

```bash
# Install dependencies
npm install

# Start dev server on http://localhost:3000
npm run dev

# Build for production
npm run build
```
