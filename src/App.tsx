import React, { useState, useEffect, useRef } from "react";
import {
  AssistantState,
  ChatMessage,
  Config,
  ThemeMode,
  BackendEngine,
  ModelTier,
  GroundingMode,
  GeneratedMusic,
  GeneratedImage,
} from "./types";
import {
  loadConfig,
  saveConfig,
  getActiveSystemPrompt,
  getModelForTier,
} from "./config";
import { TitleBar } from "./components/TitleBar";
import { AvatarRow } from "./components/AvatarRow";
import { ChatWidget } from "./components/ChatWidget";
import { InputBar } from "./components/InputBar";
import { WaveTransitionOverlay } from "./components/WaveTransitionOverlay";
import { SettingsDialog } from "./components/SettingsDialog";
import { ImageStudioModal } from "./components/ImageStudioModal";
import { MusicStudioModal } from "./components/MusicStudioModal";
import { tryExecuteSystemIntent, formatStats } from "./tools";
import { captureScreenContext } from "./utils/screenCapture";
import { Maximize2 } from "lucide-react";

export const App: React.FC = () => {
  const [config, setConfig] = useState<Config>(() => loadConfig());
  const [assistantState, setAssistantState] = useState<AssistantState>("idle");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isImageStudioOpen, setIsImageStudioOpen] = useState(false);
  const [isMusicStudioOpen, setIsMusicStudioOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [latestScreenContext, setLatestScreenContext] = useState<string | null>(null);

  // Wave ripple transition state
  const [waveState, setWaveState] = useState<{
    origin: { x: number; y: number } | null;
    toMode: ThemeMode;
  } | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  // Initial greeting matching active mode and model
  useEffect(() => {
    const isCloud = config.backend === "gemini";
    const activeModel = isCloud
      ? getModelForTier(config.modelTier)
      : config.ollama_model;
    const engineType = isCloud ? "Cloud (Google Gemini)" : "Local (Ollama)";

    const initialText =
      config.mode === "normal"
        ? `✦  AI Assistant online.\nEngine: ${engineType} · ${activeModel}\nTools: Google Search, Maps Grounding, Image Alchemy (Nano Banana), & Lyria Music ready.`
        : `👁  The Tyrant's Eye is unsealed! The dark pact is forged.\nInvoking ${engineType} · ${activeModel}.\nForbidden Spells: Web Scrying, Realm Mapping, Image Alchemy, & Lyria Melodies active!`;

    setMessages([
      {
        id: "msg_init",
        role: "system",
        text: initialText,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ]);
  }, []);

  // Save config on changes
  useEffect(() => {
    saveConfig(config);
  }, [config]);

  const addSystemMessage = (text: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: "sys_" + Date.now(),
        role: "system",
        text,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ]);
  };

  const addErrorMessage = (text: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: "err_" + Date.now(),
        role: "error",
        text,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
      },
    ]);
  };

  // Toggle backend (Ollama <-> Gemini)
  const handleToggleBackend = () => {
    const newBackend: BackendEngine =
      config.backend === "ollama" ? "gemini" : "ollama";
    const newConfig = { ...config, backend: newBackend };
    setConfig(newConfig);

    const activeModel =
      newBackend === "ollama"
        ? newConfig.ollama_model
        : getModelForTier(newConfig.modelTier);

    if (newBackend === "gemini") {
      addSystemMessage(
        `☁  Switched to Cloud Engine: Google Gemini (${activeModel}).`
      );
    } else {
      addSystemMessage(
        `⚡  Switched to Local Engine: Ollama (${activeModel}) at ${newConfig.ollama_base_url}.`
      );
    }
  };

  // Cycle Model Tier (fast -> general -> complex)
  const handleCycleModelTier = () => {
    const tiers: ModelTier[] = ["fast", "general", "complex"];
    const nextIdx = (tiers.indexOf(config.modelTier) + 1) % tiers.length;
    const nextTier = tiers[nextIdx];
    setConfig((prev) => ({ ...prev, modelTier: nextTier }));

    const modelName = getModelForTier(nextTier);
    addSystemMessage(
      `⚡  Active Model Tier switched to: ${nextTier.toUpperCase()} (${modelName})`
    );
  };

  // Cycle Grounding Mode (auto -> search -> maps -> none)
  const handleToggleGrounding = () => {
    const modes: GroundingMode[] = ["auto", "search", "maps", "none"];
    const nextIdx = (modes.indexOf(config.groundingMode) + 1) % modes.length;
    const nextMode = modes[nextIdx];
    setConfig((prev) => ({ ...prev, groundingMode: nextMode }));

    const descriptions = {
      auto: "AUTO (Detects Google Search & Google Maps automatically)",
      search: "SEARCH ALWAYS (Google Search grounding enabled for web info)",
      maps: "MAPS ALWAYS (Google Maps grounding enabled for locations & places)",
      none: "DISABLED (No search or maps grounding)",
    };

    addSystemMessage(`🌐  Grounding Mode: ${descriptions[nextMode]}`);
  };

  // Mode toggle with Google Pixel-inspired wave transition
  const handleToggleMode = (originPoint?: { x: number; y: number }) => {
    const newMode: ThemeMode = config.mode === "rikka" ? "normal" : "rikka";

    setWaveState({
      origin: originPoint || { x: window.innerWidth / 2, y: 30 },
      toMode: newMode,
    });

    setConfig((prev) => ({ ...prev, mode: newMode }));

    if (newMode === "normal") {
      addSystemMessage(
        "🫧  AI Assistant Mode activated. Frosted Acrylic aesthetic online."
      );
    } else {
      addSystemMessage(
        "👁  The Tyrant's Eye awakens! Chunibyo Magic mode restored."
      );
    }
  };

  // Privacy toggles
  const handleToggleScreen = () => {
    const nextVal = !config.screen_context_enabled;
    setConfig((prev) => ({ ...prev, screen_context_enabled: nextVal }));
    if (nextVal) {
      addSystemMessage(
        "👁️  Screen Context: ENABLED. The assistant will capture your screen to assist with queries."
      );
    } else {
      addSystemMessage(
        "🔒  Screen Context: DISABLED for privacy. No screen data will be accessed."
      );
    }
  };

  const handleToggleSystem = () => {
    const nextVal = !config.system_tools_enabled;
    setConfig((prev) => ({ ...prev, system_tools_enabled: nextVal }));
    if (nextVal) {
      addSystemMessage(
        "🌐  System & Web Tools: ENABLED. Quick web search and app launching active."
      );
    } else {
      addSystemMessage("🔒  System & Web Tools: DISABLED.");
    }
  };

  // Hardware stats action
  const handleStats = async () => {
    const scanMsg =
      config.mode === "normal"
        ? "📡  Scanning system metrics…"
        : "📡  Scanning the ether for hardware vitals…";
    addSystemMessage(scanMsg);

    try {
      const res = await fetch("/api/system/stats");
      if (!res.ok) throw new Error("Failed to fetch system stats");
      const data = await res.json();
      addSystemMessage(formatStats(data));
    } catch (err: any) {
      addErrorMessage(`Failed to retrieve system statistics: ${err.message}`);
    }
  };

  // Clear conversation
  const handleClear = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setAssistantState("idle");
    setMessages([]);
    const clearMsg =
      config.mode === "normal"
        ? "🧹  Conversation cleared."
        : "🌀  History erased. The slate is void.";
    addSystemMessage(clearMsg);
  };

  // Handle Music Created from Studio Modal
  const handleMusicCreated = (music: GeneratedMusic) => {
    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages((prev) => [
      ...prev,
      {
        id: "msg_music_" + Date.now(),
        role: "bot",
        text: isRikka
          ? `🎵  I have summoned an arcane harmonic composition from the void: "${music.prompt}"`
          : `🎵  Synthesized musical piece via ${music.model}: "${music.prompt}"`,
        timestamp,
        musicAttachment: music,
      },
    ]);
  };

  // Handle Image Created from Studio Modal
  const handleImageCreated = (image: GeneratedImage) => {
    const timestamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    setMessages((prev) => [
      ...prev,
      {
        id: "msg_img_" + Date.now(),
        role: "bot",
        text: isRikka
          ? `🎨  Behold the manifestation scryed through the Tyrant's Eye: "${image.prompt}"`
          : `🎨  Generated image via gemini-nano-banana-2.1: "${image.prompt}"`,
        timestamp,
        imageAttachment: image,
      },
    ]);
  };

  // Handle user send message
  const handleSendMessage = async (text: string) => {
    const timestamp = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    // 1. Check quick system intent if system tools are enabled
    if (config.system_tools_enabled) {
      const intent = tryExecuteSystemIntent(text);
      if (intent && intent.handled) {
        setMessages((prev) => [
          ...prev,
          { id: "usr_" + Date.now(), role: "user", text, timestamp },
          {
            id: "sys_intent_" + Date.now(),
            role: "system",
            text: `⚡  ${intent.message}`,
            timestamp,
          },
        ]);
        return;
      }
    }

    // 2. Capture screen context if enabled
    let screenImageB64: string | null = null;
    let activeWinTitle = "";

    if (config.screen_context_enabled) {
      addSystemMessage("📸  Requesting screen context capture…");
      const screenResult = await captureScreenContext();
      screenImageB64 = screenResult.base64Jpeg;
      activeWinTitle = screenResult.activeWindow;

      if (screenImageB64) {
        setLatestScreenContext(screenImageB64);
        addSystemMessage(
          `📸  Screen context attached (${
            activeWinTitle ? `Active: "${activeWinTitle}"` : "Display captured"
          })`
        );
      }
    }

    // Append user message with attached screenshot preview if available
    const userMsgId = "usr_" + Date.now();
    const newUserMsg: ChatMessage = {
      id: userMsgId,
      role: "user",
      text,
      timestamp,
      imagePreview: screenImageB64 || undefined,
      activeWindow: activeWinTitle || undefined,
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setAssistantState("thinking");

    // Prepare bot message placeholder for streaming
    const botMsgId = "bot_" + Date.now();
    const activeModelName =
      config.backend === "gemini"
        ? getModelForTier(config.modelTier)
        : config.ollama_model;

    const newBotMsg: ChatMessage = {
      id: botMsgId,
      role: "bot",
      text: "",
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
      isStreaming: true,
      modelUsed: activeModelName,
    };

    // Prepare conversational history payload
    const systemPrompt = getActiveSystemPrompt(config);

    const historyForBackend = messages
      .filter((m) => m.role === "user" || m.role === "bot")
      .slice(-config.max_history_turns * 2)
      .map((m) => ({
        role: m.role === "user" ? "user" : "model",
        content: m.text,
      }));

    const augmentedUserPrompt = activeWinTitle
      ? `[Active Window: ${activeWinTitle}]\n${text}`
      : text;

    const currentTurn = {
      role: "user",
      content: augmentedUserPrompt,
      ...(screenImageB64 ? { image_base64: screenImageB64 } : {}),
    };

    const payloadMessages = [
      { role: "system", content: systemPrompt },
      ...historyForBackend,
      currentTurn,
    ];

    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          backend: config.backend,
          model: activeModelName,
          modelTier: config.modelTier,
          groundingMode: config.groundingMode,
          apiKey: config.gemini_api_key,
          ollamaUrl: config.ollama_base_url,
          messages: payloadMessages,
        }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`Server returned HTTP ${response.status}: ${errText}`);
      }

      if (!response.body) {
        throw new Error("No readable response stream received from server");
      }

      setMessages((prev) => [...prev, newBotMsg]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let accumulatedText = "";
      let modelUsed = activeModelName;
      let groundingSources: any[] = [];

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const raw = line.slice(5).trim();
          if (!raw) continue;

          try {
            const data = JSON.parse(raw);
            if (data.error) {
              throw new Error(data.error);
            }
            if (data.token) {
              setAssistantState("speaking");
              accumulatedText += data.token;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === botMsgId
                    ? { ...m, text: accumulatedText, isStreaming: true }
                    : m
                )
              );
            }
            if (data.grounding && Array.isArray(data.grounding)) {
              groundingSources = data.grounding;
            }
            if (data.modelUsed) {
              modelUsed = data.modelUsed;
            }
            if (data.done) {
              break;
            }
          } catch (e: any) {
            if (e.message && !e.message.includes("JSON")) {
              throw e;
            }
          }
        }
      }

      // Finalize bot message
      setMessages((prev) =>
        prev.map((m) =>
          m.id === botMsgId
            ? {
                ...m,
                isStreaming: false,
                modelUsed,
                groundingSources:
                  groundingSources.length > 0 ? groundingSources : undefined,
              }
            : m
        )
      );
      setAssistantState("idle");
    } catch (err: any) {
      if (err.name === "AbortError") {
        return;
      }
      setAssistantState("idle");
      setMessages((prev) =>
        prev.filter((m) => m.id !== botMsgId || m.text.length > 0)
      );
      addErrorMessage(err.message || "An unexpected error occurred.");
    } finally {
      abortControllerRef.current = null;
    }
  };

  const isRikka = config.mode === "rikka";

  return (
    <div
      className={`min-h-screen w-full flex items-center justify-center p-2 sm:p-4 transition-colors duration-500 ${
        isRikka ? "mode-rikka bg-[#070514]" : "mode-normal bg-[#0a0c12]"
      }`}
    >
      {/* Background ambient atmospheric lighting */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        {isRikka ? (
          <>
            <div className="absolute -top-40 -left-40 w-96 h-96 bg-[#7c4dff]/20 rounded-full filter blur-[120px]" />
            <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-[#d050e8]/15 rounded-full filter blur-[130px]" />
          </>
        ) : (
          <>
            <div className="absolute -top-40 -left-40 w-96 h-96 bg-[#38BDF8]/15 rounded-full filter blur-[120px]" />
            <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-[#0071E3]/15 rounded-full filter blur-[130px]" />
          </>
        )}
      </div>

      {/* Floating Assistant Card */}
      {isMinimized ? (
        <div
          onClick={() => setIsMinimized(false)}
          className={`fixed bottom-6 right-6 z-40 px-4 py-2.5 rounded-full border shadow-2xl flex items-center gap-2.5 cursor-pointer transition-all hover:scale-105 ${
            isRikka
              ? "bg-[#141032] border-[#ae86ff]/40 text-[#ede7f6]"
              : "bg-[#181c26] border-white/20 text-white"
          }`}
        >
          <img
            src="/assets/rikka_portrait.png"
            alt="Rikka"
            className="w-7 h-7 rounded-full object-cover border border-[#ae86ff]"
          />
          <span className="text-xs font-semibold">
            {isRikka ? "Rikka Assistant" : "AI Assistant"}
          </span>
          <Maximize2 className="w-3.5 h-3.5 text-white/60 ml-1" />
        </div>
      ) : (
        <main
          className={`relative z-10 w-full max-w-[450px] h-[730px] max-h-[96vh] flex flex-col rounded-[22px] border overflow-hidden transition-all duration-300 shadow-2xl ${
            isRikka
              ? "bg-gradient-to-b from-[#141032] via-[#09071a] to-[#060412] border-[rgba(124,77,255,0.38)] shadow-[0_10px_40px_rgba(35,10,60,0.8)]"
              : "bg-gradient-to-b from-white/[0.14] via-[#141824]/95 to-[#0a0c12]/98 backdrop-blur-xl border-white/20 shadow-[0_12px_42px_rgba(0,0,0,0.7)]"
          }`}
        >
          {/* Draggable Title Bar */}
          <TitleBar
            mode={config.mode}
            backend={config.backend}
            modelTier={config.modelTier}
            onToggleBackend={handleToggleBackend}
            onToggleMode={handleToggleMode}
            onCycleModelTier={handleCycleModelTier}
            onOpenMusic={() => setIsMusicStudioOpen(true)}
            onOpenImage={() => setIsImageStudioOpen(true)}
            onMinimize={() => setIsMinimized(true)}
            onClose={() => {
              addSystemMessage("👋  Rikka Assistant minimized to tray.");
              setIsMinimized(true);
            }}
          />

          {/* Animated Avatar Row with Engine Status Badge */}
          <AvatarRow
            mode={config.mode}
            state={assistantState}
            backend={config.backend}
            model={
              config.backend === "gemini"
                ? getModelForTier(config.modelTier)
                : config.ollama_model
            }
          />

          {/* Scrollable Message History */}
          <ChatWidget
            messages={messages}
            mode={config.mode}
            isThinking={assistantState === "thinking"}
          />

          {/* Expanding Input Bar with Privacy Toggles & Action Buttons */}
          <InputBar
            mode={config.mode}
            isBusy={assistantState !== "idle"}
            screenEnabled={config.screen_context_enabled}
            systemEnabled={config.system_tools_enabled}
            modelTier={config.modelTier}
            groundingMode={config.groundingMode}
            onSendMessage={handleSendMessage}
            onStats={handleStats}
            onClear={handleClear}
            onSettings={() => setIsSettingsOpen(true)}
            onToggleScreen={handleToggleScreen}
            onToggleSystem={handleToggleSystem}
            onCycleModelTier={handleCycleModelTier}
            onToggleGrounding={handleToggleGrounding}
            onOpenMusic={() => setIsMusicStudioOpen(true)}
            onOpenImage={() => setIsImageStudioOpen(true)}
          />

          {/* Fluid expanding wave ripple overlay when switching modes */}
          {waveState && (
            <WaveTransitionOverlay
              origin={waveState.origin}
              toMode={waveState.toMode}
              onAnimationEnd={() => setWaveState(null)}
            />
          )}
        </main>
      )}

      {/* Settings Modal Dialog */}
      <SettingsDialog
        config={config}
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSave={(newConfig) => {
          setConfig(newConfig);
          addSystemMessage("✔  Settings saved. New configuration active.");
        }}
      />

      {/* Image Alchemy Studio Modal (gemini-nano-banana-2.1) */}
      <ImageStudioModal
        isOpen={isImageStudioOpen}
        mode={config.mode}
        onClose={() => setIsImageStudioOpen(false)}
        onImageCreated={handleImageCreated}
        screenContextB64={latestScreenContext}
      />

      {/* Music Studio Modal (lyria-3-clip-preview / lyria-3-pro) */}
      <MusicStudioModal
        isOpen={isMusicStudioOpen}
        mode={config.mode}
        onClose={() => setIsMusicStudioOpen(false)}
        onMusicCreated={handleMusicCreated}
        screenContextB64={latestScreenContext}
      />
    </div>
  );
};
