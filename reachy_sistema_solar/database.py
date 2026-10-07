"""Repositorio SQLite local; los datos viven en JSON y la lógica no los codifica."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


class SolarRepository:
    def __init__(self, database_path: Path, source_path: Path) -> None:
        self.database_path, self.source_path = database_path, source_path

    def initialise(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        records = json.loads(self.source_path.read_text(encoding="utf-8"))
        connection = sqlite3.connect(self.database_path)
        try:
            connection.execute("CREATE TABLE IF NOT EXISTS celestial_objects (qr_id TEXT PRIMARY KEY, payload TEXT NOT NULL)")
            connection.execute("DELETE FROM celestial_objects")
            connection.executemany(
                "INSERT INTO celestial_objects(qr_id, payload) VALUES (?, ?)",
                [(record["qr_id"], json.dumps(record, ensure_ascii=False)) for record in records],
            )
            connection.commit()
        finally:
            connection.close()

    def get_by_qr(self, qr_id: str) -> dict[str, Any] | None:
        connection = sqlite3.connect(self.database_path)
        try:
            row = connection.execute("SELECT payload FROM celestial_objects WHERE qr_id = ?", (qr_id,)).fetchone()
        finally:
            connection.close()
        return json.loads(row[0]) if row else None
