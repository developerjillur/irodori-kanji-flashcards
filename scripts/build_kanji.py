#!/usr/bin/env python3
"""Build the deck data of the separate "Irodori Kanji" category.

Reads data/kanji/raw.json (from extract_kanji.py) and data/kanji/bn.tsv (id, word, Bangla: the PDF's Bangla column,
entered by eye because the PDF's text layer scrambles Bengali vowel signs). Pre-Intermediate rows are dropped. Writes
data/kanji/cards.json. Nothing here reads or writes the vocabulary decks (data/cards.json).

Checks that stop the build: every kept row has exactly one Bangla line with the same id and word; the Bangla text
has the same consonants as the PDF's scrambled text layer (so a line cannot be skipped, shifted or retyped wrongly),
except the ids listed in data/kanji/bn_corrections.tsv, where the PDF's own Bangla was corrected on purpose.

Usage: build_kanji.py DATA_DIR
"""
import collections
import json
import os
import re
import sys
import unicodedata

BOOKS = [("starter", "KS", "Starter", "入門", "স্টার্টার"), ("elementary1", "KE1", "Elementary 1", "初級1", "এলিমেন্টারি ১"),
         ("elementary2", "KE2", "Elementary 2", "初級2", "এলিমেন্টারি ২")]
EXCLUDED = "preintermediate"
KANJI = re.compile(r"[㐀-䶿一-鿿豈-﫿々]")
KANA = re.compile(r"[぀-ゟ゠-ヿ]")
BENGALI = re.compile(r"[ঀ-৿]")


def skeleton(text, raw=False):
    """The consonants of a Bangla string, order ignored. The PDF's text layer keeps consonants and loses vowel signs."""
    if raw:
        # in the scrambled layer "7" stands for a vowel sign, "$" for থ, "%" for দ and "র্থ" for a reph
        text = text.replace("র্থ", "র").replace("$", "থ").replace("%", "দ").replace("7", "")
        text = re.sub(r"[\u0100-\u024f]", "", text)  # other stand-ins for vowel signs
    text = unicodedata.normalize("NFD", text)
    keep = [ch for ch in text if ("ক" <= ch <= "হ") or ch == "ৎ" or KANJI.match(ch) or ch.isascii() and ch.isalnum()]
    return sorted(keep)


def read_tsv(path):
    rows = []
    if not os.path.exists(path):
        return rows
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if line.strip():
            parts = line.split("\t")
            if len(parts) < 3:
                raise SystemExit("%s line %d: expected 3 tab-separated fields" % (path, n))
            rows.append(parts)
    return rows


def kana_lines_up(word, reading):
    """True when the kana printed in the word appear in the reading in the same order (okurigana check)."""
    pattern = ""
    for ch in word:
        if KANA.match(ch) or ch in "～（）":
            pattern += re.escape(ch)
        elif not pattern.endswith("(.+)"):
            pattern += "(.+)"
    return re.fullmatch(pattern, reading) is not None


def main():
    data_dir = sys.argv[1]
    kdir = os.path.join(data_dir, "kanji")
    raw = json.load(open(os.path.join(kdir, "raw.json"), encoding="utf-8"))
    bn = {r[0]: (r[1], r[2].strip()) for r in read_tsv(os.path.join(kdir, "bn.tsv"))}
    corrected = {r[0]: r for r in read_tsv(os.path.join(kdir, "bn_corrections.tsv"))}
    kept = [r for r in raw["rows"] if r["book"] != EXCLUDED]
    dropped = len(raw["rows"]) - len(kept)
    out = {"source": raw["pdf"], "pdf_rows": len(raw["rows"]), "excluded_preintermediate": dropped, "books": []}
    problems, used = [], set()
    for key, code, title, jp, bn_title in BOOKS:
        lessons = []
        for n in range(1, 19):
            rows = [r for r in kept if r["book"] == key and r["lesson"] == n]
            cards = []
            for i, r in enumerate(rows, 1):
                cid = "%s-L%02d-%02d" % (code, n, i)
                if cid not in bn:
                    problems.append("no Bangla line for " + cid)
                    continue
                word, text = bn[cid]
                used.add(cid)
                if word != r["word"]:
                    problems.append("%s: bn.tsv has %r, the PDF row is %r" % (cid, word, r["word"]))
                if not BENGALI.search(text) or chr(0x2014) in text:
                    problems.append("%s: bad Bangla text" % cid)
                if cid not in corrected and skeleton(text) != skeleton(r["bn_raw"], raw=True):
                    problems.append("%s %s: Bangla differs from the PDF text layer: %r vs %r" % (cid, word, text, r["bn_raw"]))
                if not KANJI.search(r["word"]) or KANJI.search(r["reading"]) or not kana_lines_up(r["word"], r["reading"]):
                    problems.append("%s: word and reading do not line up: %s / %s" % (cid, r["word"], r["reading"]))
                cards.append({"id": cid, "w": r["word"], "r": r["reading"], "bn": text, "p": r["page"]})
            lessons.append({"n": n, "title": rows[0]["lesson_title"] if rows else "", "cards": cards})
        out["books"].append({"key": key, "title": title, "jp": jp, "bn": bn_title, "lessons": lessons})
    extra = set(bn) - used
    if extra:
        problems.append("bn.tsv lines with no PDF row: " + ", ".join(sorted(extra)[:10]))
    if problems:
        for p in problems[:40]:
            print("PROBLEM:", p)
        raise SystemExit("%d problem(s); nothing written" % len(problems))
    with open(os.path.join(kdir, "cards.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    total = 0
    for b in out["books"]:
        c = sum(len(l["cards"]) for l in b["lessons"])
        total += c
        print(b["title"], c, "empty lessons:", [l["n"] for l in b["lessons"] if not l["cards"]])
    print("kept", total, "of", len(raw["rows"]), "PDF rows; Pre-Intermediate dropped:", dropped, "; corrected on purpose:", len(corrected))


if __name__ == "__main__":
    main()
