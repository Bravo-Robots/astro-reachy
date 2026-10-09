"""Presenta bloques narrativos naturales y sincroniza voz con gestos."""
from __future__ import annotations

import logging
from typing import Any

from .robot import DaveFXVoice, GesturePlayer

LOGGER = logging.getLogger("reachy_sistema_solar")


class Presenter:
    def __init__(self, voice: DaveFXVoice, gestures: GesturePlayer) -> None:
        self.voice, self.gestures = voice, gestures

    def _capsule(self, blocks: list[dict[str, str]], closing: str) -> None:
        """Sintetiza una sola cápsula para evitar tres cargas DaveFX seguidas."""
        if not blocks:
            return
        LOGGER.info("[VOICE] Reproduciendo cápsula: %s", ", ".join(block["id"] for block in blocks))
        text = " ".join(block["text"] for block in blocks) + " " + closing
        self.voice.speak(text, on_playback_start=lambda: self.gestures.play_concurrently(blocks[0]["gesture"]))

    def present_discovery(self, body: dict[str, Any]) -> None:
        """Primera cápsula: breve, dinámica y suficiente para despertar curiosidad."""
        LOGGER.info("[PRESENTATION] Descubrimiento de %s", body["name"])
        self._capsule(body["narration"][:3],
            f"¡Qué gran descubrimiento, explorador! Ya conocemos lo esencial de {body['name']}. "
            "¿Quieres saber más? Cuando termine de hablar, responde sí o no."
        )

    def present_more(self, body: dict[str, Any]) -> None:
        """Segunda cápsula: profundiza solo cuando el visitante lo pide."""
        LOGGER.info("[PRESENTATION] Ampliación de %s", body["name"])
        self._capsule(
            body["narration"][3:6],
            f"¡Excelente elección! Hemos abierto el cuaderno estelar de {body['name']}. "
            "Misión completada. Enséñame otra tarjeta cuando quieras seguir viajando.",
        )
        LOGGER.info("[PRESENTATION] Finalizada")
