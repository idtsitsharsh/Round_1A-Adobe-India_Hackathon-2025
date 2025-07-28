import os
import re
import string

def is_title_candidate(span, page_num):
    if page_num != 0:
        return False

    text = span["text"].strip()
    if not text or not any(c.isalpha() for c in text):
        return False
    if sum(1 for c in text if c in string.punctuation) / len(text) > 0.6:
        return False
    if re.fullmatch(r'[^A-Za-z0-9]{3,}', text):
        return False
    lowered = text.lower()
    if any(s in lowered for s in ["www.", ".com", ".org", ".net"]):
        return False
    if text.isupper() and len(text.split()) <= 5:
        return False

    bbox_width = span["bbox"][2] - span["bbox"][0]
    return span["size"] >= 10 and bbox_width >= 100

def extract_title(doc, filename="Untitled"):
    title_spans = []
    page = doc[0]
    blocks = page.get_text("dict")["blocks"]

    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                if is_title_candidate(span, 0):
                    title_spans.append({
                        "text": span["text"].strip(),
                        "y": span["bbox"][1],
                        "font_size": span["size"]
                    })

    if not title_spans:
        meta_title = doc.metadata.get("title")
        if meta_title and len(meta_title.split()) >= 3:
            return meta_title.strip()
        name_title = os.path.splitext(os.path.basename(filename))[0].replace("_", " ")
        return name_title

    max_font = max(s["font_size"] for s in title_spans)
    filtered = [s for s in title_spans if s["font_size"] >= max_font - 1]
    filtered.sort(key=lambda s: s["y"])

    seen = set()
    lines = []
    for span in filtered:
        t = span["text"]
        if t not in seen:
            lines.append(t)
            seen.add(t)

    return " ".join(lines) if lines else "Untitled"