import fitz
from collections import defaultdict

def extract_spans(pdf_path):
    doc = fitz.open(pdf_path)
    raw_spans = []
    font_sizes = []
    font_size_word_map = defaultdict(int)

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue

            line_groups = defaultdict(list)

            for line in block["lines"]:
                spans = line["spans"]
                if not spans:
                    continue

                y_key = round(spans[0]["bbox"][1], 1)
                line_groups[y_key].extend(spans)

            for y_val in sorted(line_groups.keys()):
                current_line_spans = sorted(line_groups[y_val], key=lambda s: s["bbox"][0])

                temp_line = []
                merged_lines = []
                last_x = None

                for span in current_line_spans:
                    x0 = span["bbox"][0]
                    if last_x is not None and x0 - last_x > 50: 
                        merged_lines.append(temp_line)
                        temp_line = []
                    temp_line.append(span)
                    last_x = span["bbox"][2]

                if temp_line:
                    merged_lines.append(temp_line)

                for line_spans in merged_lines:
                    if not line_spans:
                        continue

                    line_text = " ".join(s["text"].strip() for s in line_spans if s["text"].strip())
                    font_sizes.extend([s.get("size", 0) for s in line_spans])

                    for s in line_spans:
                        text = s.get("text", "").strip()
                        size = s.get("size", 0)
                        font_size_word_map[size] += len(text.split())

                    line_bbox = [float("inf"), float("inf"), float("-inf"), float("-inf")]
                    line_fonts = []
                    line_sizes = []

                    for span in line_spans:
                        font_size = span.get("size", 0)
                        line_fonts.append(span.get("font", ""))
                        line_sizes.append(font_size)
                        x0, y0, x1, y1 = span["bbox"]
                        line_bbox[0] = min(line_bbox[0], x0)
                        line_bbox[1] = min(line_bbox[1], y0)
                        line_bbox[2] = max(line_bbox[2], x1)
                        line_bbox[3] = max(line_bbox[3], y1)

                    merged_text = " ".join(line_text.split())
                    if not merged_text:
                        continue

                    raw_spans.append({
                        "text": merged_text,
                        "size": round(sum(line_sizes) / len(line_sizes), 1),
                        "font": line_fonts[0] if line_fonts else "",
                        "bold": any("bold" in f.lower() for f in line_fonts),
                        "italic": any("italic" in f.lower() or "oblique" in f.lower() for f in line_fonts),
                        "caps": merged_text.isupper(),
                        "page": page_num,
                        "y": line_bbox[1],
                        "bbox": line_bbox,
                        "span_count_on_line": len(line_spans),
                        "avg_span_width": (line_bbox[2] - line_bbox[0]) / len(line_spans) if line_spans else 0,
                        "top": block["bbox"][1],
                        "x": line_bbox[0],
                    })

    merged_spans = []
    prev = None
    for span in sorted(raw_spans, key=lambda s: (s["page"], s["y"])):
        if prev and \
            prev["page"] == span["page"] and \
            abs(prev["x"] - span["x"]) < 20 and \
            abs(prev["y"] - span["y"]) < 25 and \
            prev["size"] == span["size"] and \
            prev["font"] == span["font"]:

            prev_ends_with = prev["text"].strip()[-1] if prev["text"].strip() else ""
            if prev_ends_with not in [".", ":", ";", "!", "?", "-"]:
                prev["text"] += " " + span["text"]
                prev["bbox"][2] = max(prev["bbox"][2], span["bbox"][2])
                prev["bbox"][3] = max(prev["bbox"][3], span["bbox"][3])
                continue

        if prev:
            merged_spans.append(prev)
        prev = span

    if prev:
        merged_spans.append(prev)

    raw_spans = merged_spans
    return raw_spans, sorted(set(font_sizes), reverse=True), font_size_word_map

def smart_merge_lines(spans, debug=False):
  if not spans:
    return []

  spans = sorted(spans, key=lambda s: (s["page"], s["y"], s["x"]))
  merged = []
  prev = spans[0]

  for curr in spans[1:]:
    same_page = curr["page"] == prev["page"]
    same_font = curr["font"] == prev["font"]
    same_size = curr["size"] == prev["size"]
    same_bold = curr.get("bold") == prev.get("bold")
    same_italic = curr.get("italic") == prev.get("italic")
    font_match = same_font and same_size and same_bold and same_italic

    x_close = abs(curr["x"] - prev["x"]) <= 3
    y_close = abs(curr["y"] - prev["y"]) <= (1.5 * curr["size"])

    prev_words = prev["text"].strip().split()
    last_word_font_match = False
    if prev_words:
      last_word_font_match = font_match

    should_merge = (
      same_page and font_match and (x_close or y_close or last_word_font_match)
    )

    if should_merge:
      prev["text"] = prev["text"].rstrip() + " " + curr["text"].lstrip()
      prev["bbox"][2] = max(prev["bbox"][2], curr["bbox"][2])
      prev["bbox"][3] = max(prev["bbox"][3], curr["bbox"][3])
      prev["y"] = min(prev["y"], curr["y"])
    else:
      # Debugging Step
    #   if debug and curr["page"] == 3:
    #     print("Merge skipped on page 3:")
    #     print(f"  Prev: {prev['text']}")
    #     print(f"  Curr: {curr['text']}")
    #     print(f"  x_close = {x_close}, y_close = {y_close}")
    #     print(f"  font_match = {font_match}")
      merged.append(prev)
      prev = curr

  merged.append(prev)
  return merged
