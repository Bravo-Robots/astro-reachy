---
title: Astro Reachy
emoji: "🪐"
colorFrom: blue
colorTo: purple
sdk: static
pinned: false
short_description: Una aventura planetaria con tarjetas QR para Reachy Mini.
tags:
  - reachy_mini
  - reachy_mini_python_app
  - education
---

# Astro Reachy — Sistema Solar para Reachy Mini

Aplicación educativa determinista para explorar el Sistema Solar mediante
tarjetas QR físicas.

## Qué hace

Al mostrar una tarjeta física, la cámara de Reachy detecta su QR con OpenCV.
El QR solo contiene un identificador; la app recupera el objeto y sus bloques
educativos desde SQLite, habla con Piper/DaveFX y ejecuta gestos oficiales de
Reachy cuando estén disponibles. Primero comparte una cápsula de descubrimiento
y pregunta si se quiere saber más. Las tarjetas `MAS_001` y `OTRA_001` sirven
como respuesta física sin necesitar reconocimiento de voz; tras una presentación
espera a que la tarjeta desaparezca, para no repetirla continuamente.

No usa LLM, servicios cloud, reconocimiento de voz ni movimientos articulares
propios.

## Tarjetas QR

Los PNG imprimibles de `assets/cards/` se generan a 300 dpi en 100 × 141,7 mm,
con QR de alta corrección de errores y una zona blanca para máxima legibilidad.
También se incluyen las respuestas `MAS_001` y `OTRA_001`. Se generan una vez en el equipo de
desarrollo (no hace falta `qrcode` en Reachy):

```powershell
py -3.15 -m pip install ".[cards]"
py -3.15 scripts/generate_cards.py
```

Se crearán diez tarjetas cuyo contenido QR es, por ejemplo, `MARTE_001`; la
información no se almacena dentro del código.

Las fotografías planetarias usadas en las tarjetas están en `assets/planets/`
y proceden de misiones de NASA; las referencias concretas se conservan en
`assets/planets/CREDITS.txt`.

## Impresión 3D

El QR debe imprimirse en papel: el relieve 3D no ofrece la precisión ni el
contraste necesarios para una lectura fiable de cámara. El archivo
`models/astro_reachy_card_holder.scad` es un marco de 106 × 149,7 mm con un
rebaje para pegar dentro una tarjeta Astro Reachy. Ábrelo en OpenSCAD y exporta
STL; se recomienda PLA, capas de 0,20 mm y sin soportes.

## Configuración de DaveFX en Reachy

DaveFX es la voz local Piper `es_ES-davefx-medium`. Copia en el robot el modelo
Piper y su archivo de configuración (`.onnx` y `.onnx.json`) y especifica su
ruta antes de iniciar la app:

```bash
export DAVEFX_PIPER_BIN=/ruta/a/piper
export DAVEFX_MODEL=/ruta/a/es_ES-davefx-medium.onnx
```

La app sintetiza WAV localmente y usa `reachy_mini.media.play_sound()` para la
salida de audio gestionada por Reachy. Si falta Piper o el modelo, registra el
error y continúa escaneando sin cerrar la aplicación.

## Instalación y comprobación en Reachy Mini

Instala OpenCV en el entorno de aplicaciones de Reachy junto con el proyecto.
Después, desde la carpeta de la app:

```bash
reachy-mini-app-assistant check .
```

En el dashboard, instala/ejecuta **Sistema Solar**. La app solicita el backend
de media estándar del SDK, obtiene frames BGR con `mini.media.get_frame()` y
los procesa a 6 FPS por defecto; puede bajarse con `SOLAR_SCAN_FPS` en una
Raspberry Pi si hiciera falta.

## Pruebas sin robot

```powershell
py -3.15 -m unittest discover -s tests -v
```

Estas pruebas validan los diez identificadores, el sembrado SQLite y el caso de
QR desconocido. La prueba final de cámara, audio y gestos debe hacerse en el
robot porque este entorno de Windows no tiene `reachy-mini` ni hardware.
