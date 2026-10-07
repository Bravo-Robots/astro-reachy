"""Adaptador de cámara oficial y detector QR ligero de OpenCV."""
from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger("reachy_sistema_solar")


class QRVision:
    def __init__(self, reachy: Any) -> None:
        try:
            import cv2
        except ImportError as error:  # La app informa y sigue viva, no aborta el dashboard.
            raise RuntimeError("OpenCV no está instalado en el entorno de apps") from error
        self.cv2 = cv2
        self.reachy = reachy
        self.detector = cv2.QRCodeDetector()

    def read_qr(self) -> str | None:
        """Lee un frame BGR desde la cámara gestionada por el SDK oficial."""
        try:
            frame = self.reachy.media.get_frame()
            if frame is None:
                return None
            value, _, _ = self.detector.detectAndDecode(frame)
            return value.strip() or None
        except Exception as error:
            LOGGER.warning("[CAMERA] Frame/QR no disponible: %s", error)
            return None
