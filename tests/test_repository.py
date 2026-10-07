from pathlib import Path
import tempfile
import unittest

from reachy_sistema_solar.core import DATA_FILE
from reachy_sistema_solar.database import SolarRepository


class RepositoryTests(unittest.TestCase):
    def test_all_initial_qr_ids_are_available(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = SolarRepository(Path(directory) / "solar.db", DATA_FILE)
            repo.initialise()
            for qr_id in ("SOL_001", "MERCURIO_001", "VENUS_001", "TIERRA_001", "LUNA_001", "MARTE_001", "JUPITER_001", "SATURNO_001", "URANO_001", "NEPTUNO_001"):
                item = repo.get_by_qr(qr_id)
                self.assertIsNotNone(item)
                self.assertGreaterEqual(len(item["narration"]), 6)
                self.assertGreaterEqual(len(item["facts"]), 10)

    def test_unknown_qr_is_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = SolarRepository(Path(directory) / "solar.db", DATA_FILE)
            repo.initialise()
            self.assertIsNone(repo.get_by_qr("NO_EXISTE_001"))
