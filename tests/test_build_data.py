"""Tests for the word and reading clean-up and the kanji test (run: python3 -m unittest discover -s tests)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import build_data as bd  # noqa: E402


class KanjiTest(unittest.TestCase):
    def test_kanji_words(self):
        for w in ("学校", "お願いします", "時々", "1年", "浄土ヶ浜", "消しゴム", "～になる（1年になる）"):
            self.assertTrue(bd.has_kanji(w), w)

    def test_kana_only_words(self):
        for w in ("がっこう", "カード", "Tシャツ", "J-POP", "～よね", "すごいですね", "ドライ"):
            self.assertFalse(bd.has_kanji(w), w)


class CleanWordTest(unittest.TestCase):
    def test_verb_group_is_removed_and_kept(self):
        self.assertEqual(bd.clean_word("慣れる［2］"), ("慣れる", ["2"]))
        self.assertEqual(bd.clean_word("来る／来ます［3］"), ("来る／来ます", ["3"]))

    def test_layout_characters(self):
        self.assertEqual(bd.clean_word(" \x07皆様のご来場をお待ちしています")[0], "皆様のご来場をお待ちしています")
        self.assertEqual(bd.clean_word("1 年")[0], "1年")
        self.assertEqual(bd.clean_word("～合　（5.5 合）")[0], "～合（5.5合）")
        self.assertEqual(bd.clean_word("出る［2］( せき／鼻水が出る）")[0], "出る（せき／鼻水が出る）")
        self.assertEqual(bd.clean_word("あけましておめでとう\nございます")[0], "あけましておめでとうございます")


class CleanReadingTest(unittest.TestCase):
    def test_accent_marks_go(self):
        self.assertEqual(bd.clean_reading("がっこう○", "学校"), "がっこう")
        self.assertEqual(bd.clean_reading("く↓る／きま↓す", "来る／来ます"), "くる／きます")
        self.assertEqual(bd.clean_reading("あけま↓して△おめでとうございま↓す", "x"), "あけましておめでとうございます")

    def test_two_accents_of_one_reading_fold(self):
        self.assertEqual(bd.clean_reading("はんとし↓／はんとし○", "半年"), "はんとし")
        self.assertEqual(bd.clean_reading("バルコニー○／バルコ↓ニー／バル↓コニー", "バルコニー"), "バルコニー")
        self.assertEqual(bd.clean_reading("～かい○（いっかい○／いっ↓かい）", "～回（１回）"), "～かい（いっかい）")
        self.assertEqual(bd.clean_reading("～こみ↓（そ↓うりょう　こみ↓）／～こ↓み（そ↓うりょう　こ↓み）", "～込み（送料込み）"),
                         "～こみ（そうりょう こみ）")

    def test_real_variants_stay(self):
        self.assertEqual(bd.clean_reading("なな↓ねん／しち↓ねん", "7年"), "ななねん／しちねん")
        self.assertEqual(bd.clean_reading("しょうわ○／しょうわ○", "昭和／昭"), "しょうわ／しょうわ")

    def test_placeholder_triangle_is_kept(self):
        self.assertEqual(bd.clean_reading("だい～▲よ↓うび", "第～▲曜日"), "だい～▲ようび")


class CheckReadingTest(unittest.TestCase):
    def test_agreement(self):
        self.assertEqual(bd.check_reading("学校", "がっこう", ["がっこう"]), "")
        self.assertEqual(bd.check_reading("お先に失礼します", "おさきにしつれいします", ["さき", "しつれい"]), "")
        self.assertEqual(bd.check_reading("知り合い", "しりあい", ["し", "あ"]), "")

    def test_disagreement_is_reported(self):
        self.assertNotEqual(bd.check_reading("見学", "けんがく", ["げんがく"]), "")
        self.assertNotEqual(bd.check_reading("学校", "がっ校", ["がっこう"]), "")


if __name__ == "__main__":
    unittest.main()
