"""Reconocimiento acotado de respuestas habladas para Astro Reachy."""
from __future__ import annotations

from enum import Enum
import logging
import threading
import time
from typing import Any

import numpy as np

from .core import Settings

try:
    import speech_recognition as speech_recognition
except ImportError:  # La app informa y vuelve al QR si el extra no está disponible.
    speech_recognition = None

LOGGER = logging.getLogger("reachy_sistema_solar")


class VoiceChoice(str, Enum):
    YES = "YES"
    NO = "NO"
    UNKNOWN = "UNKNOWN"


YES_WORDS = {"si", "sí", "claro", "vale", "por supuesto", "adelante", "quiero"}
NO_WORDS = {"no", "no gracias", "negativo", "siguiente", "otro"}


def classify_answer(transcript: str) -> VoiceChoice:
    """Clasifica una respuesta española sin un modelo conversacional libre."""
    answer = " ".join(
        transcript.lower().strip().translate(str.maketrans("", "", "¿?¡!,.")).split()
    )
    if answer in YES_WORDS or answer.startswith(("si ", "sí ", "claro ", "vale ")):
        return VoiceChoice.YES
    if answer in NO_WORDS or answer.startswith(("no ", "negativo ", "siguiente ")):
        return VoiceChoice.NO
    return VoiceChoice.UNKNOWN


class YesNoListener:
    """Escucha una respuesta breve con el micrófono de Reachy Mini.

    La transcripción usa el servicio de reconocimiento de Google con ``es-ES``.
    Solo se procesa el búfer momentáneo y no se guardan audios.
    """

    def __init__(self, reachy: Any, settings: Settings) -> None:
        self.reachy, self.settings = reachy, settings

    @staticmethod
    def _as_mono_pcm16(chunks: list[Any]) -> bytes:
        """Convierte audio real del Mini a PCM mono que SpeechRecognition espera.

        El SDK puede entregar bloques ``float32`` o ``int16``, y en algunos
        firmwares lo hace en estéreo. Tratar todos como floats (la versión
        anterior) saturaba por completo el audio int16 y volvía imposible
        reconocer un simple “sí”.
        """
        blocks: list[np.ndarray] = []
        for sample in chunks:
            if isinstance(sample, (bytes, bytearray, memoryview)):
                block = np.frombuffer(sample, dtype="<i2")
            else:
                block = np.asarray(sample)
            if block.size == 0:
                continue
            if block.ndim > 1:
                # Media sobre canales: SpeechRecognition recibe un único canal.
                block = block.astype(np.float32).mean(axis=-1)
            if np.issubdtype(block.dtype, np.integer):
                info = np.iinfo(block.dtype)
                scale = float(max(abs(info.min), info.max))
                block = block.astype(np.float32) / scale
            else:
                block = block.astype(np.float32, copy=False)
            blocks.append(np.clip(block, -1.0, 1.0))
        if not blocks:
            return b""
        mono = np.concatenate(blocks)
        return (mono * 32767.0).astype("<i2").tobytes()

    def listen(self, stop_event: threading.Event) -> VoiceChoice:
        if speech_recognition is None:
            LOGGER.error("[VOICE] Falta SpeechRecognition; no se puede escuchar la respuesta")
            return VoiceChoice.UNKNOWN
        chunks: list[np.ndarray] = []
        deadline = time.monotonic() + self.settings.voice_answer_timeout
        try:
            self.reachy.media.start_recording()
            while not stop_event.is_set() and time.monotonic() < deadline:
                sample = self.reachy.media.get_audio_sample()
                if sample is not None:
                    chunks.append(np.asarray(sample))
                else:
                    stop_event.wait(0.01)
        except Exception as error:
            LOGGER.warning("[VOICE] Micrófono no disponible: %s", error)
            return VoiceChoice.UNKNOWN
        finally:
            try:
                self.reachy.media.stop_recording()
            except Exception:
                pass
        if not chunks or stop_event.is_set():
            return VoiceChoice.UNKNOWN
        try:
            pcm16 = self._as_mono_pcm16(chunks)
            if not pcm16:
                LOGGER.info("[VOICE] El micrófono no entregó muestras útiles")
                return VoiceChoice.UNKNOWN
            audio = speech_recognition.AudioData(
                pcm16, int(self.reachy.media.get_input_audio_samplerate()), 2
            )
            recognizer = speech_recognition.Recognizer()
            # Una frase de una o dos palabras; los umbrales bajos favorecen la
            # respuesta cerca del robot, sin abrir la puerta a conversación libre.
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 0.45
            transcript = recognizer.recognize_google(audio, language="es-ES")
            choice = classify_answer(transcript)
            LOGGER.info("[VOICE] Transcripción: %r; decisión: %s", transcript, choice.value)
            return choice
        except speech_recognition.UnknownValueError:
            LOGGER.info("[VOICE] Respuesta no inteligible")
        except speech_recognition.RequestError as error:
            LOGGER.warning("[VOICE] Servicio de reconocimiento no disponible: %s", error)
        except Exception as error:
            LOGGER.warning("[VOICE] No se pudo procesar la respuesta: %s", error)
        return VoiceChoice.UNKNOWN
