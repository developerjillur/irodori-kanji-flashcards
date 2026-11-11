"""Tests for the Irodori Kanji category's build checks (run: python3 -m unittest discover -s tests)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import build_kanji as bk  # noqa: E402


class SkeletonTest(unittest.TestCase):
    """The PDF's text layer loses Bengali vowel signs; the consonants must still match the typed Bangla."""

    def test_scrambled_layer_matches_real_text(self):
        pairs = [("দেশ", "ǂ%শ"), ("আমি", "আ7ম"), ("বের হওয়ার পথ; বহির্গমন", "ǂবর হওয়ার প$; ব7হগর্থমন"),
                 ("শিক্ষার্থী; ছাত্র/ছাত্রী", "7শক্ষিা$র্থী; ছোত্র/ছোত্রী"), ("পশ্চিম", "পǭশ্চিম"), ("দাঁড়ানো", "%াাড়া=না")]
        for text, raw in pairs:
            self.assertEqual(bk.skeleton(text), bk.skeleton(raw, raw=True), text)

    def test_a_wrong_line_is_caught(self):
        self.assertNotEqual(bk.skeleton("মা"), bk.skeleton("বাবা", raw=True))
        self.assertNotEqual(bk.skeleton("পানি"), bk.skeleton("পান ক7র; পান করা", raw=True))


class ReadingTest(unittest.TestCase):
    def test_kana_in_the_word_must_appear_in_the_reading(self):
        self.assertTrue(bk.kana_lines_up("食べます", "たべます"))
        self.assertTrue(bk.kana_lines_up("～曜日", "～ようび"))
        self.assertTrue(bk.kana_lines_up("好き（な）", "すき（な）"))
        self.assertTrue(bk.kana_lines_up("コピー機", "コピーき"))
        self.assertFalse(bk.kana_lines_up("食べます", "たべる"))
        self.assertFalse(bk.kana_lines_up("～時", "じ"))


if __name__ == "__main__":
    unittest.main()
