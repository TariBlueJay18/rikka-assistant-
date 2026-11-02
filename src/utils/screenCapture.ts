/**
 * Captures screen context using the browser's getDisplayMedia API,
 * downscaling to max 1024x768 and encoding to base64 JPEG,
 * mirroring tools.capture_screen_context() in PyQt.
 */
export async function captureScreenContext(
  maxW: number = 1024,
  maxH: number = 768
): Promise<{ base64Jpeg: string | null; activeWindow: string }> {
  try {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      console.warn("Screen capture getDisplayMedia is not supported in this browser.");
      return { base64Jpeg: null, activeWindow: "Browser Display" };
    }

    const stream = await navigator.mediaDevices.getDisplayMedia({
      video: {
        displaySurface: "browser",
      },
      audio: false,
    });

    const track = stream.getVideoTracks()[0];
    const trackSettings = track.getSettings();
    const activeWindow = (trackSettings as any).displaySurface || "Display Window";

    const video = document.createElement("video");
    video.srcObject = stream;
    video.autoplay = true;

    await new Promise<void>((resolve) => {
      video.onloadedmetadata = () => {
        video.play().then(() => resolve()).catch(() => resolve());
      };
    });

    // Wait a brief moment for video frame rendering
    await new Promise((r) => setTimeout(r, 150));

    let width = video.videoWidth || 1280;
    let height = video.videoHeight || 720;

    // Downscale while keeping aspect ratio
    if (width > maxW || height > maxH) {
      const ratio = Math.min(maxW / width, maxH / height);
      width = Math.round(width * ratio);
      height = Math.round(height * ratio);
    }

    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");

    if (ctx) {
      ctx.drawImage(video, 0, 0, width, height);
    }

    // Stop all media tracks immediately for privacy
    stream.getTracks().forEach((t) => t.stop());

    const dataUrl = canvas.toDataURL("image/jpeg", 0.75);
    const base64Jpeg = dataUrl.replace(/^data:image\/jpeg;base64,/, "");

    return { base64Jpeg, activeWindow: `Screen (${activeWindow})` };
  } catch (err: any) {
    console.info("User dismissed or denied screen capture prompt:", err.message);
    return { base64Jpeg: null, activeWindow: "" };
  }
}
