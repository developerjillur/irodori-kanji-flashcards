# Irodori Kanji Flashcards

Irodori-র তিন বইয়ের (Starter, Elementary 1, Elementary 2) প্রতিটা lesson-এর শুধু kanji থাকা শব্দ নিয়ে flashcard app।
সামনে kanji বানান (PDF-এ যেমন ছাপা), পেছনে hiragana reading আর বাংলা অর্থ।

## চালানো

`index.html` ফাইলটা browser-এ খুলুন (double click)। Internet লাগে না, সব data ওই এক ফাইলের ভেতরে।

- পথ: বই → Lesson 1 থেকে 18 → flashcard।
- Card-এ চাপ দিলে বা `Space` চাপলে উল্টায়; `←` `→` দিয়ে আগের ও পরের; `S` দিয়ে এলোমেলো (shuffle)।
- "English অর্থও দেখাও" চালু করলে PDF-এর নিজের English অর্থটাও পেছনে দেখায়।
- পেছনের ছোট tag: ক্রিয়ার গ্রুপ (PDF-এর ［1］［2］［3］), বাক্য বা expression, ↺ (আগের lesson-এও এসেছে), reference শব্দ (PDF-এ ধূসর রঙে ছাপা)।

## কোন PDF কোন বই

প্রতিটা PDF-এর প্রতি পাতার নিচের লেখা থেকে নিশ্চিত করা:

| ফাইল | পাতার নিচে লেখা | বই |
|---|---|---|
| `wordlist_X.pdf` (74 পাতা) | 入門 ことばリスト | Starter |
| `wordlist_Y.pdf` (62 পাতা) | 初級1 ことばリスト | Elementary 1 |
| `wordlist_Z.pdf` (88 পাতা) | 初級2 ことばリスト | Elementary 2 |

তিনটাই The Japan Foundation-এর ことばリスト, Ver. 2021/10/01, অর্থ English-এ।

## Data কোথা থেকে কীভাবে এল

1. `scripts/extract.py`: PDF-এর text layer পড়ে (PyMuPDF)। PDF নিজেই প্রতিটা সারির প্রতিটা ঘর আলাদা rectangle হিসেবে আঁকে,
   তাই কোন লেখা কোন সারির কোন column-এ, সেটা অনুমান নয়, মাপ থেকে আসে। Lesson নম্বর আসে পাতার নিচের `L4 - 2` থেকে।
2. `scripts/build_data.py`: শব্দ পরিষ্কার করে (ক্রিয়ার গ্রুপ চিহ্ন আলাদা রাখে), reading নেয় PDF-এর accent column থেকে
   (↓ ○ △ চিহ্ন বাদ দিয়ে), আর শব্দের উপরে ছাপা furigana-র সাথে মিলিয়ে দেখে। Kanji আছে কি না code দিয়ে ঠিক হয়
   (Unicode CJK ideograph আর 々), চোখে নয়।
3. `data/tr/out_*.tsv`: বাংলা অর্থ, PDF-এর ওই lesson-এর English অর্থ ধরে লেখা। সংশোধন থাকলে `data/tr/bn_fixes.tsv`।
4. `scripts/build_cards.py` আর `scripts/build_app.py`: deck data আর `index.html` বানায়।
5. `scripts/verify.py`: মিলিয়ে দেখে আর `out/VERIFY.md` লেখে।

নতুন করে বানাতে (PyMuPDF লাগে; PDF শুধু data হিসেবে পড়া হয়, তাই `-I`):

```bash
python3 -I scripts/extract.py ~/Downloads/wordlist_X.pdf data/raw_X.json
python3 -I scripts/extract.py ~/Downloads/wordlist_Y.pdf data/raw_Y.json
python3 -I scripts/extract.py ~/Downloads/wordlist_Z.pdf data/raw_Z.json
python3 -I scripts/build_data.py data
python3 -I scripts/build_cards.py data
python3 -I scripts/build_app.py data scripts/app_template.html index.html
python3 -I scripts/verify.py
python3 -I -m unittest discover -s tests
```

একটা বাংলা অর্থ বদলাতে: `data/tr/bn_fixes.tsv`-তে এক লাইন যোগ করুন (`id<TAB>শব্দ<TAB>নতুন বাংলা`), তারপর শেষ চারটা command চালান।

## যা জানা দরকার

- "শব্দ" বলতে word list-এর প্রতিটা সারি: একক শব্দ, বাক্য বা expression, আর `～語（中国語）`-এর মতো pattern, সবই।
  যার ছাপা রূপে অন্তত একটা kanji আছে সেটাই deck-এ আছে।
- একই শব্দ PDF একাধিক lesson-এ দিলে (↺ চিহ্ন) প্রতিটা lesson-এর deck-এ আছে, কারণ PDF ওখানে দিয়েছে।
- যাচাইয়ের পুরো table আর সন্দেহের তালিকা: `out/VERIFY.md` আর `REPORT.md`।
