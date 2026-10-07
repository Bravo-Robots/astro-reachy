"""Presenta bloques narrativos naturales y sincroniza voz con gestos."""
from __future__ import annotations

import logging
from typing import Any

from .robot import DaveFXVoice, GesturePlayer

LOGGER = logging.getLogger("reachy_sistema_solar")


class Presenter:
    def __init__(self, voice: DaveFXVoice, gestures: GesturePlayer) -> None:
        self.voice, self.gestures = voice, gestures

    def _speak_blocks(self, body: dict[str, Any], blocks: list[dict[str, str]]) -> None:
        for block in blocks:
            LOGGER.info("[VOICE] Reproduciendo bloque: %s", block["id"])
            gesture_thread = self.gestures.play_concurrently(block["gesture"])
            self.voice.speak(block["text"])
            gesture_thread.join(timeout=0.1)

    def present_discovery(self, body: dict[str, Any]) -> None:
        """Primera cápsula: breve, dinámica y suficiente para despertar curiosidad."""
        LOGGER.info("[PRESENTATION] Descubrimiento de %s", body["name"])
        self._speak_blocks(body, body["narration"][:3])
        self.voice.speak(
            f"¡Qué gran descubrimiento, explorador! Ya conocemos lo esencial de {body['name']}. "
            "¿Quieres saber más? Muestra la tarjeta MÁS para continuar, u OTRA para seguir viajando."
        )

    def present_more(self, body: dict[str, Any]) -> None:
        """Segunda cápsula: profundiza solo cuando el visitante lo pide."""
        LOGGER.info("[PRESENTATION] Ampliación de %s", body["name"])
        self.voice.speak(f"¡Excelente elección! Abrimos el cuaderno estelar de {body['name']}.")
        self._speak_blocks(body, body["narration"][3:])
        self.voice.speak("¡Muy bien! Enséñame otra tarjeta para continuar nuestro viaje por el Sistema Solar.")
        LOGGER.info("[PRESENTATION] Finalizada")
