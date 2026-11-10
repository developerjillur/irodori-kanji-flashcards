#!/usr/bin/env python3
"""The done-check: prove the app's decks match the PDFs' entry lists.

Checks, from the files on disk (entries.json from the PDFs, cards.json, and the data inside index.html):
  - 3 books x 18 lessons, every lesson present in the entry list and in the app;
  - per lesson: entries with a kanji (counted again here with its own test) == cards in cards.json == cards in the app;
  - every card: its word has a kanji, its reading has none and is not empty, its Bangla meaning is not empty and is in
    Bengali script, its id belongs to that book and lesson, ids are unique, word and reading equal the entry list's;
  - no entry without kanji is in any deck, and no kanji entry is missing.
Writes out/VERIFY.md (the per-lesson table) and exits 1 on any failure.

Usage: verify.py   (run from the project folder)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KANJI = re.compile(r"[㐀-䶿一-鿿豈-﫿々]")
BENGALI = re.compile(r"[ঀ-৿]")
BOOKS = [("starter", "S", "Starter (入門)", "wordlist_X.pdf"), ("elementary1", "E1", "Elementary 1 (初級1)", "wordlist_Y.pdf"),
         ("elementary2", "E2", "Elementary 2 (初級2)", "wordlist_Z.pdf")]


def app_data(path):
    html = open(path, encoding="utf-8").read()
    m = re.search(r"const DATA = (\{.*?\});\n</script>", html, re.S)
    if not m:
        raise SystemExit("FAIL: no data found in " + path)
    return json.loads(m.group(1).replace("<\\/", "</"))


def main():
    fails = []
    entries = json.load(open(os.path.join(HERE, "data", "entries.json"), encoding="utf-8"))
    cards = json.load(open(os.path.join(HERE, "data", "cards.json"), encoding="utf-8"))
    app = app_data(os.path.join(HERE, "index.html"))
    by_id = {e["id"]: e for e in entries}
    if len(by_id) != len(entries):
        fails.append("duplicate entry ids")
    seen = set()
    lines = ["# Verification: decks against the PDF word lists", "",
             "Made by `scripts/verify.py` from `data/entries.json` (extracted from the PDFs), `data/cards.json` and the data",
             "inside `index.html`. \"PDF entries\" is every row of the lesson's word list; \"with kanji\" is counted here again",
             "with a Unicode test (CJK ideographs U+3400 to U+4DBF, U+4E00 to U+9FFF, U+F900 to U+FAFF, and 々).", ""]
    grand = [0, 0, 0]
    for bi, (key, code, title, pdf) in enumerate(BOOKS):
        cb = cards["books"][bi]
        ab = app["books"][bi]
        if cb["key"] != key or ab["key"] != key:
            fails.append("book order differs for " + key)
        if len(cb["lessons"]) != 18 or len(ab["lessons"]) != 18:
            fails.append("%s: not 18 lessons" % key)
        lines += ["## %s, from `%s`" % (title, pdf), "", "| Lesson | PDF entries | With kanji | Cards in deck | Match |", "|---|---|---|---|---|"]
        tot = [0, 0, 0]
        for n in range(1, 19):
            es = [e for e in entries if e["book"] == key and e["lesson"] == n]
            ks = [e for e in es if KANJI.search(e["word"])]
            cl = cb["lessons"][n - 1]["cards"]
            al = ab["lessons"][n - 1]["cards"]
            ok = bool(es) and len(ks) == len(cl) == len(al)
            if not es:
                fails.append("%s lesson %d: no entries" % (key, n))
            if [c["id"] for c in cl] != [e["id"] for e in ks]:
                ok = False
                fails.append("%s lesson %d: deck ids differ from the kanji entries" % (key, n))
            if [(c["id"], c["w"], c["r"], c["bn"]) for c in cl] != [(c["id"], c["w"], c["r"], c["bn"]) for c in al]:
                ok = False
                fails.append("%s lesson %d: the app's cards differ from cards.json" % (key, n))
            for c in al:
                e = by_id.get(c["id"])
                prefix = "%s-L%02d-" % (code, n)
                if c["id"] in seen:
                    fails.append("card id twice: " + c["id"])
                seen.add(c["id"])
                if e is None or not c["id"].startswith(prefix) or e["book"] != key or e["lesson"] != n:
                    fails.append("card %s is not an entry of %s lesson %d" % (c["id"], key, n))
                    continue
                if c["w"] != e["word"] or c["r"] != e["reading"]:
                    fails.append("card %s: word or reading differs from the entry list" % c["id"])
                if not KANJI.search(c["w"]):
                    fails.append("card %s: no kanji in %s" % (c["id"], c["w"]))
                if not c["r"].strip() or KANJI.search(c["r"]):
                    fails.append("card %s: bad reading %r" % (c["id"], c["r"]))
                if not BENGALI.search(c["bn"]) or chr(0x2014) in c["bn"]:
                    fails.append("card %s: bad Bangla meaning" % c["id"])
            lines.append("| %d | %d | %d | %d | %s |" % (n, len(es), len(ks), len(al), "yes" if ok else "NO"))
            if not ok and len(ks) != len(al):
                fails.append("%s lesson %d: %d kanji entries, %d cards" % (key, n, len(ks), len(al)))
            tot = [tot[0] + len(es), tot[1] + len(ks), tot[2] + len(al)]
        lines += ["| **Total** | **%d** | **%d** | **%d** | |" % tuple(tot), ""]
        grand = [grand[i] + tot[i] for i in range(3)]
    lines += ["**All three books: %d PDF entries, %d with kanji, %d cards.**" % tuple(grand), ""]
    all_kanji = {e["id"] for e in entries if KANJI.search(e["word"])}
    if seen != all_kanji:
        fails.append("%d kanji entries missing from the app, %d extra" % (len(all_kanji - seen), len(seen - all_kanji)))
    flagged = [e for e in entries if e["has_kanji"] and e["check"] and not e["check"].startswith("partial")]
    lines += ["## Readings where the PDF's furigana and its accent column do not line up mechanically", "",
              "The card uses the accent column (the PDF's full reading). These %d are listed for a human eye:" % len(flagged), "",
              "| Card | Word | Reading on the card | Furigana printed above the word | PDF page |", "|---|---|---|---|---|"]
    for e in flagged:
        lines.append("| %s | %s | %s | %s | %s p.%d |" % (e["id"], e["word"], e["reading"], " + ".join(e["ruby"]) or "(none)", e["pdf"], e["pdf_page"]))
    lines += ["", "Result: %s" % ("PASS" if not fails else "FAIL (%d)" % len(fails)), ""]
    for f in fails[:50]:
        lines.append("- " + f)
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    with open(os.path.join(HERE, "out", "VERIFY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("books 3, lessons 54, PDF entries %d, with kanji %d, cards %d" % tuple(grand))
    if fails:
        print("FAIL:", len(fails))
        for f in fails[:20]:
            print(" -", f)
        sys.exit(1)
    print("PASS: every lesson's kanji entries equal its deck; report in out/VERIFY.md")


if __name__ == "__main__":
    main()
