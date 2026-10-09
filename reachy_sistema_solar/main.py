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
            # Una app iniciada desde el dashboard no despierta los motores por
            # sí sola. Astro Reachy debe estar listo para recibir una tarjeta
            # sin exigir un paso manual adicional al visitante.
            try:
                reachy_mini.enable_motors()
                reachy_mini.wake_up()
            except Exception as error:
                LOGGER.warning("[ROBOT] No se pudo ejecutar el despertar automático: %s", error)
            repo.initialise()
            vision = QRVision(reachy_mini)
            voice = DaveFXVoice(reachy_mini, settings)
            presenter = Presenter(voice, GesturePlayer(reachy_mini))
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
                    # Una interacción determinista: cinco datos y vuelta a
                    # esperar tarjeta. No hay reconocimiento de voz ni pausas
                    # que puedan romper una demostración con público.
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
