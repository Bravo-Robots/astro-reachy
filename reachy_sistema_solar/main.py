"""Aplicación instalable Sistema Solar para Reachy Mini."""
from __future__ import annotations

import logging
import threading
import time

from reachy_mini import ReachyMini, ReachyMiniApp

from .core import AppState, DATA_FILE, DATABASE_FILE, Settings
from .database import SolarRepository
from .presenter import Presenter
from .robot import DaveFXVoice, GesturePlayer
from .vision import QRVision
from .voice_choice import VoiceChoice, YesNoListener

LOGGER = logging.getLogger("reachy_sistema_solar")


class ReachySistemaSolar(ReachyMiniApp):
    """QR → SQLite → DaveFX + gestos oficiales, con bloqueo hasta retirar tarjeta."""
    custom_app_url: str | None = None
    # El SDK negocia LOCAL/WebRTC automáticamente; no se fuerza un backend.
    request_media_backend: str | None = None

    def run(self, reachy_mini: ReachyMini, stop_event: threading.Event) -> None:
        settings = Settings()
        repo = SolarRepository(DATABASE_FILE, DATA_FILE)
        state, latched_qr, missing_frames, active_body = AppState.BOOT, None, 0, None
        try:
            repo.initialise()
            vision = QRVision(reachy_mini)
            voice = DaveFXVoice(reachy_mini, settings)
            voice.warm_up()
            presenter = Presenter(voice, GesturePlayer(reachy_mini))
            listener = YesNoListener(reachy_mini, settings)
            state = AppState.SCANNING
            LOGGER.info("[APP] Sistema Solar iniciado; [STATE] %s", state.value)
            while not stop_event.wait(1 / settings.scan_fps):
                qr_id = vision.read_qr()
                if state is AppState.SCANNING:
                    if not qr_id:
                        continue
                    state, latched_qr = AppState.QR_DETECTED, qr_id
                    LOGGER.info("[QR] Detectado: %s", qr_id)
                    state = AppState.LOADING
                    body = repo.get_by_qr(qr_id)
                    if not body:
                        LOGGER.warning("[DATABASE] QR desconocido: %s", qr_id)
                        state, latched_qr = AppState.WAIT_CARD_REMOVAL, qr_id
                        continue
                    LOGGER.info("[DATABASE] Encontrado: %s", body["name"])
                    state = AppState.PRESENTING
                    presenter.present_discovery(body)
                    state = AppState.LISTENING
                    choice = listener.listen(stop_event)
                    attempts = 0
                    while choice is VoiceChoice.UNKNOWN and attempts < settings.voice_answer_retries and not stop_event.is_set():
                        attempts += 1
                        presenter.voice.speak("No te he entendido. ¿Quieres saber más? Responde sí o no.")
                        choice = listener.listen(stop_event)
                    if choice is VoiceChoice.YES:
                        LOGGER.info("[CHOICE] Más información sobre %s", body["name"])
                        state = AppState.PRESENTING
                        presenter.present_more(body)
                    elif choice is VoiceChoice.NO:
                        LOGGER.info("[CHOICE] El visitante termina la misión de %s", body["name"])
                        presenter.voice.speak("Perfecto. Cuando quieras, enséñame otra tarjeta para descubrir un nuevo planeta.")
                    else:
                        presenter.voice.speak("No he recibido una respuesta. Estoy listo para leer otra tarjeta.")
                    # Evita repetir el mismo planeta mientras la tarjeta sigue
                    # delante de la cámara. La siguiente misión empieza al retirarla.
                    state, active_body, missing_frames = AppState.WAIT_CARD_REMOVAL, None, 0
                elif state is AppState.WAIT_CARD_REMOVAL:
                    if qr_id == latched_qr:
                        missing_frames = 0
                    else:
                        missing_frames += 1
                    if missing_frames >= settings.removal_frames:
                        LOGGER.info("[QR] Tarjeta retirada; [STATE] SCANNING")
                        state, latched_qr, active_body, missing_frames = AppState.SCANNING, None, None, 0
        except Exception as error:
            LOGGER.exception("[APP] Error recuperable: %s", error)
            # Terminar permite al dashboard liberar/reiniciar los recursos con seguridad.
        finally:
            LOGGER.info("[APP] Sistema Solar detenido; recursos liberados por el SDK")


if __name__ == "__main__":
    ReachySistemaSolar().wrapped_run()
