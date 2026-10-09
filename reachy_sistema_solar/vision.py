"""Adaptador de cámara oficial y detector QR ligero de OpenCV."""
from __future__ import annotations

import logging
from typing import Any

import numpy as np

LOGGER = logging.getLogger("reachy_sistema_solar")


class QRVision:
    def __init__(self, reachy: Any) -> None:
        try:
            import zxingcpp
        except ImportError as error:  # La app informa y sigue viva, no aborta el dashboard.
            raise RuntimeError("El lector QR no está instalado en el entorno de apps") from error
        self.zxingcpp = zxingcpp
        self.reachy = reachy
        self._consecutive_misses = 0

    @staticmethod
    def _scan_sized(frame: Any) -> Any:
        """Reduce sólo para el análisis, nunca la cámara del dashboard.

        El stream IMX708 es mucho mayor de lo necesario para un QR impreso.
        Usar un muestreo de hasta 480 px de lado evita que la CPU de la
        Raspberry acumule frames obsoletos y conserva módulos suficientes
        para los QR de las tarjetas Astro Reachy.
        """
        height, width = frame.shape[:2]
        stride = max(1, (max(height, width) + 479) // 480)
        return frame[::stride, ::stride]

    @staticmethod
    def _lift_dark_frame(frame: Any) -> Any:
        """Da margen al QR en sombra sin alterar un fotograma bien expuesto."""
        mean_luma = float(np.asarray(frame).mean())
        if mean_luma >= 82:
            return frame
        # Sólo amplificamos sombras moderadas: con oscuridad absoluta no se
        # inventan detalles, por lo que la iluminación frontal sigue siendo
        # imprescindible para una lectura fiable.
        gain = 2 if mean_luma >= 38 else 3
        return np.minimum(np.asarray(frame, dtype=np.uint16) * gain, 255).astype(np.uint8)

    def read_qr(self) -> str | None:
        """Lee un frame BGR desde la cámara gestionada por el SDK oficial."""
        try:
            frame = self.reachy.media.get_frame()
            if frame is None:
                return None
            frame = self._lift_dark_frame(self._scan_sized(frame))
            # La vía rápida se ejecuta en cada fotograma. La más costosa sólo
            # cada cuatro fallos: así no bloquea ni retrasa la cámara mientras
            # no hay tarjeta, pero mantiene tolerancia al desenfoque moderado.
            binarizers = [self.zxingcpp.Binarizer.LocalAverage]
            if self._consecutive_misses % 4 == 3:
                binarizers.append(self.zxingcpp.Binarizer.GlobalHistogram)
            for binarizer in binarizers:
                codes = self.zxingcpp.read_barcodes(
                    frame,
                    formats=self.zxingcpp.BarcodeFormat.QRCode,
                    try_rotate=True,
                    try_downscale=True,
                    try_invert=False,
                    binarizer=binarizer,
                )
                for code in codes:
                    value = code.text.strip()
                    if value:
                        self._consecutive_misses = 0
                        return value
            self._consecutive_misses += 1
            return None
        except Exception as error:
            LOGGER.warning("[CAMERA] Frame/QR no disponible: %s", error)
            return None
