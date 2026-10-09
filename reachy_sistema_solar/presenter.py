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
        """Una cápsula continua con movimientos repartidos durante la voz."""
        if not blocks:
            return
        LOGGER.info("[VOICE] Reproduciendo cápsula: %s", ", ".join(block["id"] for block in blocks))
        text = " ".join(block["text"] for block in blocks) + " " + closing
        gestures = [block["gesture"] for block in blocks]
        self.voice.speak(text, on_playback_start=lambda duration: self.gestures.play_sequence(gestures, duration))

    def present_discovery(self, body: dict[str, Any]) -> None:
        """Cinco datos esenciales, seguidos de espera para otra tarjeta."""
        LOGGER.info("[PRESENTATION] Descubrimiento de %s", body["name"])
        self._capsule(body["narration"][:5],
            f"Misión sobre {body['name']} completada. Cuando quieras, enséñame otra tarjeta para descubrir otro mundo."
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
