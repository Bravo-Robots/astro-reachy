import unittest

import numpy as np

from reachy_sistema_solar.voice_choice import VoiceChoice, YesNoListener, classify_answer


class VoiceChoiceTests(unittest.TestCase):
    def test_accepts_spanish_yes_variants(self):
        for answer in ("sí", "si", "claro", "vale, quiero saber más"):
            self.assertEqual(classify_answer(answer), VoiceChoice.YES)

    def test_accepts_spanish_no_variants(self):
        for answer in ("no", "no gracias", "siguiente planeta"):
            self.assertEqual(classify_answer(answer), VoiceChoice.NO)

    def test_unknown_reply_is_safe(self):
        self.assertEqual(classify_answer("cuéntame un chiste"), VoiceChoice.UNKNOWN)

    def test_microphone_int16_is_not_saturated(self):
        pcm = YesNoListener._as_mono_pcm16([np.array([0, 1200, -1200], dtype=np.int16)])
        restored = np.frombuffer(pcm, dtype="<i2")
        self.assertGreater(restored[1], 1000)
        self.assertLess(restored[2], -1000)

    def test_stereo_microphone_is_mixed_to_mono(self):
        pcm = YesNoListener._as_mono_pcm16([np.array([[0.5, 0.5], [-0.5, -0.5]], dtype=np.float32)])
        restored = np.frombuffer(pcm, dtype="<i2")
        self.assertEqual(len(restored), 2)
        self.assertGreater(restored[0], 10000)
        self.assertLess(restored[1], -10000)
