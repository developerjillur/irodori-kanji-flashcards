#!/usr/bin/env python3
"""Write the single-file app: the template with the deck data inlined.

Usage: build_app.py DATA_DIR TEMPLATE OUT_HTML
"""
import json
import sys

MARK = "/*__DATA__*/null"
KMARK = "/*__KANJI__*/null"


def main():
    data_dir, template, out = sys.argv[1], sys.argv[2], sys.argv[3]
    data = json.load(open(data_dir + "/cards.json", encoding="utf-8"))
    slim = {"books": []}
    for b in data["books"]:
        lessons = []
        for l in b["lessons"]:
            cards = [{k: c[k] for k in ("id", "w", "r", "bn", "en", "g", "x", "rp", "rf")} for c in l["cards"]]
            lessons.append({"n": l["n"], "entries": l["entries"], "cards": cards})
        slim["books"].append({"key": b["key"], "title": b["title"], "jp": b["jp"], "bn": b["bn"], "lessons": lessons})
    blob = json.dumps(slim, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = open(template, encoding="utf-8").read()
    if html.count(MARK) != 1:
        raise SystemExit("template must contain the data marker exactly once")
    html = html.replace(MARK, blob)
    # the separate Irodori Kanji category: its own file in, its own constant out
    kpath = data_dir + "/kanji/cards.json"
    kdata = json.load(open(kpath, encoding="utf-8"))
    kslim = {"books": [{"key": kb["key"], "title": kb["title"], "jp": kb["jp"], "bn": kb["bn"],
                        "lessons": [{"n": l["n"], "title": l["title"],
                                     "cards": [{k: c[k] for k in ("id", "w", "r", "bn")} for c in l["cards"]]}
                                    for l in kb["lessons"]]} for kb in kdata["books"]]}
    kblob = json.dumps(kslim, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    if html.count(KMARK) != 1:
        raise SystemExit("template must contain the kanji data marker exactly once")
    html = html.replace(KMARK, kblob)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(out, "%.0f KB" % (len(html.encode("utf-8")) / 1024),
          "cards", sum(len(l["cards"]) for b in slim["books"] for l in b["lessons"]),
          "kanji cards", sum(len(l["cards"]) for kb in kslim["books"] for l in kb["lessons"]))


if __name__ == "__main__":
    main()
