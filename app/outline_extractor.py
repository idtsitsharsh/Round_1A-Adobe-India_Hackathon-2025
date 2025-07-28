import fitz
import sys
import os
import re
from collections import Counter
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
from features import (
    normalize_span,
    is_heading_candidate,
    determine_heading_level_v2,
    cluster_font_sizes,
)
from title_extractor import extract_title
from pdf_parser import (
    extract_spans,
    smart_merge_lines,
)  

def extract_outline(pdf_path, filename, include_content=False):

    spans_info, sorted_font_sizes, font_size_word_map = extract_spans(pdf_path)

    font_info = cluster_font_sizes(sorted_font_sizes, font_size_word_map)
    body_font = font_info["body_font"]

    spans_info = [normalize_span(span) for span in spans_info]
    spans_info = smart_merge_lines(spans_info, debug=True)
    
    # Parsed files for Debugging
    # debug_filename = f"parsed_spans_debug_{os.path.splitext(filename)[0]}.txt"
    # with open(debug_filename, "w", encoding="utf-8") as f:
    #     f.write(f"--- FONT CLUSTER SUMMARY ---\n")
    #     f.write(f"Body Font Size (Threshold): {body_font:.1f}\n\n")
    #     f.write(">> Font Size Frequencies:\n")
    #     for size, count in sorted(font_info["font_counts"].items()):
    #         word_count = font_size_word_map.get(size, 0)
    #         f.write(f"  Size: {size:.1f} | Count: {count} | Words: {word_count}\n")
    #     f.write("\n--- PARSED SPANS ---\n\n")
    #     for span in spans_info:
    #         f.write(
    #             f"[Page {span['page']}] Size: {span['size']:.1f} | Bold: {span['bold']} | Italic: {span['italic']} | "
    #             f"Font: {span['font'].lower()} | X: {span['x']:.1f} | Y: {span['y']:.1f} | Text: {span['text'].strip()}\n"
    #         )

    title_text = extract_title(fitz.open(pdf_path), filename)

    headings = []
    seen_lines = set()
    heading_spans = []

    for i, span in enumerate(spans_info):
        text = span["text"]
        if not text or text in seen_lines:
            continue
        if span["page"] == 0 and text in title_text:
            continue

        level = determine_heading_level_v2(span, body_font)
        if level not in ["H1", "H2", "H3"]:
            continue
        if re.fullmatch(r"\d+(\.\d+)*", text.strip()):
            continue 

        headings.append({
            "level": level,
            "text": text,
            "page": span["page"] + 1
        })
        heading_spans.append((i, level))
        seen_lines.add(text)

    if not include_content:
        return {
            "title": title_text,
            "outline": headings
        }

    enriched_headings = []
    for idx, (heading_idx, level) in enumerate(heading_spans):
        start = heading_idx + 1
        end = heading_spans[idx + 1][0] if idx + 1 < len(heading_spans) else len(spans_info)

        content_lines = []
        for j in range(start, end):
            line = spans_info[j]["text"].strip()
            if line and line not in seen_lines:
                content_lines.append(line)

        enriched_headings.append({
            "level": level,
            "text": spans_info[heading_idx]["text"],
            "page": spans_info[heading_idx]["page"] + 1,
            "content": "\n".join(content_lines)
        })

    return {
        "title": title_text,
        "outline": enriched_headings,
        "spans": spans_info
    }
