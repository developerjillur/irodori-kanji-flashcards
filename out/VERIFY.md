# Verification: decks against the PDF word lists

Made by `scripts/verify.py` from `data/entries.json` (extracted from the PDFs), `data/cards.json` and the data
inside `index.html`. "PDF entries" is every row of the lesson's word list; "with kanji" is counted here again
with a Unicode test (CJK ideographs U+3400 to U+4DBF, U+4E00 to U+9FFF, U+F900 to U+FAFF, and 々).

## Starter (入門), from `wordlist_X.pdf`

| Lesson | PDF entries | With kanji | Cards in deck | Match |
|---|---|---|---|---|
| 1 | 24 | 5 | 5 | yes |
| 2 | 50 | 22 | 22 | yes |
| 3 | 36 | 20 | 20 | yes |
| 4 | 58 | 26 | 26 | yes |
| 5 | 54 | 26 | 26 | yes |
| 6 | 94 | 28 | 28 | yes |
| 7 | 95 | 57 | 57 | yes |
| 8 | 35 | 23 | 23 | yes |
| 9 | 82 | 66 | 66 | yes |
| 10 | 74 | 43 | 43 | yes |
| 11 | 66 | 27 | 27 | yes |
| 12 | 99 | 83 | 83 | yes |
| 13 | 77 | 65 | 65 | yes |
| 14 | 73 | 48 | 48 | yes |
| 15 | 104 | 61 | 61 | yes |
| 16 | 119 | 64 | 64 | yes |
| 17 | 93 | 65 | 65 | yes |
| 18 | 51 | 35 | 35 | yes |
| **Total** | **1284** | **764** | **764** | |

## Elementary 1 (初級1), from `wordlist_Y.pdf`

| Lesson | PDF entries | With kanji | Cards in deck | Match |
|---|---|---|---|---|
| 1 | 68 | 58 | 58 | yes |
| 2 | 66 | 47 | 47 | yes |
| 3 | 50 | 34 | 34 | yes |
| 4 | 39 | 28 | 28 | yes |
| 5 | 52 | 35 | 35 | yes |
| 6 | 50 | 41 | 41 | yes |
| 7 | 34 | 27 | 27 | yes |
| 8 | 48 | 23 | 23 | yes |
| 9 | 64 | 45 | 45 | yes |
| 10 | 70 | 54 | 54 | yes |
| 11 | 92 | 52 | 52 | yes |
| 12 | 53 | 28 | 28 | yes |
| 13 | 91 | 69 | 69 | yes |
| 14 | 61 | 47 | 47 | yes |
| 15 | 97 | 76 | 76 | yes |
| 16 | 114 | 85 | 85 | yes |
| 17 | 70 | 37 | 37 | yes |
| 18 | 72 | 44 | 44 | yes |
| **Total** | **1191** | **830** | **830** | |

## Elementary 2 (初級2), from `wordlist_Z.pdf`

| Lesson | PDF entries | With kanji | Cards in deck | Match |
|---|---|---|---|---|
| 1 | 57 | 36 | 36 | yes |
| 2 | 74 | 44 | 44 | yes |
| 3 | 104 | 70 | 70 | yes |
| 4 | 91 | 56 | 56 | yes |
| 5 | 88 | 67 | 67 | yes |
| 6 | 114 | 91 | 91 | yes |
| 7 | 110 | 91 | 91 | yes |
| 8 | 106 | 69 | 69 | yes |
| 9 | 112 | 86 | 86 | yes |
| 10 | 96 | 55 | 55 | yes |
| 11 | 100 | 63 | 63 | yes |
| 12 | 124 | 96 | 96 | yes |
| 13 | 88 | 65 | 65 | yes |
| 14 | 134 | 103 | 103 | yes |
| 15 | 101 | 76 | 76 | yes |
| 16 | 195 | 164 | 164 | yes |
| 17 | 26 | 15 | 15 | yes |
| 18 | 50 | 40 | 40 | yes |
| **Total** | **1770** | **1287** | **1287** | |

**All three books: 4245 PDF entries, 2881 with kanji, 2881 cards.**

## Readings where the PDF's furigana and its accent column do not line up mechanically

The card uses the accent column (the PDF's full reading). These 12 are listed for a human eye:

| Card | Word | Reading on the card | Furigana printed above the word | PDF page |
|---|---|---|---|---|
| S-L06-038 | 焼き鳥／焼鳥 | やきとり | や + とり + やきとり | wordlist_X.pdf p.17 |
| S-L07-071 | 入れる／入 | いれる | い | wordlist_X.pdf p.24 |
| S-L07-072 | 切る／切 | きる | き | wordlist_X.pdf p.24 |
| S-L15-099 | 押す／押 | おす | お | wordlist_X.pdf p.56 |
| S-L15-100 | 引く／引 | ひく | ひ | wordlist_X.pdf p.56 |
| S-L15-101 | 開く／開 | ひらく | ひら | wordlist_X.pdf p.56 |
| S-L15-102 | 閉じる／閉 | とじる | と | wordlist_X.pdf p.56 |
| S-L16-097 | ～割引（二割引き） | ～わりびき（にわりびき） | わりびき + に + わりびき | wordlist_X.pdf p.61 |
| E1-L10-025 | 見学 | けんがく | げんがく | wordlist_Y.pdf p.27 |
| E2-L06-030 | ～行き | ～いき／ゆき | い／ゆ | wordlist_Z.pdf p.23 |
| E2-L06-092 | 浄土ヶ浜 | じょうどがはま | じょうどがはま | wordlist_Z.pdf p.26 |
| E2-L12-062 | ～合（5.5合） | ～ごう（ごーてんごごう） | ごう + ごてんごごう | wordlist_Z.pdf p.53 |

## Irodori Kanji (separate category), from `Irodori_Kanji_Furigana_Bangla_v2.pdf`

The PDF has 634 rows; 182 are Pre-Intermediate (初中級) and are left out.

| Lesson | Starter: PDF rows / cards | Elementary 1: PDF rows / cards | Elementary 2: PDF rows / cards |
|---|---|---|---|
| 1 | 0 / 0 | 10 / 10 | 9 / 9 |
| 2 | 0 / 0 | 11 / 11 | 10 / 10 |
| 3 | 3 / 3 | 9 / 9 | 10 / 10 |
| 4 | 4 / 4 | 10 / 10 | 9 / 9 |
| 5 | 3 / 3 | 10 / 10 | 10 / 10 |
| 6 | 3 / 3 | 10 / 10 | 10 / 10 |
| 7 | 4 / 4 | 10 / 10 | 11 / 11 |
| 8 | 3 / 3 | 9 / 9 | 9 / 9 |
| 9 | 8 / 8 | 10 / 10 | 10 / 10 |
| 10 | 7 / 7 | 9 / 9 | 10 / 10 |
| 11 | 6 / 6 | 10 / 10 | 10 / 10 |
| 12 | 6 / 6 | 9 / 9 | 10 / 10 |
| 13 | 8 / 8 | 11 / 11 | 11 / 11 |
| 14 | 6 / 6 | 10 / 10 | 10 / 10 |
| 15 | 6 / 6 | 11 / 11 | 10 / 10 |
| 16 | 10 / 10 | 12 / 12 | 9 / 9 |
| 17 | 8 / 8 | 11 / 11 | 10 / 10 |
| 18 | 6 / 6 | 11 / 11 | 10 / 10 |
| **Total** | **91 / 91** | **183 / 183** | **178 / 178** |

**Irodori Kanji: 452 cards in 3 books; the combined "All Irodori Kanji" deck is the same 452 cards in PDF order.**


Result: PASS

