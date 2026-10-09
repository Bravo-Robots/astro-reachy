"""Voz DaveFX y expresividad: aisladas para no comprometer la detección."""
from __future__ import annotations

import logging
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time
from typing import Any
import wave

from .core import Settings

LOGGER = logging.getLogger("reachy_sistema_solar")


class DaveFXVoice:
    """Sintetiza localmente con Piper y reproduce mediante el media manager de Reachy."""
    def __init__(self, reachy: Any, settings: Settings) -> None:
        self.reachy, self.settings = reachy, settings
        self._piper_voice: Any | None = None

    def _synthesise_davefx(self, text: str, output: Path, model: Path) -> None:
        """Mantiene DaveFX cargado para no pagar su arranque en cada frase."""
        if self._piper_voice is None:
            from piper import PiperVoice
            self._piper_voice = PiperVoice.load(str(model))
        with wave.open(str(output), "wb") as wav_file:
            self._piper_voice.synthesize_wav(text, wav_file)

    def warm_up(self) -> None:
        """Carga DaveFX al iniciar para que la primera tarjeta responda al instante."""
        model = Path(self.settings.davefx_model)
        if not model.is_file():
            return
        descriptor, path = tempfile.mkstemp(suffix=".wav")
        os.close(descriptor)
        try:
            self._synthesise_davefx("Listo.", Path(path), model)
        except Exception as error:
            LOGGER.warning("[VOICE] No se pudo precargar DaveFX: %s", error)
        finally:
            Path(path).unlink(missing_ok=True)

    def speak(self, text: str) -> bool:
        model = Path(self.settings.davefx_model)
        output = Path(tempfile.mkstemp(prefix="reachy-solar-", suffix=".wav")[1])
        try:
            if model.is_file():
                self._synthesise_davefx(text, output, model)
            else:
                # El Wireless no trae el modelo DaveFX de fábrica. eSpeak NG
                # está disponible en su sistema y mantiene la experiencia
                # didáctica completamente local, sin depender de internet.
                LOGGER.info("[VOICE] DaveFX no disponible; usando voz local eSpeak NG")
                result = subprocess.run(
                    [self.settings.espeak_bin, "-v", self.settings.espeak_voice, "-s", "155", "-w", str(output), text],
                    text=True, encoding="utf-8", capture_output=True, timeout=45, check=False,
                )
                if result.returncode:
                    LOGGER.error("[VOICE] eSpeak NG falló: %s", result.stderr.strip())
                    return False
            # API oficial: el media manager reproduce un fichero wav local.
            self.reachy.media.play_sound(str(output))
            return True
        except Exception as error:
            LOGGER.exception("[VOICE] No se pudo reproducir DaveFX: %s", error)
            return False
        finally:
            output.unlink(missing_ok=True)


class GesturePlayer:
    """Solo reproduce movimientos registrados por Pollen; no manda motores manualmente."""
    # Nombres comprobados en la biblioteca oficial de Pollen. Cada movimiento
    # ya contiene una trayectoria segura de cabeza, cuerpo y antenas.
    _MAP = {
        "alegre": "welcoming1",
        "curioso": "curious1",
        "sorpresa": "surprised1",
        "suave": "calming1",
        "orgulloso": "proud1",
        "atento": "attentive1",
    }

    def __init__(self, reachy: Any) -> None:
        self.reachy = reachy
        self.moves: Any | None = None
        self._last_started = 0.0
        try:
            from reachy_mini.motion.recorded_move import RecordedMoves
            self.moves = RecordedMoves("pollen-robotics/reachy-mini-emotions-library")
            LOGGER.info("[MOTION] Biblioteca oficial de emociones disponible")
        except Exception as error:
            LOGGER.warning("[MOTION] Gestos oficiales no disponibles; se omitirá movimiento: %s", error)

    def play(self, gesture: str) -> None:
        if not self.moves:
            return
        # Nunca solapar coreografías: el daemon rechaza objetivos simultáneos
        # y el resultado visual parece un espasmo.
        if time.monotonic() - self._last_started < 8.0:
            return
        try:
            name = self._MAP.get(gesture, "happy")
            self._last_started = time.monotonic()
            self.reachy.play_move(self.moves.get(name), initial_goto_duration=1.0)
        except Exception as error:
            LOGGER.warning("[MOTION] Gesto omitido: %s", error)

    def play_concurrently(self, gesture: str) -> threading.Thread:
        thread = threading.Thread(target=self.play, args=(gesture,), daemon=True)
        thread.start()
        return thread
