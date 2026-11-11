#!/usr/bin/env python3
"""Extract the Irodori kanji-word list PDF (word, furigana, Bangla column) into rows per book and lesson.

The PDF is a three-column table under lesson headings such as
"Starter (入門) · Lesson 3", then a long dash and the lesson title. The Japanese word and the furigana come out of the text layer
intact. The Bangla column does not (the PDF's Bengali font has no usable character map for vowel signs), so it is kept
only as "bn_raw", a hint; the real Bangla text is entered by eye in data/kanji/bn.tsv.

Usage: extract_kanji.py PDF OUT.json      (run with the interpreter's -I flag; the PDF is data only)
"""
import json
import re
import sys

import fitz  # PyMuPDF

HEAD_RE = re.compile(r"^(Starter|Elementary 1|Elementary 2|Pre-Intermediate)\s*\((入門|初級1|初級2|初中級)\)\s*·\s*Lesson\s*(\d+)\s*[" + chr(0x2014) + r"\-]\s*(.*)$")
BOOK_KEY = {"Starter": "starter", "Elementary 1": "elementary1", "Elementary 2": "elementary2",
            "Pre-Intermediate": "preintermediate"}
COL2_X, COL3_X = 195.0, 325.0


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    doc = fitz.open(pdf)
    rows, problems = [], []
    book = lesson = title = None
    for pno in range(doc.page_count):
        spans = []
        for b in doc[pno].get_text("dict")["blocks"]:
            if b["type"] != 0:
                continue
            for ln in b["lines"]:
                for s in ln["spans"]:
                    if s["text"].strip():
                        spans.append({"x": s["bbox"][0], "y": s["bbox"][1], "size": round(s["size"], 1),
                                      "font": s["font"], "text": s["text"]})
        # group into visual lines (CJK and Bengali spans of one line differ by about 2 pt in their top edge)
        spans.sort(key=lambda s: (s["y"], s["x"]))
        lines = []
        for s in spans:
            if lines and abs(lines[-1]["y"] - s["y"]) <= 4.0:
                lines[-1]["spans"].append(s)
            else:
                lines.append({"y": s["y"], "spans": [s]})
        for ln in lines:
            ln["spans"].sort(key=lambda s: s["x"])
            text = "".join(s["text"] for s in ln["spans"]).strip()
            bold = all("Bold" in s["font"] for s in ln["spans"])
            if ln["y"] > 800 or text.startswith("Irodori Kanji") or "ふりがな · Furigana" in text:
                continue
            m = HEAD_RE.match(re.sub(r"\s+", " ", text)) if bold else None
            if m:
                book, lesson, title = BOOK_KEY[m.group(1)], int(m.group(3)), m.group(4).strip()
                continue
            if book is None:
                continue  # the intro note before the first lesson heading
            c1 = "".join(s["text"] for s in ln["spans"] if s["x"] < COL2_X).strip()
            c2 = "".join(s["text"] for s in ln["spans"] if COL2_X <= s["x"] < COL3_X).strip()
            c3 = "".join(s["text"] for s in ln["spans"] if s["x"] >= COL3_X).strip()
            if c1 and c2:
                rows.append({"book": book, "lesson": lesson, "lesson_title": title, "word": c1, "reading": c2,
                             "bn_raw": c3, "page": pno + 1, "y": round(ln["y"], 1)})
            elif rows and rows[-1]["page"] == pno + 1 and ln["y"] - rows[-1]["y"] < 40 and not c1:
                # a wrapped second line of the furigana or Bangla cell
                rows[-1]["reading"] += c2
                rows[-1]["bn_raw"] += " " + c3
                rows[-1]["wrapped"] = True
            else:
                problems.append({"page": pno + 1, "y": round(ln["y"], 1), "text": text})
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"pdf": pdf.rsplit("/", 1)[-1], "pages": doc.page_count, "rows": rows, "problems": problems},
                  fh, ensure_ascii=False, indent=1)
    by = {}
    for r in rows:
        by.setdefault(r["book"], {}).setdefault(r["lesson"], 0)
        by[r["book"]][r["lesson"]] += 1
    print("rows", len(rows), "problems", len(problems))
    for b, d in by.items():
        print(b, sum(d.values()), dict(sorted(d.items())))


if __name__ == "__main__":
    main()
