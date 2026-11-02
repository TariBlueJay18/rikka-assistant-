"""
Asynchronous LLM backend with multimodal screen context support.
Supports streaming from Ollama (local) and Gemini (cloud REST API).
All network I/O runs in a QThread so the UI never blocks.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Callable, Optional

import httpx
from PyQt6.QtCore import QThread, pyqtSignal

from config import Config

log = logging.getLogger(__name__)

MessageList = list[dict[str, Any]]


class LLMWorker(QThread):
    """
    Background thread that streams a single LLM turn.
    Supports text and optional screen context image.
    """

    token_received = pyqtSignal(str)
    response_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, config: Config, messages: MessageList) -> None:
        super().__init__()
        self._config = config
        self._messages = messages
        self._cancelled = False
        self._accumulated = ""

    def cancel(self) -> None:
        self._cancelled = True

    # ------------------------------------------------------------------ #

    def run(self) -> None:
        try:
            if self._config.backend == "ollama":
                self._run_ollama()
            elif self._config.backend == "gemini":
                self._run_gemini()
            else:
                self.error_occurred.emit(f"Unknown backend: '{self._config.backend}'")
        except Exception as exc:
            log.exception("LLMWorker unhandled exception")
            self.error_occurred.emit(f"Unexpected error: {exc}")

    # ------------------------------------------------------------------ #
    #  Ollama streaming                                                    #
    # ------------------------------------------------------------------ #

    def _run_ollama(self) -> None:
        url = f"{self._config.ollama_base_url}/api/chat"

        # Format messages for Ollama (handles optional images list)
        formatted_messages = []
        for msg in self._messages:
            entry: dict[str, Any] = {
                "role": msg["role"],
                "content": msg["content"],
            }
            if "image_base64" in msg and msg["image_base64"]:
                entry["images"] = [msg["image_base64"]]
            formatted_messages.append(entry)

        payload = {
            "model": self._config.ollama_model,
            "messages": formatted_messages,
            "stream": True,
        }
        try:
            with httpx.Client(timeout=self._config.ollama_timeout) as client:
                with client.stream("POST", url, json=payload) as resp:
                    resp.raise_for_status()
                    for raw_line in resp.iter_lines():
                        if self._cancelled:
                            return
                        if not raw_line:
                            continue
                        try:
                            obj = json.loads(raw_line)
                        except json.JSONDecodeError:
                            continue
                        chunk: str = obj.get("message", {}).get("content", "")
                        if chunk:
                            self._accumulated += chunk
                            self.token_received.emit(chunk)
                        if obj.get("done"):
                            break
            self.response_complete.emit(self._accumulated)

        except httpx.ConnectError:
            self.error_occurred.emit(
                f"Cannot reach Ollama at {self._config.ollama_base_url}.\n"
                "Please verify the server is running with: ollama serve"
            )
        except httpx.HTTPStatusError as exc:
            self.error_occurred.emit(
                f"Ollama returned HTTP {exc.response.status_code}:\n"
                f"{exc.response.text[:300]}"
            )

    # ------------------------------------------------------------------ #
    #  Gemini streaming (Server-Sent Events)                               #
    # ------------------------------------------------------------------ #

    def _run_gemini(self) -> None:
        if not self._config.gemini_api_key.strip():
            self.error_occurred.emit(
                "Gemini API key is not configured.\nOpen ⚙ Settings to add your key."
            )
            return

        system_text = ""
        chat_contents: list[dict] = []

        for msg in self._messages:
            if msg["role"] == "system":
                system_text = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                parts: list[dict] = [{"text": msg["content"]}]

                # Attach screen context image if present
                if "image_base64" in msg and msg["image_base64"]:
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": msg["image_base64"],
                        }
                    })

                chat_contents.append({
                    "role": role,
                    "parts": parts,
                })

        payload: dict = {
            "contents": chat_contents,
            "generationConfig": {"maxOutputTokens": 2048, "temperature": 0.85},
        }
        if system_text:
            payload["systemInstruction"] = {"parts": [{"text": system_text}]}

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._config.gemini_model}:streamGenerateContent"
            f"?key={self._config.gemini_api_key}&alt=sse"
        )

        try:
            with httpx.Client(timeout=self._config.ollama_timeout) as client:
                with client.stream("POST", url, json=payload) as resp:
                    resp.raise_for_status()
                    for raw_line in resp.iter_lines():
                        if self._cancelled:
                            return
                        if not raw_line.startswith("data:"):
                            continue
                        raw = raw_line[5:].strip()
                        if raw == "[DONE]":
                            break
                        try:
                            obj = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        for candidate in obj.get("candidates", []):
                            for part in candidate.get("content", {}).get("parts", []):
                                chunk = part.get("text", "")
                                if chunk:
                                    self._accumulated += chunk
                                    self.token_received.emit(chunk)
            self.response_complete.emit(self._accumulated)

        except httpx.ConnectError as exc:
            self.error_occurred.emit(f"Network error connecting to Gemini: {exc}")
        except httpx.HTTPStatusError as exc:
            self.error_occurred.emit(
                f"Gemini API error {exc.response.status_code}:\n"
                f"{exc.response.text[:300]}"
            )


# ------------------------------------------------------------------ #
#  Engine (conversation manager)                                       #
# ------------------------------------------------------------------ #

class LLMEngine:
    """Manages conversation history and coordinates LLMWorker threads."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self._history: MessageList = []
        self._active_worker: Optional[LLMWorker] = None

    def send(
        self,
        user_text: str,
        on_token: Callable[[str], None],
        on_complete: Callable[[str], None],
        on_error: Callable[[str], None],
        image_base64: Optional[str] = None,
        active_window: str = "",
    ) -> LLMWorker:
        """Append user message with optional screen context and stream response."""
        self.cancel_current()

        # Build augmented user content if window title is provided
        prompt_text = user_text
        if active_window:
            prompt_text = f"[Active Window: {active_window}]\n{user_text}"

        user_msg: dict[str, Any] = {"role": "user", "content": prompt_text}
        if image_base64:
            user_msg["image_base64"] = image_base64

        self._history.append(user_msg)

        max_msgs = self.config.max_history_turns * 2
        if len(self._history) > max_msgs:
            self._history = self._history[-max_msgs:]

        messages: MessageList = [
            {"role": "system", "content": self.config.system_prompt},
            *self._history,
        ]

        worker = LLMWorker(self.config, messages)
        worker.token_received.connect(on_token)
        worker.response_complete.connect(
            lambda full: self._handle_complete(full, on_complete)
        )
        worker.error_occurred.connect(on_error)
        self._active_worker = worker
        worker.start()
        return worker

    def _handle_complete(self, full_response: str, callback: Callable[[str], None]) -> None:
        self._history.append({"role": "assistant", "content": full_response})
        callback(full_response)

    def cancel_current(self) -> None:
        if self._active_worker and self._active_worker.isRunning():
            self._active_worker.cancel()
            self._active_worker.wait(2000)

    def clear_history(self) -> None:
        self.cancel_current()
        self._history.clear()

    def is_busy(self) -> bool:
        return bool(self._active_worker and self._active_worker.isRunning())
