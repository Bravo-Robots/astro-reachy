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
        for index, block in enumerate(blocks):
            LOGGER.info("[VOICE] Reproduciendo bloque: %s", block["id"])
            # Una sola coreografía por cápsula. Antes se lanzaban varias en
            # paralelo si el audio no estaba disponible, provocando órdenes
            # de motor incompatibles.
            spoken = self.voice.speak(block["text"])
            # La voz sintetiza antes de comenzar el movimiento, para que el
            # gesto acompañe al sonido real y nunca a un silencio de carga.
            if index == 0 and spoken:
                self.gestures.play(block["gesture"])

    def present_discovery(self, body: dict[str, Any]) -> None:
        """Primera cápsula: breve, dinámica y suficiente para despertar curiosidad."""
        LOGGER.info("[PRESENTATION] Descubrimiento de %s", body["name"])
        self._speak_blocks(body, body["narration"][:3])
        self.voice.speak(
            f"¡Qué gran descubrimiento, explorador! Ya conocemos lo esencial de {body['name']}. "
            "¿Quieres saber más? Cuando termine de hablar, responde sí o no."
        )

    def present_more(self, body: dict[str, Any]) -> None:
        """Segunda cápsula: profundiza solo cuando el visitante lo pide."""
        LOGGER.info("[PRESENTATION] Ampliación de %s", body["name"])
        self.voice.speak(f"¡Excelente elección! Abrimos el cuaderno estelar de {body['name']}.")
        self._speak_blocks(body, body["narration"][3:6])
        self.voice.speak("Misión completada. Enséñame otra tarjeta cuando quieras seguir viajando.")
        LOGGER.info("[PRESENTATION] Finalizada")
