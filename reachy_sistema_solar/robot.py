"""Voz DaveFX y expresividad: aisladas para no comprometer la detección."""
from __future__ import annotations

import logging
import hashlib
import math
from pathlib import Path
import subprocess
import tempfile
import threading
import time
from typing import Any, Callable
import wave

import numpy as np

from .core import Settings

LOGGER = logging.getLogger("reachy_sistema_solar")


class DaveFXVoice:
    """Sintetiza localmente con Piper y reproduce mediante el media manager de Reachy."""
    def __init__(self, reachy: Any, settings: Settings) -> None:
        self.reachy, self.settings = reachy, settings

    def _synthesise_davefx(self, text: str, output: Path, model: Path) -> None:
        """Genera DaveFX en un proceso corto, aislado del vídeo del robot."""
        result = subprocess.run(
            [self.settings.piper_bin, "--model", str(model), "--output_file", str(output)],
            input=text, text=True, encoding="utf-8", capture_output=True, timeout=300, check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "Piper no pudo sintetizar DaveFX")

    def _synthesise_espeak(self, text: str, output: Path) -> None:
        result = subprocess.run(
            [self.settings.espeak_bin, "-v", self.settings.espeak_voice, "-s", "155", "-w", str(output), text],
            text=True, encoding="utf-8", capture_output=True, timeout=20, check=False,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "eSpeak NG no pudo sintetizar la voz")

    def _davefx_cache_file(self, text: str) -> Path:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:24]
        directory = Path(self.settings.davefx_cache_dir)
        directory.mkdir(parents=True, exist_ok=True)
        return directory / f"{digest}.wav"

    def warm_up(self) -> None:
        """Compatibilidad: no precargamos ONNX para no frenar cámara ni gestos."""
        return

    @staticmethod
    def _duration_seconds(path: Path) -> float:
        """Duración real del WAV para sincronizar voz, gesto y micrófono."""
        with wave.open(str(path), "rb") as wav_file:
            return wav_file.getnframes() / max(1, wav_file.getframerate())

    def speak(self, text: str, on_playback_start: Callable[[float], None] | None = None) -> bool:
        model = Path(self.settings.davefx_model)
        output: Path | None = None
        is_cached = False
        try:
            if self.settings.voice_engine.lower() == "davefx" and model.is_file():
                output = self._davefx_cache_file(text)
                is_cached = output.is_file() and output.stat().st_size > 44
                if not is_cached:
                    LOGGER.info("[VOICE] Preparando cápsula DaveFX (sólo una vez)")
                    self._synthesise_davefx(text, output, model)
            else:
                LOGGER.info("[VOICE] Usando voz local inmediata")
                output = Path(tempfile.mkstemp(prefix="reachy-solar-", suffix=".wav")[1])
                self._synthesise_espeak(text, output)
            # Arranca el gesto justo antes de reproducir: así acompaña a la
            # voz (no llega después de que termine de hablar).
            duration = self._duration_seconds(output)
            if on_playback_start is not None:
                on_playback_start(duration)
            # play_sound es asíncrono en el SDK. Conservamos el fichero y
            # esperamos su duración, de modo que el micrófono nunca intenta
            # reconocer la propia pregunta de Reachy.
            self.reachy.media.play_sound(str(output))
            time.sleep(duration + 0.20)
            return True
        except Exception as error:
            LOGGER.exception("[VOICE] No se pudo reproducir DaveFX: %s", error)
            return False
        finally:
            if output is not None and not is_cached and self.settings.voice_engine.lower() != "davefx":
                output.unlink(missing_ok=True)


class GesturePlayer:
    """Gestos mínimos de antenas que no compiten con la reproducción de voz."""
    # Los movimientos registrados de la biblioteca de emociones contienen
    # coreografías completas. En un Mini inalámbrico pueden competir con el
    # audio de la narración. Usamos en su lugar pequeños movimientos de
    # antenas: visibles, silenciosos y sin cambiar cabeza ni cuerpo.
    _MAP = {
        "alegre": [0.42, -0.42],
        "curioso": [-0.36, 0.48],
        "sorpresa": [0.58, -0.58],
        "suave": [0.28, -0.28],
        "orgulloso": [-0.48, 0.34],
        "atento": [0.30, 0.30],
    }

    def __init__(self, reachy: Any) -> None:
        self.reachy = reachy
        self._last_started = 0.0

    def play(self, gesture: str) -> None:
        # Nunca solapar movimientos: el daemon rechaza objetivos simultáneos.
        if time.monotonic() - self._last_started < 4.8:
            return
        try:
            target = self._MAP.get(gesture, self._MAP["atento"])
            self._last_started = time.monotonic()
            # Alternamos un asentimiento/inclinación de cabeza y un giro
            # corporal mínimo. Son posiciones interpoladas, no animaciones
            # completas, para que sigan siendo silenciosas y predecibles.
            angle = {"alegre": 0.28, "curioso": -0.24, "sorpresa": 0.18,
                     "suave": -0.16, "orgulloso": 0.32, "atento": -0.20}.get(gesture, 0.0)
            head = np.eye(4)
            head[:3, :3] = np.array([
                [math.cos(angle), -math.sin(angle), 0.0],
                [math.sin(angle), math.cos(angle), 0.0],
                [0.0, 0.0, 1.0],
            ])
            body_yaw = 0.22 if gesture in {"alegre", "orgulloso", "sorpresa"} else -0.18
            self.reachy.goto_target(head=head, antennas=target, duration=0.90, body_yaw=body_yaw)
            self.reachy.goto_target(head=np.eye(4), antennas=[-0.1745, 0.1745], duration=0.90, body_yaw=0.0)
        except Exception as error:
            LOGGER.warning("[MOTION] Gesto omitido: %s", error)

    def play_concurrently(self, gesture: str) -> threading.Thread:
        thread = threading.Thread(target=self.play, args=(gesture,), daemon=True)
        thread.start()
        return thread

    def play_sequence(self, gestures: list[str], speech_duration: float) -> threading.Thread:
        """Reparte los gestos narrativos durante toda la explicación."""
        selected = gestures[:5]

        def run() -> None:
            if not selected:
                return
            # Deja que se oiga claramente la frase de descubrimiento antes
            # del primer gesto, pero aún sucede durante la explicación.
            time.sleep(min(3.0, speech_duration / 5.0))
            interval = max(5.2, speech_duration / (len(selected) + 0.5))
            for index, gesture in enumerate(selected):
                if index:
                    time.sleep(interval)
                self.play(gesture)

        thread = threading.Thread(target=run, name="astro-gesture-sequence", daemon=True)
        thread.start()
        return thread
