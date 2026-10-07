# Plan de entrega

Aplicación Python para Reachy Mini que detecta tarjetas QR físicas, consulta una
base SQLite local y presenta explicaciones educativas en español con Piper/DaveFX
y movimientos seguros de la API oficial. No usa red, LLM ni reconocimiento de voz.

La app conserva el punto de entrada `reachy_mini_apps` existente. En el robot
usará `mini.media.get_frame()` (BGR) y `cv2.QRCodeDetector`; en desarrollo se
puede probar la cadena QR → SQLite → presentador con imágenes de `assets/cards`.

Pendiente de confirmar en el robot antes de una demostración física: modelo
(Lite/Wireless), rutas reales de `piper` y del modelo DaveFX, y disponibilidad de
la librería oficial de emociones. Si la última no está instalada, se omiten los
gestos sin enviar mandatos directos a motores.
