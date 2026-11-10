#!/usr/bin/env python3
"""Join the entry list with the Bangla meanings and write the deck data.

Reads data/entries.json and data/tr/out_*.tsv (id, word, Bangla; one line per distinct word and
PDF meaning, keyed by the id of its first appearance). A line whose id or word does not match the
entry list stops the build. Writes data/cards.json: book -> lesson -> cards, kanji entries only.

Usage: build_cards.py DATA_DIR
"""
import glob
import json
import os
import re
import sys

BOOKS = [
    ("starter", "Starter", "入門", "স্টার্টার"),
    ("elementary1", "Elementary 1", "初級1", "এলিমেন্টারি ১"),
    ("elementary2", "Elementary 2", "初級2", "এলিমেন্টারি ২"),
]
BENGALI_RE = re.compile(r"[ঀ-৿]")
FIX_FILE = "bn_fixes.tsv"  # optional later corrections: id, word, Bangla


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) != 3:
                raise SystemExit("%s line %d: expected 3 tab-separated fields, got %d" % (path, n, len(parts)))
            rows.append(parts)
    return rows


def main():
    data_dir = sys.argv[1]
    entries = json.load(open(os.path.join(data_dir, "entries.json"), encoding="utf-8"))
    by_id = {e["id"]: e for e in entries}
    bn = {}
    files = sorted(glob.glob(os.path.join(data_dir, "tr", "out_*.tsv")))
    fix = os.path.join(data_dir, "tr", FIX_FILE)
    if os.path.exists(fix):
        files.append(fix)
    for path in files:
        for eid, word, text in read_tsv(path):
            e = by_id.get(eid)
            if e is None:
                raise SystemExit("%s: unknown id %s" % (path, eid))
            if e["word"] != word:
                raise SystemExit("%s: id %s is %r in the entry list, not %r" % (path, eid, e["word"], word))
            text = text.strip()
            if not BENGALI_RE.search(text):
                raise SystemExit("%s: id %s has no Bangla text" % (path, eid))
            if chr(0x2014) in text or (" " + chr(0x2013) + " ") in text:
                raise SystemExit("%s: id %s has a dash that is not allowed" % (path, eid))
            bn[(e["word"], e["english"])] = text
    missing = []
    out = {"books": []}
    for key, title, jp, bn_title in BOOKS:
        lessons = []
        for n in range(1, 19):
            es = [e for e in entries if e["book"] == key and e["lesson"] == n]
            cards = []
            for e in es:
                if not e["has_kanji"]:
                    continue
                text = bn.get((e["word"], e["english"]))
                if text is None:
                    missing.append(e["id"])
                    continue
                cards.append({
                    "id": e["id"], "w": e["word"], "r": e["reading"], "bn": text, "en": e["english"],
                    "g": e["verb_group"], "x": int(e["expression"]), "rp": int(e["repeated"]),
                    "rf": int(e["reference"]), "p": e["pdf_page"],
                })
            lessons.append({"n": n, "entries": len(es), "cards": cards})
        out["books"].append({"key": key, "title": title, "jp": jp, "bn": bn_title, "lessons": lessons})
    if missing:
        raise SystemExit("no Bangla meaning for %d entries: %s" % (len(missing), ", ".join(missing[:20])))
    with open(os.path.join(data_dir, "cards.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    for b in out["books"]:
        print(b["title"], "lessons", len(b["lessons"]), "cards", sum(len(l["cards"]) for l in b["lessons"]))
    print("distinct meanings", len(bn))


if __name__ == "__main__":
    main()
