"""Estado, configuración y tipos compartidos."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "objects.json"
DATABASE_FILE = ROOT / "data" / "solar_system.db"


class AppState(str, Enum):
    BOOT = "BOOT"
    IDLE = "IDLE"
    SCANNING = "SCANNING"
    QR_DETECTED = "QR_DETECTED"
    LOADING = "LOADING"
    PRESENTING = "PRESENTING"
    WAIT_CHOICE = "WAIT_CHOICE"
    LISTENING = "LISTENING"
    WAIT_CARD_REMOVAL = "WAIT_CARD_REMOVAL"
    ERROR = "ERROR"
    RECOVERY = "RECOVERY"


@dataclass(frozen=True)
class Settings:
    scan_fps: float = float(os.getenv("SOLAR_SCAN_FPS", "6"))
    removal_frames: int = int(os.getenv("SOLAR_REMOVAL_FRAMES", "12"))
    piper_bin: str = os.getenv("DAVEFX_PIPER_BIN", "piper")
    davefx_model: str = os.getenv("DAVEFX_MODEL", "/opt/reachy/voices/es_ES-davefx-medium.onnx")
    audio_player: str = os.getenv("DAVEFX_AUDIO_PLAYER", "aplay")
    voice_answer_timeout: float = float(os.getenv("SOLAR_VOICE_TIMEOUT", "5"))
    voice_answer_retries: int = int(os.getenv("SOLAR_VOICE_RETRIES", "1"))
