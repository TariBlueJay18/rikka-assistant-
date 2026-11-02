import React, { useState, useRef, useEffect } from "react";
import { Play, Pause, Download, Volume2, VolumeX, Music, FileText } from "lucide-react";
import { GeneratedMusic, ThemeMode } from "../types";

interface AudioPlayerWidgetProps {
  music: GeneratedMusic;
  mode: ThemeMode;
}

export const AudioPlayerWidget: React.FC<AudioPlayerWidgetProps> = ({
  music,
  mode,
}) => {
  const isRikka = mode === "rikka";
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [showLyrics, setShowLyrics] = useState(false);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const onTimeUpdate = () => setCurrentTime(audio.currentTime);
    const onLoadedMetadata = () => setDuration(audio.duration || 0);
    const onEnded = () => setIsPlaying(false);

    audio.addEventListener("timeupdate", onTimeUpdate);
    audio.addEventListener("loadedmetadata", onLoadedMetadata);
    audio.addEventListener("ended", onEnded);

    return () => {
      audio.removeEventListener("timeupdate", onTimeUpdate);
      audio.removeEventListener("loadedmetadata", onLoadedMetadata);
      audio.removeEventListener("ended", onEnded);
    };
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;
    if (isPlaying) {
      audio.pause();
      setIsPlaying(false);
    } else {
      audio.play().then(() => setIsPlaying(true)).catch(console.error);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = val;
      setCurrentTime(val);
    }
  };

  const toggleMute = () => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const formatTime = (secs: number) => {
    if (isNaN(secs)) return "0:00";
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div
      className={`rounded-2xl p-3.5 my-2 border shadow-lg transition-all ${
        isRikka
          ? "bg-[#181238]/90 border-[rgba(174,134,255,0.4)] text-[#ede7f6]"
          : "bg-white/10 border-white/20 text-white backdrop-blur-md"
      }`}
    >
      <audio ref={audioRef} src={music.audioUrl} preload="metadata" />

      {/* Track header */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2 overflow-hidden">
          <div
            className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
              isRikka
                ? "bg-gradient-to-br from-[#7c4dff] to-[#d050e8] text-white"
                : "bg-gradient-to-br from-[#0071E3] to-[#38BDF8] text-white"
            }`}
          >
            <Music className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <p className="text-xs font-bold truncate tracking-wide">
              {music.prompt}
            </p>
            <p className="text-[10px] text-white/60 font-mono">
              Model: {music.model}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          {music.lyrics && (
            <button
              onClick={() => setShowLyrics(!showLyrics)}
              className={`p-1.5 rounded-lg text-xs transition-colors cursor-pointer ${
                showLyrics
                  ? isRikka
                    ? "bg-[#ae86ff]/30 text-white"
                    : "bg-[#38BDF8]/30 text-white"
                  : "text-white/60 hover:text-white"
              }`}
              title="Toggle lyrics & notes"
            >
              <FileText className="w-3.5 h-3.5" />
            </button>
          )}

          <a
            href={music.audioUrl}
            download={`rikka-music-${Date.now()}.mp3`}
            className="p-1.5 rounded-lg text-white/60 hover:text-white transition-colors cursor-pointer"
            title="Download Audio MP3"
          >
            <Download className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* Animated Sound Waveform Bars */}
      <div className="flex items-center justify-center gap-1 h-6 my-2 px-1">
        {[20, 45, 80, 55, 90, 70, 35, 85, 60, 95, 40, 75, 50, 85, 30, 65].map(
          (height, i) => (
            <span
              key={i}
              className={`w-1 rounded-full transition-all duration-200 ${
                isPlaying
                  ? isRikka
                    ? "bg-gradient-to-t from-[#7c4dff] to-[#e879f9] animate-pulse"
                    : "bg-gradient-to-t from-[#0071E3] to-[#38BDF8] animate-pulse"
                  : "bg-white/20"
              }`}
              style={{
                height: isPlaying ? `${Math.max(15, (height * (i % 2 === 0 ? 1 : 0.7)))}%` : "20%",
                animationDelay: `${i * 70}ms`,
              }}
            />
          )
        )}
      </div>

      {/* Scrubber & Controls */}
      <div className="space-y-1">
        <input
          type="range"
          min={0}
          max={duration || 30}
          step={0.1}
          value={currentTime}
          onChange={handleSeek}
          className="w-full h-1 bg-white/20 rounded-lg appearance-none cursor-pointer accent-[#ae86ff]"
        />

        <div className="flex items-center justify-between text-[10px] text-white/60 font-mono">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls row */}
      <div className="flex items-center justify-between mt-2 pt-1 border-t border-white/10">
        <button
          onClick={togglePlay}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold shadow-md transition-all cursor-pointer ${
            isRikka
              ? "bg-gradient-to-r from-[#7c4dff] to-[#d050e8] hover:scale-105 text-white"
              : "bg-gradient-to-r from-[#0071E3] to-[#38BDF8] hover:scale-105 text-white"
          }`}
        >
          {isPlaying ? (
            <>
              <Pause className="w-3.5 h-3.5" />
              <span>Pause</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Play Melody</span>
            </>
          )}
        </button>

        <button
          onClick={toggleMute}
          className="p-1 text-white/60 hover:text-white cursor-pointer"
        >
          {isMuted ? (
            <VolumeX className="w-3.5 h-3.5" />
          ) : (
            <Volume2 className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Optional Lyrics Dropdown */}
      {showLyrics && music.lyrics && (
        <div className="mt-2.5 p-2.5 rounded-xl bg-black/40 border border-white/10 text-xs text-white/80 whitespace-pre-wrap font-sans max-h-36 overflow-y-auto leading-relaxed">
          <p className="font-semibold text-[11px] text-[#ae86ff] mb-1">
            Lyrics / Production Notes:
          </p>
          {music.lyrics}
        </div>
      )}
    </div>
  );
};
