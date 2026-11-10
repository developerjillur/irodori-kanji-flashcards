#!/usr/bin/env python3
"""Extract every entry of an Irodori word-list PDF into rows.

The PDF draws each table row as one filled rectangle per column, so the cell rectangles give the
exact row and column of every text span. No text is guessed: a span that falls outside every cell
of a word page is reported in the "stray" list.

Usage: extract.py PDF OUT.json
Run with the interpreter's -I flag; the PDF is data only.
"""
import json
import re
import sys
import unicodedata

import fitz  # PyMuPDF

FOOTER_RE = re.compile(r"L\s*(\d+)\s*-\s*(\d+)")
BOOKS = {"入門": "starter", "初級1": "elementary1", "初級2": "elementary2"}
ACCENT_MARKS = "↓○△〇◯"
RUBY_MAX = 7.6  # ruby in the word column is 6 pt, base text 12 pt


def norm(text):
    """Map Kangxi and CJK radical code points to the ordinary ideograph; leave everything else."""
    out = []
    for ch in text:
        if 0x2E80 <= ord(ch) <= 0x2FDF:
            out.append(unicodedata.normalize("NFKC", ch))
        else:
            out.append(ch)
    return "".join(out)


def page_spans(page):
    spans = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for s in line["spans"]:
                if not s["text"].strip():
                    continue
                x0, y0, x1, y1 = s["bbox"]
                spans.append({
                    "text": norm(s["text"]), "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                    "size": round(s["size"], 1), "font": s["font"], "color": "%06x" % s["color"],
                })
    return spans


def page_rows(page):
    """Rows of the table: groups of cell rectangles that share the same top and bottom."""
    cells = {}
    icons = []
    for g in page.get_drawings():
        r = g["rect"]
        # the expression icon (speech bubble) and the repeated-word icon are small drawings
        if 3 < r.width < 12 and 3 < r.height < 12:
            icons.append((r.x0, r.y0, r.x1, r.y1, len(g["items"])))
        if g["type"] != "f":
            continue
        for it in g["items"]:
            if it[0] != "re":
                continue
            q = it[1]
            if q.height < 12 or q.height > 200 or q.width > 400 or q.width < 40:
                continue
            key = (round(q.y0, 1), round(q.y1, 1))
            cells.setdefault(key, set()).add((round(q.x0, 1), round(q.x1, 1)))
    rows = []
    for (y0, y1), cols in sorted(cells.items()):
        cols = sorted(cols)
        if len(cols) < 3:
            continue
        rows.append({"y0": y0, "y1": y1, "cols": cols})
    return rows, icons


def lines_of(spans, tol=3.0):
    """Group spans into text lines by their top edge, top to bottom, each line left to right."""
    lines = []
    for s in sorted(spans, key=lambda s: (s["y0"], s["x0"])):
        for ln in lines:
            if abs(ln["y"] - s["y0"]) <= tol:
                ln["spans"].append(s)
                break
        else:
            lines.append({"y": s["y0"], "spans": [s]})
    for ln in lines:
        ln["spans"].sort(key=lambda s: s["x0"])
    lines.sort(key=lambda ln: ln["y"])
    return lines


def cell_text(spans, sep=""):
    return sep.join("".join(s["text"] for s in ln["spans"]) for ln in lines_of(spans))


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    doc = fitz.open(pdf)
    result = {"pdf": pdf.rsplit("/", 1)[-1], "pages": doc.page_count, "book": None,
              "skipped_pages": [], "rows": [], "stray": [], "headings": []}
    for pno in range(doc.page_count):
        page = doc[pno]
        spans = page_spans(page)
        footer_lesson = None
        book = None
        foot = [s for s in spans if s["y0"] > 770 and s["size"] > 12]
        foot_text = "".join(s["text"] for s in sorted(foot, key=lambda s: s["x0"])).replace(" ", "").replace("　", "")
        m = FOOTER_RE.search(foot_text)
        if m:
            footer_lesson = (int(m.group(1)), int(m.group(2)))
        for jp, key in BOOKS.items():
            if foot_text.startswith(jp + "ことばリスト"):
                book = key
        if footer_lesson is None or book is None:
            head = " ".join(s["text"] for s in sorted(spans, key=lambda s: (s["y0"], s["x0"]))[:6])
            result["skipped_pages"].append({"page": pno + 1, "head": head[:120]})
            continue
        if result["book"] is None:
            result["book"] = book
        elif result["book"] != book:
            raise SystemExit("two books in one PDF: page %d" % (pno + 1))
        lesson, lpage = footer_lesson
        rows, icons = page_rows(page)
        # an entry whose row has no drawn cell rectangle: word-column text in the entry font outside every row
        if rows:
            col0 = rows[0]["cols"][0]
            for s in sorted(spans, key=lambda s: s["y0"]):
                cy = (s["y0"] + s["y1"]) / 2
                if s["y0"] > 770 or any(r["y0"] - 0.5 <= cy < r["y1"] + 0.5 for r in rows):
                    continue
                if (s["font"] == "UDShinGoPro-Medium" and s["size"] in (10.0, 12.0)
                        and s["color"] in ("231f20", "9d9fa2", "808285") and col0[0] <= s["x0"] < col0[1]):
                    y0 = s["y0"] - 8
                    y1 = s["y0"] + 24
                    for r in rows:
                        if r["y0"] > s["y0"]:
                            y1 = min(y1, r["y0"])
                        if r["y1"] <= s["y0"]:
                            y0 = max(y0, r["y1"])
                    rows.append({"y0": y0, "y1": y1, "cols": rows[0]["cols"], "pseudo": True})
                    result["stray"].append({"page": pno + 1, "why": "entry without a drawn row, recovered as a row",
                                            "text": s["text"]})
            rows.sort(key=lambda r: r["y0"])
        used = set()
        for ri, row in enumerate(rows):
            cols = row["cols"]
            cellspans = [[] for _ in cols]
            for si, s in enumerate(spans):
                cy = (s["y0"] + s["y1"]) / 2
                if not (row["y0"] - 0.5 <= cy < row["y1"] + 0.5):
                    continue
                cx = (s["x0"] + s["x1"]) / 2
                for ci, (cx0, cx1) in enumerate(cols):
                    if cx0 <= cx < cx1:
                        cellspans[ci].append(s)
                        used.add(si)
                        break
            wspans = cellspans[0]
            base = [s for s in wspans if s["size"] > RUBY_MAX]
            ruby = [s for s in wspans if s["size"] <= RUBY_MAX]
            if not base:
                if any(cellspans):
                    result["stray"].append({"page": pno + 1, "why": "row without base word text",
                                            "text": " | ".join(cell_text(c) for c in cellspans)})
                continue
            word_lines = lines_of(base)
            # ruby goes with the base line right below it
            ruby_by_line = [[] for _ in word_lines]
            for r in ruby:
                best = None
                for li, ln in enumerate(word_lines):
                    d = ln["y"] - r["y0"]
                    if -1 <= d <= 9 and (best is None or d < best[0]):
                        best = (d, li)
                if best is None:
                    result["stray"].append({"page": pno + 1, "why": "ruby without base line", "text": r["text"]})
                    continue
                ruby_by_line[best[1]].append(r)
            word_raw = "".join("".join(s["text"] for s in ln["spans"]) for ln in word_lines)
            ruby_list = []
            for li in range(len(word_lines)):
                for r in sorted(ruby_by_line[li], key=lambda r: r["x0"]):
                    ruby_list.append(r["text"])
            acc_i = len(cols) - 2
            entry = {
                "book": book, "lesson": lesson, "lesson_page": lpage, "pdf_page": pno + 1,
                "y": row["y0"], "ncols": len(cols),
                "word_raw": word_raw,
                "parts": [[s["text"], s["size"], s["color"]] for ln in word_lines for s in ln["spans"]],
                "word_lines": len(word_lines),
                "ruby": ruby_list,
                "accent_raw": cell_text(cellspans[acc_i]),
                "english": re.sub(r"\s+", " ", cell_text(cellspans[-1], sep="\n").replace("-\n", "-").replace("\n", " ")).strip(),
                "romaji": re.sub(r"\s+", " ", cell_text(cellspans[1], sep=" ")).strip() if len(cols) == 4 else "",
                "colors": sorted({s["color"] for s in base}),
                "fonts": sorted({s["font"] + "@" + str(s["size"]) for s in base}),
                "expr": any(row["y0"] <= (i[1] + i[3]) / 2 <= row["y1"] and i[0] < cols[0][0] + 14 for i in icons),
                "icons": [[round(i[0], 1), i[4]] for i in icons if row["y0"] <= (i[1] + i[3]) / 2 <= row["y1"]],
            }
            result["rows"].append(entry)
        # anything on a word page that sits in the table area but in no row
        for si, s in enumerate(spans):
            if si in used or s["y0"] > 770:
                continue
            result["headings"].append({"page": pno + 1, "lesson": lesson, "y": round(s["y0"], 1), "x": round(s["x0"], 1),
                                       "size": s["size"], "font": s["font"], "color": s["color"], "text": s["text"]})
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    lessons = sorted({r["lesson"] for r in result["rows"]})
    print(result["pdf"], result["book"], "rows", len(result["rows"]), "lessons", lessons,
          "skipped", [p["page"] for p in result["skipped_pages"]], "stray", len(result["stray"]),
          "outside-row spans", len(result["headings"]))


if __name__ == "__main__":
    main()
