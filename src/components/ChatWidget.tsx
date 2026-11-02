import React, { useEffect, useRef, useState } from "react";
import { ChatMessage, ThemeMode } from "../types";
import { Copy, Check, Globe, MapPin, ExternalLink, Download } from "lucide-react";
import { AudioPlayerWidget } from "./AudioPlayerWidget";

interface ChatWidgetProps {
  messages: ChatMessage[];
  mode: ThemeMode;
  isThinking: boolean;
}

export const ChatWidget: React.FC<ChatWidgetProps> = ({
  messages,
  mode,
  isThinking,
}) => {
  const isRikka = mode === "rikka";
  const scrollRef = useRef<HTMLDivElement>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Auto-scroll on new message or stream chunk
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isThinking]);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1800);
  };

  return (
    <div
      ref={scrollRef}
      className="flex-1 overflow-y-auto px-3.5 py-4 space-y-3.5 text-sm"
    >
      {messages.map((msg) => {
        const isUser = msg.role === "user";
        const isBot = msg.role === "bot";
        const isSystem = msg.role === "system";
        const isError = msg.role === "error";

        if (isSystem) {
          return (
            <div
              key={msg.id}
              className={`p-2.5 rounded-xl border text-xs leading-relaxed transition-all ${
                isRikka
                  ? "bg-[rgba(124,77,255,0.12)] border-[rgba(174,134,255,0.25)] text-[#d8b4fe]"
                  : "bg-white/[0.06] border-white/10 text-[#CBD5E1]"
              }`}
            >
              <div className="whitespace-pre-wrap font-mono text-[11.5px]">
                {msg.text}
              </div>
            </div>
          );
        }

        if (isError) {
          return (
            <div
              key={msg.id}
              className="p-2.5 rounded-xl border bg-red-500/10 border-red-500/30 text-red-300 text-xs leading-relaxed"
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
            </div>
          );
        }

        return (
          <div
            key={msg.id}
            className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
          >
            <div
              className={`group relative max-w-[88%] sm:max-w-[82%] rounded-2xl p-3 shadow-md transition-all ${
                isUser
                  ? isRikka
                    ? "rounded-tr-sm bg-gradient-to-r from-[#3a1b6c] to-[#6b35cc] border border-[#ae86ff]/30 text-white"
                    : "rounded-tr-sm bg-gradient-to-br from-[#0071E3] to-[#0056B3] border border-white/20 text-white"
                  : isRikka
                  ? "rounded-tl-sm bg-gradient-to-br from-[#12102a]/90 to-[#1e1a44]/90 border border-[rgba(124,77,255,0.38)] text-[#ede7f6]"
                  : "rounded-tl-sm bg-gradient-to-b from-white/10 to-white/[0.04] backdrop-blur-md border border-white/10 text-[#F1F5F9]"
              }`}
            >
              {/* Optional attached screen context snapshot preview */}
              {msg.imagePreview && (
                <div className="mb-2.5 rounded-lg overflow-hidden border border-white/20 max-h-44 bg-black/40">
                  <img
                    src={`data:image/jpeg;base64,${msg.imagePreview}`}
                    alt="Screen Context"
                    className="w-full h-auto object-cover"
                  />
                  <div className="text-[10px] px-2 py-1 bg-black/60 text-white/70 font-mono flex items-center justify-between">
                    <span>Attached Screen Context</span>
                    {msg.activeWindow && <span>{msg.activeWindow}</span>}
                  </div>
                </div>
              )}

              {/* Message text with whitespace preservation */}
              {msg.text && (
                <div className="whitespace-pre-wrap leading-relaxed text-[13px] break-words">
                  {msg.text}
                  {msg.isStreaming && (
                    <span className="inline-block w-1.5 h-4 ml-1 bg-current animate-pulse align-middle" />
                  )}
                </div>
              )}

              {/* Embedded Audio Widget if message has music attachment */}
              {msg.musicAttachment && (
                <AudioPlayerWidget music={msg.musicAttachment} mode={mode} />
              )}

              {/* Embedded Image Artwork if message has image attachment */}
              {msg.imageAttachment && (
                <div className="my-2.5 rounded-xl overflow-hidden border border-white/20 shadow-xl bg-black/40">
                  <img
                    src={msg.imageAttachment.imageUrl}
                    alt={msg.imageAttachment.prompt}
                    className="w-full h-auto object-cover max-h-64"
                  />
                  <div className="p-2 bg-black/50 flex items-center justify-between text-[10px] text-white/70 font-mono">
                    <span className="truncate max-w-[70%]">
                      🎨 {msg.imageAttachment.prompt}
                    </span>
                    <a
                      href={msg.imageAttachment.imageUrl}
                      download={`rikka-art-${Date.now()}.png`}
                      className="p-1 rounded hover:bg-white/10 text-white"
                      title="Download image"
                    >
                      <Download className="w-3.5 h-3.5" />
                    </a>
                  </div>
                </div>
              )}

              {/* Google Search & Maps Grounding Citations */}
              {msg.groundingSources && msg.groundingSources.length > 0 && (
                <div className="mt-2.5 pt-2 border-t border-white/10 space-y-1.5">
                  <div className="flex items-center gap-1.5 text-[10px] font-bold text-white/60 uppercase tracking-wider">
                    <span>Grounding Sources</span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.groundingSources.map((source, sIdx) => {
                      const isMap = source.type === "maps";
                      return (
                        <a
                          key={sIdx}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={`inline-flex items-center gap-1 px-2 py-1 rounded-md text-[10px] border transition-colors ${
                            isMap
                              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300 hover:bg-emerald-500/20"
                              : "bg-sky-500/10 border-sky-500/30 text-sky-300 hover:bg-sky-500/20"
                          }`}
                        >
                          {isMap ? (
                            <MapPin className="w-2.5 h-2.5" />
                          ) : (
                            <Globe className="w-2.5 h-2.5" />
                          )}
                          <span className="max-w-[130px] truncate">
                            {source.title}
                          </span>
                          <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                        </a>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Footer: Timestamp, Model Used & Copy action */}
              <div
                className={`mt-2 flex items-center justify-between gap-2 text-[10px] ${
                  isUser
                    ? "text-white/60"
                    : isRikka
                    ? "text-[#9d8fc2]/70"
                    : "text-white/40"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <span>{msg.timestamp}</span>
                  {msg.modelUsed && (
                    <span className="font-mono text-[9px] px-1.5 py-0.2 rounded bg-white/5 border border-white/10">
                      {msg.modelUsed}
                    </span>
                  )}
                </div>

                <button
                  onClick={() => handleCopy(msg.id, msg.text)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded hover:bg-white/10 text-white/70 cursor-pointer"
                  title="Copy text"
                >
                  {copiedId === msg.id ? (
                    <Check className="w-3 h-3 text-emerald-400" />
                  ) : (
                    <Copy className="w-3 h-3" />
                  )}
                </button>
              </div>
            </div>
          </div>
        );
      })}

      {/* Typing indicator bubble */}
      {isThinking && (
        <div className="flex flex-col items-start animate-fade-in">
          <div
            className={`rounded-2xl rounded-tl-sm px-4 py-2.5 shadow-md flex items-center gap-1.5 border ${
              isRikka
                ? "bg-[#141032]/80 border-[rgba(124,77,255,0.3)] text-[#ae86ff]"
                : "bg-white/10 border-white/10 text-[#38BDF8]"
            }`}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="w-1.5 h-1.5 rounded-full bg-current animate-bounce" style={{ animationDelay: "300ms" }} />
            <span className="text-xs ml-1 font-mono tracking-wide">
              {isRikka ? "weaving spell…" : "processing…"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
