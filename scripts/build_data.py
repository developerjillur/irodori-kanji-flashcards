#!/usr/bin/env python3
"""Turn the raw rows of the three word lists into one clean entry list.

Reads data/raw_X.json, raw_Y.json, raw_Z.json (from extract.py) and writes data/entries.json:
every entry of every lesson, with the word as printed, the reading taken from the PDF's accent
column (accent marks removed), the PDF's English meaning, flags, and whether it contains kanji.
The reading is cross-checked against the furigana printed above the word; a disagreement is
recorded in the entry's "check" field, never silently fixed.

Usage: build_data.py DATA_DIR
"""
import json
import os
import re
import sys

BOOK_ORDER = ["starter", "elementary1", "elementary2"]
BOOK_CODE = {"starter": "S", "elementary1": "E1", "elementary2": "E2"}
ACCENT_MARKS = "↓○△〇◯"  # ▲ is not an accent mark: the PDF prints it as a placeholder in one entry
KANJI_RE = re.compile(r"[㐀-䶿一-鿿豈-﫿々]")
KANA_RE = re.compile(r"[぀-ゟ゠-ヿ]")
VERB_RE = re.compile(r"［([123])］")
PUNCT = set("（）()～／？！、。…・「」 　,.?!-％%")
GRAY = {"9d9fa2", "808285"}


def has_kanji(text):
    return bool(KANJI_RE.search(text))


def clean_word(raw):
    text = re.sub(r"[\x00-\x1f]", "", raw)
    groups = VERB_RE.findall(text)
    text = VERB_RE.sub("", text)
    text = text.replace("(", "（").replace(")", "）")
    # the PDF sets a thin gap between a digit or Latin letter and Japanese text; it is layout, not spelling
    text = re.sub(r"(?<=[^\x00-\x7f]) +", "", text)
    text = re.sub(r" +(?=[^\x00-\x7f])", "", text)
    text = re.sub(r"　+", "　", text)
    text = re.sub(r"　?（", "（", text)
    return text.strip(" 　"), groups


def split_top(text, sep="／"):
    parts, depth, cur = [], 0, ""
    for ch in text:
        if ch == "（":
            depth += 1
        elif ch == "）":
            depth -= 1
        if ch == sep and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def clean_reading(raw, word):
    text = re.sub(r"[\x00-\x1f]", "", raw)
    for m in ACCENT_MARKS:
        text = text.replace(m, "")
    text = text.replace("(", "（").replace(")", "）").replace("?", "？").replace("!", "！")
    text = re.sub(r"[ 　]+", " ", text)
    text = re.sub(r" ?([（）／？！]) ?", r"\1", text)
    text = text.strip()
    # "はんとし↓／はんとし○" gives the same kana twice: two accents of one reading. Fold them, but
    # only when the word itself does not list as many variants (昭和／昭 keeps both readings).
    if text.count("／") > word.count("／"):
        prev = None
        while prev != text:
            prev = text
            text = re.sub(r"(^|（|／)([^／（）]+)／\2(?=$|（|）|／)", r"\1\2", text)
        parts = split_top(text)
        if len(parts) > len(split_top(word)):
            dedup = []
            for part in parts:
                if not dedup or dedup[-1] != part:
                    dedup.append(part)
            text = "／".join(dedup)
    return text


def strip_punct(text):
    return "".join(ch for ch in text if ch not in PUNCT)


def check_reading(word, reading, ruby):
    """Compare the reading with the printed furigana. Returns '' when they agree."""
    w = strip_punct(word)
    r = strip_punct(reading)
    rb = [strip_punct(x) for x in ruby if strip_punct(x)]
    if KANJI_RE.search(reading):
        return "reading contains kanji"
    # runs of non-kana characters are what the furigana covers
    tokens = []
    for ch in w:
        kana = bool(KANA_RE.match(ch))
        if tokens and tokens[-1][0] == kana:
            tokens[-1][1] += ch
        else:
            tokens.append([kana, ch])
    runs = [t for t in tokens if not t[0]]
    if not runs:
        return "" if w == r else "kana word differs from reading"
    if len(rb) == len(runs):
        it = iter(rb)
        built = "".join(t[1] if t[0] else next(it) for t in tokens)
        if built == r:
            return ""
    pattern = "".join(re.escape(t[1]) if t[0] else "(.+)" for t in tokens)
    m = re.fullmatch(pattern, r)
    if not m:
        return "kana in the word does not line up with the reading"
    if not rb:
        return "no furigana printed for a non-kana part" if has_kanji(w) else ""
    joined = "".join(rb)
    # try every split of the reading that fits the pattern: accept when one equals the furigana
    lazy = re.fullmatch("".join(re.escape(t[1]) if t[0] else "(.+?)" for t in tokens), r)
    for mm in (m, lazy):
        if mm and "".join(mm.groups()) == joined:
            return ""
    # furigana printed only for some runs (digits and Latin letters often carry none)
    rest = "".join(m.groups())
    pos = 0
    for x in rb:
        k = rest.find(x, pos)
        if k < 0:
            return "furigana %s not found in the reading" % "+".join(rb)
        pos = k + len(x)
    return "partial furigana (ok in order)"


def main():
    data_dir = sys.argv[1]
    entries = []
    report = {"books": {}}
    for letter in "XYZ":
        raw = json.load(open(os.path.join(data_dir, "raw_%s.json" % letter), encoding="utf-8"))
        book = raw["book"]
        rows = [r for r in raw["rows"] if not (r["colors"] == ["ffffff"] and r["word_raw"].strip() == "ことば")]
        headers = len(raw["rows"]) - len(rows)
        rows.sort(key=lambda r: (r["lesson"], r["pdf_page"], r["y"]))
        seq = {}
        for r in rows:
            word, groups = clean_word(r["word_raw"])
            reading = clean_reading(r["accent_raw"], word)
            main_colors = {p[2] for p in r["parts"] if p[1] >= 9.5 and p[0].strip("\x07\t ")}
            icons = r["icons"]
            n = seq[r["lesson"]] = seq.get(r["lesson"], 0) + 1
            head = word.split("（")[0]
            e = {
                "id": "%s-L%02d-%03d" % (BOOK_CODE[book], r["lesson"], n),
                "book": book, "lesson": r["lesson"], "seq": n,
                "word": word, "reading": reading, "english": r["english"],
                "romaji": r.get("romaji", ""),
                "verb_group": groups[0] if groups else "",
                "expression": bool(r["expr"]),
                "repeated": any(i[1] != 7 for i in icons),
                "reference": bool(main_colors) and main_colors <= GRAY,
                "has_kanji": has_kanji(word),
                "kanji_only_in_example": has_kanji(word) and not has_kanji(head),
                "ruby": r["ruby"],
                "pdf": raw["pdf"], "pdf_page": r["pdf_page"],
            }
            e["check"] = check_reading(word, reading, r["ruby"])
            entries.append(e)
        report["books"][book] = {
            "pdf": raw["pdf"], "pages": raw["pages"], "header_rows": headers,
            "skipped_pages": raw["skipped_pages"], "recovered": raw["stray"],
        }
    with open(os.path.join(data_dir, "entries.json"), "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(data_dir, "extract_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    for book in BOOK_ORDER:
        es = [e for e in entries if e["book"] == book]
        ks = [e for e in es if e["has_kanji"]]
        print(book, "entries", len(es), "with kanji", len(ks), "lessons", len({e["lesson"] for e in es}),
              "header rows dropped", report["books"][book]["header_rows"])
    flagged = [e for e in entries if e["check"]]
    print("reading checks flagged:", len(flagged))


if __name__ == "__main__":
    main()
