"""Adaptador de cámara oficial y detector QR ligero de OpenCV."""
from __future__ import annotations

import logging
from typing import Any

LOGGER = logging.getLogger("reachy_sistema_solar")


class QRVision:
    def __init__(self, reachy: Any) -> None:
        try:
            import zxingcpp
        except ImportError as error:  # La app informa y sigue viva, no aborta el dashboard.
            raise RuntimeError("El lector QR no está instalado en el entorno de apps") from error
        self.zxingcpp = zxingcpp
        self.reachy = reachy

    def read_qr(self) -> str | None:
        """Lee un frame BGR desde la cámara gestionada por el SDK oficial."""
        try:
            frame = self.reachy.media.get_frame()
            if frame is None:
                return None
            codes = self.zxingcpp.read_barcodes(frame)
            for code in codes:
                value = code.text.strip()
                if value:
                    return value
            return None
        except Exception as error:
            LOGGER.warning("[CAMERA] Frame/QR no disponible: %s", error)
            return None
