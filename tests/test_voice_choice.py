import unittest

from reachy_sistema_solar.voice_choice import VoiceChoice, classify_answer


class VoiceChoiceTests(unittest.TestCase):
    def test_accepts_spanish_yes_variants(self):
        for answer in ("sí", "si", "claro", "vale, quiero saber más"):
            self.assertEqual(classify_answer(answer), VoiceChoice.YES)

    def test_accepts_spanish_no_variants(self):
        for answer in ("no", "no gracias", "siguiente planeta"):
            self.assertEqual(classify_answer(answer), VoiceChoice.NO)

    def test_unknown_reply_is_safe(self):
        self.assertEqual(classify_answer("cuéntame un chiste"), VoiceChoice.UNKNOWN)
