"""Prepara en el Reachy los WAV DaveFX de las cápsulas planetarias.

Ejecutar cuando el robot esté libre. Las tarjetas se reproducen después sin
tener que sintetizar nada durante la demostración.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


# En el snapshot de Hugging Face los scripts pueden ser enlaces a blobs;
# permitimos fijar la raíz del Space sin depender de resolve().
ROOT = Path(os.getenv("ASTRO_SOURCE_ROOT", Path(__file__).parents[1]))
MODEL = Path("/opt/reachy/voices/es_ES-davefx-medium.onnx")
CACHE = Path("/home/pollen/.cache/astro_reachy/davefx")
PIPER = Path(sys.executable).parent / "piper"


def capsule(body: dict) -> str:
    closing = f"Misión sobre {body['name']} completada. Cuando quieras, enséñame otra tarjeta para descubrir otro mundo."
    return " ".join(item["text"] for item in body["narration"][:5]) + " " + closing


def main() -> None:
    if not MODEL.is_file():
        raise SystemExit(f"No se encuentra DaveFX: {MODEL}")
    CACHE.mkdir(parents=True, exist_ok=True)
    bodies = json.loads((ROOT / "data" / "objects.json").read_text(encoding="utf-8"))
    for index, body in enumerate(bodies, start=1):
        text = capsule(body)
        output = CACHE / f"{hashlib.sha256(text.encode('utf-8')).hexdigest()[:24]}.wav"
        if output.is_file() and output.stat().st_size > 44:
            print(f"[{index}/{len(bodies)}] {body['name']}: ya listo", flush=True)
            continue
        print(f"[{index}/{len(bodies)}] {body['name']}: generando DaveFX…", flush=True)
        subprocess.run(
            [str(PIPER), "--model", str(MODEL), "--output_file", str(output)],
            input=text, text=True, encoding="utf-8", check=True, timeout=300,
        )
    print("Caché DaveFX preparada.", flush=True)


if __name__ == "__main__":
    main()
