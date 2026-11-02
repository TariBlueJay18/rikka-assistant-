import { SystemStats } from "./types";

export interface IntentResult {
  handled: boolean;
  message: string;
  actionUrl?: string;
}

export function tryExecuteSystemIntent(text: string): IntentResult | null {
  const lower = text.trim().toLowerCase();

  // Web search command: "search for ...", "google ..."
  const matchSearch = lower.match(/^(?:search(?:\s+for|\s+web|\s+google)?|google)\s+(.+)$/i);
  if (matchSearch) {
    const query = matchSearch[1].trim();
    const url = `https://www.google.com/search?q=${encodeURIComponent(query)}`;
    try {
      window.open(url, "_blank", "noopener,noreferrer");
    } catch {
      // browser popup blocker fallback
    }
    return {
      handled: true,
      message: `Opened web search for "${query}".`,
      actionUrl: url,
    };
  }

  // Open specific websites: "open youtube", "open github", "open reddit", etc.
  const matchOpenSite = lower.match(
    /^open\s+(youtube|github|reddit|twitter|x|twitch|wikipedia|gmail)\.?(?:com)?$/i
  );
  if (matchOpenSite) {
    const site = matchOpenSite[1].toLowerCase();
    const urls: Record<string, string> = {
      youtube: "https://youtube.com",
      github: "https://github.com",
      reddit: "https://reddit.com",
      twitter: "https://x.com",
      x: "https://x.com",
      twitch: "https://twitch.tv",
      wikipedia: "https://wikipedia.org",
      gmail: "https://mail.google.com",
    };
    const targetUrl = urls[site] || `https://${site}.com`;
    try {
      window.open(targetUrl, "_blank", "noopener,noreferrer");
    } catch {
      // ignore
    }
    return {
      handled: true,
      message: `Opened ${site} (${targetUrl}).`,
      actionUrl: targetUrl,
    };
  }

  // Open general URL: "open http..."
  const matchUrl = lower.match(/^open\s+(https?:\/\/\S+)$/i);
  if (matchUrl) {
    const targetUrl = matchUrl[1];
    try {
      window.open(targetUrl, "_blank", "noopener,noreferrer");
    } catch {
      // ignore
    }
    return {
      handled: true,
      message: `Opened URL in browser: ${targetUrl}`,
      actionUrl: targetUrl,
    };
  }

  // Desktop tool launch simulation
  const matchApp = lower.match(/^open\s+([a-zA-Z0-9_\- ]+)$/i);
  if (matchApp) {
    const appName = matchApp[1].trim().toLowerCase();
    const commonApps: Record<string, string> = {
      calculator: "Calculator (app launcher invoked)",
      calc: "Calculator (app launcher invoked)",
      notepad: "Text Editor (app launcher invoked)",
      terminal: "Terminal Console (app launcher invoked)",
      vscode: "Visual Studio Code (app launcher invoked)",
      spotify: "Spotify Music (app launcher invoked)",
      discord: "Discord Messenger (app launcher invoked)",
    };
    if (commonApps[appName]) {
      return {
        handled: true,
        message: `Launched ${commonApps[appName]}.`,
      };
    }
  }

  return null;
}

export function formatStats(stats: SystemStats): string {
  const lines: string[] = [
    `🖥  CPU     ${stats.cpu_percent}%  (${stats.cpu_count_physical}P / ${stats.cpu_count_logical}L cores)`,
    `🧠 RAM     ${stats.ram_used_gb} / ${stats.ram_total_gb} GB  (${stats.ram_percent}%)`,
  ];

  if (stats.disk_total_gb !== undefined && stats.disk_used_gb !== undefined) {
    lines.push(
      `💾 Disk    ${stats.disk_used_gb} / ${stats.disk_total_gb} GB  (${stats.disk_percent ?? 28}%)`
    );
  }

  if (stats.battery_percent !== undefined) {
    const plug = stats.battery_plugged ? "⚡" : "🔋";
    lines.push(`${plug}  Battery  ${Math.round(stats.battery_percent)}%`);
  }

  if (stats.platform) {
    lines.push(`🌐 System   ${stats.platform} (${stats.hostname || "local-host"})`);
  }

  return lines.join("\n");
}
